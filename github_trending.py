import requests
import json
import os
import time
import datetime
from concurrent.futures import ThreadPoolExecutor
from db import SessionLocal
from models import TrendingProject, ExecutionRecord
from sqlalchemy.exc import IntegrityError

class GitHubTrending:
    def __init__(self, save_dir='data'):
        self.base_url = "https://api.github.com/search/repositories"
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        # 添加您的 GitHub Token
        self.headers["Authorization"] = "YOUR_PERSONAL_ACCESS_TOKEN"
        
        self.save_dir = save_dir
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)


    def get_trending(self, period='daily'):
        """获取GitHub趋势项目
        
        Args:
            period: 'daily' 或 'weekly'
            
        Returns:
            趋势项目列表
        """
        # 计算时间范围
        now = datetime.datetime.now()
        if period == 'daily':
            date_from = now - datetime.timedelta(days=1)
        elif period == 'weekly':
            date_from = now - datetime.timedelta(weeks=1)
        else:
            raise ValueError("period must be 'daily' or 'weekly'")
        
        # 格式化日期为GitHub API查询格式
        date_query = date_from.strftime("%Y-%m-%d")
        
        # 构建查询参数
        query = f"created:>{date_query} sort:stars"
        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": 100  # 最大值为100
        }
        
        try:
            print(f"正在请求GitHub API: {self.base_url}?q={query}")
            response = requests.get(self.base_url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            items = data.get('items', [])
            print(f"获取到 {len(items)} 个项目")
            
            # 计算每个项目的今日星标数
            # 注意：GitHub API不直接提供today_stars，我们需要通过额外请求或估算
            # 这里我们使用一个简单的估算方法：对于新项目，假设所有星标都是今天的
            for item in items:
                # 对于日榜，假设所有星标都是当天的；对于周榜，假设是过去一周的平均值
                if period == 'daily':
                    item['today_stars'] = item.get('stargazers_count', 0)
                else:
                    # 周榜简单估算：总星标数除以7
                    item['today_stars'] = max(1, item.get('stargazers_count', 0) // 7)
            
            return items
        except requests.exceptions.RequestException as e:
            print(f"请求错误: {e}")
            return []
    
    def save_trending_data(self, trending_data, period, execution_record_id=None):
        """保存趋势数据到JSON文件并写入数据库"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.save_dir}/{period}_trending_{timestamp}.json"
        
        # 提取需要的项目信息
        processed_projects = []
        for raw_item in trending_data: # 修改这里，使用正确的变量名 trending_data
            # 确保使用一致的字段名：在JSON中使用todayStars，与前端保持一致
            project_data = {
                "name": raw_item.get("full_name"),
                "url": raw_item.get("html_url"),
                "description": raw_item.get("description"),
                "language": raw_item.get("language"),
                "stars": raw_item.get("stargazers_count"),
                "forks": raw_item.get("forks_count"),
                "todayStars": raw_item.get("today_stars", 0), # 使用我们在get_trending中计算的today_stars值

                "updated_at": raw_item.get("updated_at")
            }
            processed_projects.append(project_data)
            
            # 调试输出
            print(f"处理项目: {project_data['name']}, 语言: {project_data['language']}, 星标: {project_data['stars']}, 今日星标: {project_data['todayStars']}")
            
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(processed_projects, f, ensure_ascii=False, indent=2)
        print(f"已保存{len(processed_projects)}个{period}趋势项目到 {filename}")

        # 写入数据库
        session = SessionLocal()
        items_added_to_session = 0
        current_date_for_run = datetime.datetime.now().date() # Use a consistent date for this run

        for project_data_item in processed_projects: # Iterate over the list of processed project dicts
            try:
                updated_at_str = project_data_item.get("updated_at")
                parsed_updated_at = None
                if updated_at_str:
                    if not isinstance(updated_at_str, str):
                        print(f"警告: 项目 '{project_data_item.get('name')}' 的 updated_at 字段不是字符串: {updated_at_str}. 将其设置为 None.")
                    else:
                        try:
                            parsed_updated_at = datetime.datetime.strptime(updated_at_str, "%Y-%m-%dT%H:%M:%SZ")
                        except ValueError as ve:
                            print(f"警告: 项目 '{project_data_item.get('name')}' 的 updated_at ('{updated_at_str}') 解析失败: {ve}. 将其设置为 None.")
                
                # 确保使用正确的字段名称获取今日星标数
                today_stars_value = project_data_item.get("todayStars", 0)
                
                # 获取当前时间并验证年份是否合理（避免系统时间设置错误）
                current_time = datetime.datetime.now()
                # 移除硬编码年份的逻辑，直接使用当前系统时间
                
                db_project = TrendingProject(
                    name=project_data_item.get("name", ""),
                    url=project_data_item.get("url", ""),
                    description=project_data_item.get("description", ""),
                    language=project_data_item.get("language", ""),
                    stars=project_data_item.get("stars", 0),
                    forks=project_data_item.get("forks", 0),
                    today_stars=today_stars_value,  # 数据库字段名为today_stars
                    period=period,
                    date=current_date_for_run, 
                    updated_at=parsed_updated_at,
                    captured_at=current_time,  # 使用验证后的时间
                    execution_record_id=execution_record_id  # 设置执行记录ID
                )
                session.add(db_project)
                items_added_to_session += 1
            except Exception as e:
                print(f"错误: 项目 '{project_data_item.get('name')}' 添加到数据库会话失败: {e}")
        
        if items_added_to_session > 0:
            try:
                session.commit()
                print(f"成功: {items_added_to_session} 个项目的数据已提交到数据库。")
            except IntegrityError as e:
                session.rollback()
                print(f"数据库写入失败 (IntegrityError): {e}. 请检查数据是否重复或违反约束。")
            except Exception as e: 
                session.rollback()
                print(f"数据库提交时发生未知错误: {e}")
        elif processed_projects:
             print("警告: 本次运行没有项目成功添加到数据库会话。不执行提交操作。请检查上述错误/警告。")
            
        session.close()
        return filename
    
    def analyze_trending(self, data):
        """分析趋势数据，统计语言分布等信息"""
        languages = {}
        total_stars = 0
        total_forks = 0
        
        for item in data:
            lang = item.get("language") or "Unknown"
            if lang in languages:
                languages[lang] += 1
            else:
                languages[lang] = 1
            
            # 修改这里，使用 stargazers_count 字段
            total_stars += item.get("stargazers_count", 0)
            total_forks += item.get("forks_count", 0)
        
        # 按数量排序语言
        sorted_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)
        
        analysis = {
            "total_projects": len(data),
            "total_stars": total_stars,
            "total_forks": total_forks,
            "language_distribution": dict(sorted_languages),
            "top_languages": dict(sorted_languages[:5]) if len(sorted_languages) > 5 else dict(sorted_languages)
        }
        
        return analysis
    
    def run(self, periods=['daily', 'weekly']):
        """运行趋势抓取"""
        results = {}
        
        for period in periods:
            print(f"正在获取{period}趋势项目...")
            # 记录开始时间
            start_time = datetime.datetime.now()
            
            # 创建执行记录
            session = SessionLocal()
            execution_record = ExecutionRecord(
                type=period,
                start_time=start_time,
                status='running'
            )
            session.add(execution_record)
            session.commit()
            execution_id = execution_record.id
            session.close()
            
            trending_data = self.get_trending(period)            
            if trending_data:
                # 保存数据，传递执行记录ID
                saved_file = self.save_trending_data(trending_data, period, execution_id)
                
                # 分析数据
                analysis = self.analyze_trending(trending_data)
                
                results[period] = {
                    "data_file": saved_file,
                    "analysis": analysis,
                    "top_projects": trending_data[:50]  # 前50个项目
                }
                
                print(f"{period}趋势项目分析:")
                print(f"  总项目数: {analysis['total_projects']}")
                print(f"  总星标数: {analysis['total_stars']}")
                print(f"  热门语言: {', '.join(list(analysis['top_languages'].keys()))}")
                
                # 更新执行记录
                end_time = datetime.datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                session = SessionLocal()
                execution_record = session.query(ExecutionRecord).get(execution_id)
                if execution_record:
                    execution_record.end_time = end_time
                    execution_record.status = 'completed'
                    execution_record.project_count = analysis['total_projects']
                    execution_record.stars_count = analysis['total_stars']
                    execution_record.updates_count = analysis['total_projects']  # 假设所有项目都是更新的
                    execution_record.duration = duration
                    session.commit()
                session.close()
            else:
                print(f"未能获取{period}趋势项目数据")
                
                # 更新执行记录为失败状态
                session = SessionLocal()
                execution_record = session.query(ExecutionRecord).get(execution_id)
                if execution_record:
                    execution_record.end_time = datetime.datetime.now()
                    execution_record.status = 'failed'
                    session.commit()
                session.close()
        
        return results

# 示例用法
if __name__ == "__main__":
    # 创建GitHub趋势抓取器
    github_trending = GitHubTrending()
    
    # 运行抓取
    results = github_trending.run()
    
    # 打印前5个日榜项目
    if 'daily' in results and results['daily']['top_projects']:
        print("\n日榜前5个项目:")
        for i, project in enumerate(results['daily']['top_projects'][:5], 1):
            print(f"{i}. {project['full_name']} - ⭐ {project['stargazers_count']}")
            print(f"   {project['description']}")
            print(f"   {project['html_url']}")
        print(f"\n共获取了{len(results['daily']['top_projects'])}个日榜热门项目")
    
    # 打印前5个周榜项目
    if 'weekly' in results and results['weekly']['top_projects']:
        print("\n周榜前5个项目:")
        for i, project in enumerate(results['weekly']['top_projects'][:5], 1):
            print(f"{i}. {project['full_name']} - ⭐ {project['stargazers_count']}")
            print(f"   {project['description']}")
            print(f"   {project['html_url']}")
        print(f"\n共获取了{len(results['weekly']['top_projects'])}个周榜热门项目")