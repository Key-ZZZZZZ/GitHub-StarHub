import argparse
import os
from github_trending import GitHubTrending
from visualizer import TrendingVisualizer
from db import create_db_tables
import schedule
import time
from datetime import datetime

def run_once(periods=['daily', 'weekly'], visualize=True):
    """运行一次抓取和可视化"""
    print(f"\n开始执行GitHub趋势项目抓取 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 抓取趋势数据
    github_trending = GitHubTrending()
    results = github_trending.run(periods)
    
    # 生成可视化报告
    if visualize and results:
        print("\n开始生成可视化报告...")
        visualizer = TrendingVisualizer()
        
        for period in periods:
            if period in results:
                report = visualizer.generate_report(period)
                if report:
                    print(f"已生成{period}趋势报告，包含{report['project_count']}个项目")
    
    print(f"任务完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return results

def run_scheduler(daily_time="08:00", weekly_time="09:00"):
    """运行定时任务调度器"""
    # 每天抓取日榜
    schedule.every().day.at(daily_time).do(run_once, periods=["daily"])
    # 每周一抓取周榜
    schedule.every().monday.at(weekly_time).do(run_once, periods=["weekly"])
    
    print("已设置定时任务:")
    print(f"- 每天 {daily_time} 抓取GitHub日榜趋势项目")
    print(f"- 每周一 {weekly_time} 抓取GitHub周榜趋势项目")
    
    # 立即执行一次
    print("立即执行一次抓取任务...")
    run_once()
    
    # 持续运行定时任务
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次是否有待执行的任务
    except KeyboardInterrupt:
        print("\n定时任务已停止")

def main():
    """主函数，处理命令行参数"""
    parser = argparse.ArgumentParser(description="GitHub趋势项目抓取工具")
    parser.add_argument("-m", "--mode", choices=["once", "schedule"], default="once",
                        help="运行模式: once(运行一次) 或 schedule(定时运行)")
    parser.add_argument("-p", "--period", choices=["daily", "weekly", "both"], default="both",
                        help="抓取周期: daily(日榜), weekly(周榜) 或 both(两者)")
    parser.add_argument("-v", "--visualize", action="store_true", default=True,
                        help="是否生成可视化报告")
    parser.add_argument("--daily-time", default="08:00", help="每日抓取时间 (格式: HH:MM)")
    parser.add_argument("--weekly-time", default="09:00", help="每周抓取时间 (格式: HH:MM)")
    
    args = parser.parse_args()
    
    # 确定抓取周期
    if args.period == "both":
        periods = ["daily", "weekly"]
    else:
        periods = [args.period]
    
    # 根据模式运行
    if args.mode == "once":
        run_once(periods, args.visualize)
    else:  # schedule模式
        run_scheduler(args.daily_time, args.weekly_time)

if __name__ == "__main__":
    # 确保数据目录存在
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(os.path.join("data", "visualizations")):
        os.makedirs(os.path.join("data", "visualizations"))
    
    create_db_tables()
    main()