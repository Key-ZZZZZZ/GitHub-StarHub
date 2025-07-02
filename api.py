from flask import Flask, jsonify, request
from main import run_once  # 导入 run_once 函数
from db import SessionLocal
from models import TrendingProject, ExecutionRecord
from flask_cors import CORS
import os
import sys
import threading
import time
from datetime import datetime, timedelta
from models import SchedulerSetting
from db import engine
from sqlalchemy import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from flask import Flask, request, jsonify
current_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@app.route('/api/scheduler/settings', methods=['GET'])
def get_scheduler_settings():
    session = SessionLocal()
    setting = session.query(SchedulerSetting).first()
    if setting:
        result = {
            'daily_time': setting.daily_time,
            'weekly_time': setting.weekly_time
        }
    else:
        result = {
            'daily_time': '08:00',
            'weekly_time': '09:00'
        }
    session.close()
    return jsonify(result)

@app.route('/api/scheduler/settings', methods=['POST'])
def update_scheduler_settings():
    data = request.json
    daily_time = data.get('daily_time', '08:00')
    weekly_time = data.get('weekly_time', '09:00')
    print(f"收到设置 daily_time={daily_time}, weekly_time={weekly_time}")
    session = SessionLocal()
    setting = session.query(SchedulerSetting).first()
    if not setting:
        setting = SchedulerSetting(daily_time=daily_time, weekly_time=weekly_time)
        session.add(setting)
        print("数据库无原有设置，已新建记录")
    else:
        print(f"数据库原有设置: daily_time={setting.daily_time}, weekly_time={setting.weekly_time}")
        setting.daily_time = daily_time
        setting.weekly_time = weekly_time
        print("已更新数据库记录")
    session.commit()
    print("数据库已提交更改")
    session.close()
    return jsonify({'success': True})
CORS(app)  # 允许跨域请求，方便前端调试

# 获取执行记录历史
@app.route('/api/execution-history', methods=['GET'])
def get_execution_history():
    session = SessionLocal()
    try:
        # 从数据库中获取执行记录
        records = session.query(ExecutionRecord).order_by(ExecutionRecord.start_time.desc()).all()
        history = []
        
        for record in records:
            # 计算执行时长
            duration_str = ''
            if record.duration:
                duration_str = f"{record.duration:.1f}s"
            
            # 格式化时间
            start_time_str = record.start_time.strftime("%Y-%m-%d %H:%M:%S") if record.start_time else ''
            end_time_str = record.end_time.strftime("%Y-%m-%d %H:%M:%S") if record.end_time else ''
            
            history.append({
                'id': record.id,
                'type': record.type,
                'execution_time': start_time_str,
                'finishTime': end_time_str,
                'count': record.project_count,
                'stars': record.stars_count,
                'updates': record.updates_count,
                'duration': duration_str,
                'status': record.status
            })
        
        return jsonify(history)
    except Exception as e:
        print(f"获取执行记录失败: {e}")
        return jsonify([]), 500
    finally:
        session.close()

# 示例：手动触发每日任务
@app.route('/api/run-daily', methods=['POST'])
def trigger_daily_run():
    try:
        results = run_once(periods=['daily'], visualize=False) # API通常不直接生成可视化文件
        return jsonify({'status': 'success', 'message': '每日任务已触发', 'results': results})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# 示例：手动触发每周任务
@app.route('/api/run-weekly', methods=['POST'])
def trigger_weekly_run():
    try:
        results = run_once(periods=['weekly'], visualize=False)
        return jsonify({'status': 'success', 'message': '每周任务已触发', 'results': results})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# 全局变量，用于跟踪调度器状态
scheduler_thread = None
scheduler_status = {
    'daily_task': {'status': 'idle', 'next_run': ''},
    'weekly_task': {'status': 'idle', 'next_run': ''}
}

# 获取调度器状态
@app.route('/api/scheduler-status', methods=['GET'])
def get_scheduler_status():
    return jsonify(scheduler_status)

@app.route('/api/trending/dates', methods=['GET'])
def get_trending_dates():
    """获取所有可用的趋势数据日期"""
    project_type = request.args.get('type', 'daily')
    session = SessionLocal()
    try:
        # 查询指定类型的所有不重复日期
        dates = session.query(TrendingProject.date)\
            .filter(TrendingProject.period == project_type)\
            .distinct()\
            .order_by(TrendingProject.date.desc())\
            .all()
        
        return jsonify([date[0].strftime("%Y-%m-%d") for date in dates])
    finally:
        session.close()

@app.route('/api/trending/languages', methods=['GET'])
def get_trending_languages():
    """获取所有可用的编程语言"""
    project_type = request.args.get('type', 'daily')
    date_str = request.args.get('date')
    
    session = SessionLocal()
    try:
        query = session.query(TrendingProject.language)\
            .filter(TrendingProject.period == project_type)\
            .filter(TrendingProject.language.isnot(None))
        
        if date_str:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            query = query.filter(TrendingProject.date == date_obj)
        
        languages = query.distinct().all()
        return jsonify([lang[0] for lang in languages if lang[0]])
    finally:
        session.close()

# 修改现有的trending接口，添加分页支持
@app.route('/api/analysis-data', methods=['GET'])
def get_analysis_data():
    project_type = request.args.get('type', 'daily')
    date_str = request.args.get('date')

    session = SessionLocal()
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        projects = session.query(TrendingProject).filter(
            TrendingProject.period == project_type,
            TrendingProject.date == date_obj
        ).all()

        # 编程语言分布
        language_counts = {}
        for project in projects:
            if project.language:
                language_counts[project.language] = language_counts.get(project.language, 0) + 1
        language_distribution = [{'name': lang, 'value': count} for lang, count in language_counts.items()]
        # 星标数量分布
        # 动态星标数量分布
        stars_distribution_raw = [project.stars for project in projects if project.stars is not None]
        max_stars = max(stars_distribution_raw) if stars_distribution_raw else 0

        stars_ranges = []
        if max_stars <= 100:
            # 细分 0-100 区间
            stars_ranges = [
                (0, 20, '0-20'),
                (21, 40, '21-40'),
                (41, 60, '41-60'),
                (61, 80, '61-80'),
                (81, 100, '81-100')
            ]
        elif max_stars <= 500:
            stars_ranges = [(0, 100, '0-100'), (101, 500, '101-500')]
        elif max_stars <= 1000:
            stars_ranges = [(0, 100, '0-100'), (101, 500, '101-500'), (501, 1000, '501-1000')]
        elif max_stars <= 5000:
            stars_ranges = [(0, 100, '0-100'), (101, 500, '101-500'), (501, 1000, '501-1000'), (1001, 5000, '1001-5000')]
        else:
            stars_ranges = [(0, 100, '0-100'), (101, 500, '101-500'), (501, 1000, '501-1000'), (1001, 5000, '1001-5000'), (5001, float('inf'), '5001+')]

        stars_distribution_counts = {r[2]: 0 for r in stars_ranges}

        for project in projects:
            if project.stars is not None:
                for lower, upper, name in stars_ranges:
                    if lower <= project.stars <= upper:
                        stars_distribution_counts[name] += 1
                        break

        stars_distribution = [{'name': name, 'value': count} for name, count in stars_distribution_counts.items() if count > 0]
        # 按照星标范围的顺序进行排序，确保图表显示顺序正确
        stars_distribution.sort(key=lambda x: [r[2] for r in stars_ranges].index(x['name']))

        # 项目创建时间分布
        time_counts = {}
        for project in projects:
            if project.updated_at:
                # 对于每日榜，按天统计；对于每周榜，按周统计
                if project_type == 'daily':
                    # 假设 updated_at 是 datetime 对象，我们只取日期部分
                    date_key = project.updated_at.strftime("%Y-%m-%d")
                elif project_type == 'weekly':
                    # 对于每周榜，可以考虑按周一的日期作为周的标识
                    # 或者简单地按月份统计，如果数据量不大，按月可能更合适
                    # 这里我们先按月份统计，如果需要更细致的周统计，需要更复杂的逻辑
                    date_key = project.updated_at.strftime("%Y-%W") # %W 表示一年中的第几周，周一作为一周的第一天
                else:
                    date_key = "Unknown"
                time_counts[date_key] = time_counts.get(date_key, 0) + 1

        # 将时间分布数据转换为前端ECharts可用的格式
        # 按照日期/周进行排序
        time_distribution = sorted([{'name': time_key, 'value': count} for time_key, count in time_counts.items()], key=lambda x: x['name'])

        return jsonify({
            'language_distribution': language_distribution,
            'stars_distribution': stars_distribution,
            'time_distribution': time_distribution
        })

    except Exception as e:
        print(f"Error in get_analysis_data: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        session.close()

@app.route('/api/analysis-projects', methods=['GET'])
def get_analysis_projects():
    project_type = request.args.get('type', 'daily')
    date_str = request.args.get('date')
    language = request.args.get('language')
    stars_min = request.args.get('stars_min', type=int)
    stars_max = request.args.get('stars_max', type=int)
    captured_at_start = request.args.get('captured_at_start')
    captured_at_end = request.args.get('captured_at_end')

    session = SessionLocal()
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        query = session.query(TrendingProject).filter(
            TrendingProject.period == project_type,
            TrendingProject.date == date_obj
        )

        if language:
            query = query.filter(TrendingProject.language == language)
        if stars_min is not None:
            query = query.filter(TrendingProject.stars >= stars_min)
        if stars_max is not None:
            query = query = query.filter(TrendingProject.stars <= stars_max)
        if captured_at_start:
            captured_at_start_obj = datetime.strptime(captured_at_start, "%Y-%m-%d %H:%M:%S")
            query = query.filter(TrendingProject.captured_at >= captured_at_start_obj)
        if captured_at_end:
            captured_at_end_obj = datetime.strptime(captured_at_end, "%Y-%m-%d %H:%M:%S")
            query = query.filter(TrendingProject.captured_at <= captured_at_end_obj)

        projects = query.order_by(TrendingProject.stars.desc()).all()

        project_list = []
        for project in projects:
            project_list.append({
                "id": project.id,
                "name": project.name,
                "url": project.url,
                "description": project.description,
                "language": project.language,
                "stars": project.stars,
                "forks": project.forks,
                "todayStars": project.today_stars,
                "period": project.period,
                "date": project.date.strftime("%Y-%m-%d"),
                "updatedAt": project.updated_at.strftime("%Y-%m-%d %H:%M:%S") if project.updated_at else None,
                "capturedAt": project.captured_at.strftime("%Y-%m-%d %H:%M:%S") if project.captured_at else None
            })
        return jsonify(project_list)
    except Exception as e:
        print(f"获取分析项目失败: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route('/api/execution-analysis-data', methods=['GET'])
def get_execution_analysis_data():
    analysis_type = request.args.get('type', 'daily') # 'daily' or 'weekly'
    
    session = SessionLocal()
    try:
        if analysis_type == 'daily':
            # Group by day
            results = session.query(
                func.strftime('%Y-%m-%d', ExecutionRecord.start_time).label('date'),
                func.sum(ExecutionRecord.project_count).label('total_projects')
            ).group_by('date').order_by('date').all()
            
            time_distribution = [{'name': row.date, 'value': row.total_projects} for row in results]
            
        elif analysis_type == 'weekly':
            # Group by week (using %Y-%W for year and week number)
            results = session.query(
                func.strftime('%Y-%W', ExecutionRecord.start_time).label('week'),
                func.sum(ExecutionRecord.project_count).label('total_projects')
            ).group_by('week').order_by('week').all()
            
            time_distribution = [{'name': row.week, 'value': row.total_projects} for row in results]
            
        else:
            return jsonify({'status': 'error', 'message': 'Invalid analysis type'}), 400

        return jsonify({
            'time_distribution': time_distribution
        })

    except Exception as e:
        print(f"Error in get_execution_analysis_data: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        session.close()



@app.route('/api/trending', methods=['GET'])
def get_trending_projects():
    """获取GitHub热门项目，支持分页、日期和语言筛选"""
    project_type = request.args.get('type', 'daily')
    date_str = request.args.get('date')
    language = request.args.get('language')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))  # 默认每页50条
    
    session = SessionLocal()
    try:
        query = session.query(TrendingProject).filter(TrendingProject.period == project_type)
        
        if date_str:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            query = query.filter(TrendingProject.date == date_obj)
        
        if language:
            query = query.filter(TrendingProject.language == language)
        
        # 获取总记录数
        total = query.count()
        
        # 添加排序和分页
        projects = query.order_by(TrendingProject.stars.desc())\
            .offset((page - 1) * per_page)\
            .limit(per_page)\
            .all()
        
        result = {
            "total": total,
            "page": page,
            "per_page": per_page,
            "data": [{
                "id": p.id,
                "name": p.name,
                "url": p.url,
                "description": p.description,
                "language": p.language,
                "stars": p.stars,
                "forks": p.forks,
                "todayStars": p.today_stars,
                "period": p.period,
                "date": p.date.strftime("%Y-%m-%d"),
                "updatedAt": p.updated_at.strftime("%Y-%m-%d %H:%M:%S") if p.updated_at else None,
                "capturedAt": p.captured_at.strftime("%Y-%m-%d %H:%M:%S") if p.captured_at else None
            } for p in projects]
        }
        
        return jsonify(result)
    finally:
        session.close()

# 启动计划任务的线程函数
def scheduler_thread_func():
    try:
        # 导入所需模块
        import schedule
        import requests
        
        # 初始化上次运行时间记录
        scheduler_thread_func.last_daily_run = datetime.now().replace(year=2000)  # 设置一个很久以前的时间
        scheduler_thread_func.last_weekly_run = datetime.now().replace(year=2000)
        
        # 每次启动线程时从数据库读取最新的调度时间
        session = SessionLocal()
        setting = session.query(SchedulerSetting).first()
        if setting:
            daily_time = setting.daily_time or '08:00'
            weekly_time = setting.weekly_time or '09:00'
            print(f"从数据库读取调度时间: 每日={daily_time}, 每周={weekly_time}")
        else:
            daily_time = '08:00'
            weekly_time = '09:00'
            print(f"使用默认调度时间: 每日={daily_time}, 每周={weekly_time}")
        session.close()
        
        # 更新调度器状态
        global scheduler_status
        scheduler_status['daily_task']['status'] = 'running'
        next_daily_run = datetime.now().replace(hour=int(daily_time.split(":")[0]), minute=int(daily_time.split(":")[1]), second=0)
        scheduler_status['daily_task']['next_run'] = next_daily_run.strftime('%Y-%m-%d %H:%M')
        
        scheduler_status['weekly_task']['status'] = 'running'
        next_weekly_run = datetime.now().replace(hour=int(weekly_time.split(":")[0]), minute=int(weekly_time.split(":")[1]), second=0)
        scheduler_status['weekly_task']['next_run'] = next_weekly_run.strftime('%Y-%m-%d %H:%M')
        
        print(f"下次每日任务执行时间: {scheduler_status['daily_task']['next_run']}")
        print(f"下次每周任务执行时间: {scheduler_status['weekly_task']['next_run']}")
        
        # 定义任务执行函数，确保在执行时记录日志并直接调用API接口
        def run_daily_task():
            print(f"\n[调度器] 触发每日任务执行 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            try:
                # 直接调用API接口执行每日任务
                import requests
                response = requests.post('http://localhost:5001/api/run-daily')
                print(f"[调度器] 每日任务API调用结果: {response.status_code} - {response.text}")
                
                # 更新下次执行时间 - 始终设置为明天的同一时间
                now = datetime.now()
                tomorrow = now + timedelta(days=1)
                next_daily_run = tomorrow.replace(
                    hour=int(daily_time.split(":")[0]), 
                    minute=int(daily_time.split(":")[1]), 
                    second=0, 
                    microsecond=0
                )
                scheduler_status['daily_task']['next_run'] = next_daily_run.strftime('%Y-%m-%d %H:%M')
                print(f"[调度器] 更新下次每日任务执行时间: {scheduler_status['daily_task']['next_run']}")
                
                return {"status": "success"}
            except Exception as e:
                print(f"[调度器] 每日任务执行失败: {str(e)}")
                return {"error": str(e)}
        
        def run_weekly_task():
            print(f"\n[调度器] 触发每周任务执行 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            try:
                # 直接调用API接口执行每周任务
                import requests
                response = requests.post('http://localhost:5001/api/run-weekly')
                print(f"[调度器] 每周任务API调用结果: {response.status_code} - {response.text}")
                
                # 更新下次执行时间 - 计算下一个周一的日期
                now = datetime.now()
                days_until_next_monday = 7 - now.weekday()
                if days_until_next_monday == 7:
                    days_until_next_monday = 7  # 如果今天是周一，则设置为下周一
                
                next_monday = now + timedelta(days=days_until_next_monday)
                next_weekly_run = next_monday.replace(
                    hour=int(weekly_time.split(":")[0]),
                    minute=int(weekly_time.split(":")[1]),
                    second=0,
                    microsecond=0
                )
                
                scheduler_status['weekly_task']['next_run'] = next_weekly_run.strftime('%Y-%m-%d %H:%M')
                print(f"[调度器] 更新下次每周任务执行时间: {scheduler_status['weekly_task']['next_run']}")
                
                return {"status": "success"}
            except Exception as e:
                print(f"[调度器] 每周任务执行失败: {str(e)}")
                return {"error": str(e)}
        
        # 设置定时任务
        schedule.clear()  # 清除之前的所有任务
        print(f"设置每日任务执行时间: {daily_time}")
        schedule.every().day.at(daily_time).do(run_daily_task)
        print(f"设置每周任务执行时间: {weekly_time}")
        schedule.every().monday.at(weekly_time).do(run_weekly_task)
        
        print("调度器已启动，等待执行计划任务...")
        
        # 持续运行调度器，检查是否有待执行的任务
        while True:
            try:
                # 获取当前时间
                now = datetime.now()
                current_time = now.strftime('%H:%M')
                current_day = now.weekday()  # 0是周一，6是周日
                
                # 检查是否有待执行的任务
                pending_jobs = schedule.get_jobs()
                job_times = [job.next_run.strftime('%Y-%m-%d %H:%M:%S') if hasattr(job, 'next_run') and job.next_run else 'Unknown' for job in pending_jobs]
                
                # 每5分钟输出一次详细日志
                if now.minute % 5 == 0 and now.second < 10:
                    print(f"\n[调度器状态] 当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"[调度器状态] 当前待执行任务数: {len(pending_jobs)}")
                    print(f"[调度器状态] 下次执行时间: {job_times if job_times else '无'}")
                    print(f"[调度器状态] 每日任务时间: {daily_time}, 每周任务时间: {weekly_time} (周一)")
                    # 输出上次执行时间
                    last_daily = getattr(scheduler_thread_func, 'last_daily_run', datetime.now().replace(year=2000)).strftime('%Y-%m-%d %H:%M:%S')
                    last_weekly = getattr(scheduler_thread_func, 'last_weekly_run', datetime.now().replace(year=2000)).strftime('%Y-%m-%d %H:%M:%S')
                    print(f"[调度器状态] 上次每日任务执行时间: {last_daily}")
                    print(f"[调度器状态] 上次每周任务执行时间: {last_weekly}")
                
                # 手动检查是否应该执行任务（作为schedule的备份机制）
                # 检查每日任务 - 使用时间范围检查，避免错过执行窗口
                daily_hour, daily_minute = map(int, daily_time.split(':'))
                target_daily_time = now.replace(hour=daily_hour, minute=daily_minute, second=0, microsecond=0)
                time_diff = abs((now - target_daily_time).total_seconds())
                
                # 如果当前时间在目标时间的前后30秒内，且今天还没执行过
                if time_diff <= 30:
                    last_run_date = getattr(scheduler_thread_func, 'last_daily_run', datetime.now().replace(year=2000)).date()
                    if last_run_date < now.date():
                        print(f"\n[调度器] 当前时间 {now.strftime('%H:%M:%S')} 接近每日任务时间 {daily_time}，触发执行")
                        run_daily_task()
                        scheduler_thread_func.last_daily_run = now
                        print(f"[调度器] 每日任务已执行，更新上次执行时间为: {now.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # 检查每周任务 - 确保是周一且在指定时间附近
                if current_day == 0:  # 周一
                    weekly_hour, weekly_minute = map(int, weekly_time.split(':'))
                    target_weekly_time = now.replace(hour=weekly_hour, minute=weekly_minute, second=0, microsecond=0)
                    time_diff = abs((now - target_weekly_time).total_seconds())
                    
                    # 如果当前时间在目标时间的前后30秒内，且本周一还没执行过
                    if time_diff <= 30:
                        last_run = getattr(scheduler_thread_func, 'last_weekly_run', datetime.now().replace(year=2000))
                        # 确保上次运行不是今天或者本周一
                        if last_run.date() < now.date() or last_run.weekday() != 0:
                            print(f"\n[调度器] 当前时间 {now.strftime('%H:%M:%S')} 在周一且接近每周任务时间 {weekly_time}，触发执行")
                            run_weekly_task()
                            scheduler_thread_func.last_weekly_run = now
                            print(f"[调度器] 每周任务已执行，更新上次执行时间为: {now.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # 运行schedule的待执行任务
                schedule.run_pending()
            except Exception as e:
                print(f"[调度器] 主循环异常: {str(e)}")
                import traceback
                print(traceback.format_exc())
            
            # 每分钟检查一次
            time.sleep(60)
    except Exception as e:
        print(f"调度器线程异常: {str(e)}")
        import traceback
        print(traceback.format_exc())

# 启动计划任务
@app.route('/api/start-scheduler', methods=['POST'])
def start_scheduler_api():
    global scheduler_thread, scheduler_status
    
    # 检查调度器线程是否已经在运行
    if scheduler_thread and scheduler_thread.is_alive():
        return jsonify({'status': 'info', 'message': '计划任务已在运行中'})
    
    try:
        # 创建并启动调度器线程
        scheduler_thread = threading.Thread(target=scheduler_thread_func, daemon=True)
        scheduler_thread.start()
        
        # 启动后立即返回最新调度器状态
        return jsonify(scheduler_status)
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'启动计划任务失败: {str(e)}'}), 500

# 停止计划任务
@app.route('/api/stop-scheduler', methods=['POST'])
def stop_scheduler_api():
    global scheduler_status, scheduler_thread
    try:
        # 更新调度器状态
        scheduler_status['daily_task']['status'] = 'idle'
        scheduler_status['daily_task']['next_run'] = ''
        scheduler_status['weekly_task']['status'] = 'idle'
        scheduler_status['weekly_task']['next_run'] = ''
        # 彻底终止调度器线程
        if scheduler_thread and scheduler_thread.is_alive():
            import ctypes
            tid = scheduler_thread.ident
            res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), ctypes.py_object(SystemExit))
            if res == 0:
                print('无法终止调度器线程')
            scheduler_thread = None
        # 停止后立即返回最新调度器状态
        return jsonify(scheduler_status)
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'停止计划任务失败: {str(e)}'}), 500

@app.route('/api/execution-detail/<int:record_id>', methods=['GET'])
def get_execution_detail(record_id):
    session = SessionLocal()
    try:
        record = session.query(ExecutionRecord).get(record_id)
        if not record:
            return jsonify({"error": "执行记录不存在"}), 404
        
        # 直接通过 execution_record_id 查询相关项目
        projects = session.query(TrendingProject).filter(
            TrendingProject.execution_record_id == record_id
        ).order_by(TrendingProject.stars.desc()).all()
        
        # 格式化项目数据
        project_list = []
        for project in projects:
            project_list.append({
                "id": project.id,
                "name": project.name,
                "url": project.url,
                "description": project.description,
                "language": project.language,
                "stars": project.stars,
                "forks": project.forks,
                "todayStars": project.today_stars,
                "period": project.period,
                "date": project.date.strftime("%Y-%m-%d"),
                "updatedAt": project.updated_at.strftime("%Y-%m-%d %H:%M:%S") if project.updated_at else None
            })
        
        # 构建响应数据
        result = {
            "record": {
                "id": record.id,
                "type": record.type,
                "start_time": record.start_time.strftime("%Y-%m-%d %H:%M:%S") if record.start_time else None,
                "end_time": record.end_time.strftime("%Y-%m-%d %H:%M:%S") if record.end_time else None,
                "status": record.status,
                "project_count": record.project_count,
                "stars_count": record.stars_count,
                "updates_count": record.updates_count,
                "duration": f"{record.duration:.1f}s" if record.duration else None
            },
            "projects": project_list
        }
        
        return jsonify(result)
    except Exception as e:
        print(f"获取执行记录详情失败: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


if __name__ == '__main__':
    # 确保数据目录存在，这部分逻辑可以从main.py移到此处或共享
    if not os.path.exists(os.path.join(current_dir, "data")):
        os.makedirs(os.path.join(current_dir, "data"))
    if not os.path.exists(os.path.join(current_dir, "data", "visualizations")):
        os.makedirs(os.path.join(current_dir, "data", "visualizations"))
    
    print("启动API服务器，关闭调试模式以避免自动重启影响调度器线程...")
    app.run(host="127.0.0.1", port=5001, debug=True)

