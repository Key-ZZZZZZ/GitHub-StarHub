import matplotlib.pyplot as plt
import json
import os
import pandas as pd
import numpy as np
from datetime import datetime

class TrendingVisualizer:
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        # 创建可视化结果保存目录
        self.viz_dir = os.path.join(data_dir, 'visualizations')
        if not os.path.exists(self.viz_dir):
            os.makedirs(self.viz_dir)
    
    def load_data(self, file_path):
        """加载JSON数据文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载数据文件失败: {e}")
            return []
    
    def get_latest_data_file(self, period='daily'):
        """获取最新的数据文件"""
        files = [f for f in os.listdir(self.data_dir) 
                if f.startswith(f"{period}_trending_") and f.endswith(".json")]
        
        if not files:
            return None
        
        # 按文件名排序（文件名包含时间戳）
        files.sort(reverse=True)
        return os.path.join(self.data_dir, files[0])
    
    def visualize_language_distribution(self, data, period='daily'):
        """可视化语言分布"""
        # 统计语言分布
        languages = {}
        for item in data:
            lang = item.get("language") or "Unknown"
            if lang in languages:
                languages[lang] += 1
            else:
                languages[lang] = 1
        
        # 按数量排序并获取前10种语言
        sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)
        top_langs = sorted_langs[:10] if len(sorted_langs) > 10 else sorted_langs
        
        # 创建饼图
        labels = [lang for lang, count in top_langs]
        sizes = [count for lang, count in top_langs]
        
        plt.figure(figsize=(10, 8))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
        plt.axis('equal')  # 使饼图为正圆形
        plt.title(f'GitHub {period.capitalize()} Trending - 语言分布 (前10名)')
        
        # 保存图表
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.viz_dir}/{period}_language_dist_{timestamp}.png"
        plt.savefig(filename)
        plt.close()
        
        print(f"语言分布图已保存到: {filename}")
        return filename
    
    def visualize_stars_distribution(self, data, period='daily'):
        """可视化星标分布"""
        # 提取项目名称和星标数
        projects = [item.get("name").split('/')[-1] for item in data[:15]]  # 取前15个项目
        stars = [item.get("stars") for item in data[:15]]
        
        # 创建条形图
        plt.figure(figsize=(12, 8))
        bars = plt.barh(projects, stars, color='skyblue')
        plt.xlabel('星标数')
        plt.ylabel('项目名称')
        plt.title(f'GitHub {period.capitalize()} Trending - 热门项目星标数 (前15名)')
        plt.tight_layout()
        
        # 在条形上显示具体数值
        for bar in bars:
            width = bar.get_width()
            plt.text(width + 0.1, bar.get_y() + bar.get_height()/2, f'{int(width):,}', 
                    ha='left', va='center')
        
        # 保存图表
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.viz_dir}/{period}_stars_dist_{timestamp}.png"
        plt.savefig(filename)
        plt.close()
        
        print(f"星标分布图已保存到: {filename}")
        return filename
    
    def visualize_creation_time(self, data, period='daily'):
        """可视化项目创建时间分布"""
        # 提取创建时间
        creation_dates = []
        for item in data:
            try:
                date_str = item.get("created_at")
                if date_str:
                    date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
                    creation_dates.append(date)
            except Exception:
                continue
        
        if not creation_dates:
            print("没有有效的创建时间数据")
            return None
        
        # 转换为pandas Series以便分析
        dates_series = pd.Series(creation_dates)
        
        # 按月份分组
        monthly_counts = dates_series.dt.to_period('M').value_counts().sort_index()
        
        # 创建时间序列图
        plt.figure(figsize=(12, 6))
        monthly_counts.plot(kind='line', marker='o')
        plt.title(f'GitHub {period.capitalize()} Trending - 项目创建时间分布')
        plt.xlabel('创建月份')
        plt.ylabel('项目数量')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # 保存图表
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.viz_dir}/{period}_creation_time_{timestamp}.png"
        plt.savefig(filename)
        plt.close()
        
        print(f"创建时间分布图已保存到: {filename}")
        return filename
    
    def generate_report(self, period='daily'):
        """生成可视化报告"""
        # 获取最新数据文件
        data_file = self.get_latest_data_file(period)
        if not data_file:
            print(f"未找到{period}趋势数据文件")
            return None
        
        print(f"正在为{data_file}生成可视化报告...")
        data = self.load_data(data_file)
        
        if not data:
            print("数据为空，无法生成报告")
            return None
        
        # 生成各种可视化
        lang_viz = self.visualize_language_distribution(data, period)
        stars_viz = self.visualize_stars_distribution(data, period)
        time_viz = self.visualize_creation_time(data, period)
        
        # 返回可视化结果
        return {
            "data_file": data_file,
            "visualizations": {
                "language_distribution": lang_viz,
                "stars_distribution": stars_viz,
                "creation_time_distribution": time_viz
            },
            "project_count": len(data),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

# 示例用法
if __name__ == "__main__":
    # 创建可视化器
    visualizer = TrendingVisualizer()
    
    # 生成日榜和周榜报告
    daily_report = visualizer.generate_report('daily')
    weekly_report = visualizer.generate_report('weekly')
    
    if daily_report:
        print(f"\n日榜报告生成完成，共包含{daily_report['project_count']}个项目")
    
    if weekly_report:
        print(f"\n周榜报告生成完成，共包含{weekly_report['project_count']}个项目")