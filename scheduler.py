import time
import schedule
from github_trending import GitHubTrending
import datetime

def job():
    """定时执行的抓取任务"""
    print(f"\n开始执行抓取任务 - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    github_trending = GitHubTrending()
    results = github_trending.run()
    print(f"抓取任务完成 - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return results

def schedule_jobs():
    """设置定时任务"""
    # 每天早上8点抓取日榜
    schedule.every().day.at("08:00").do(job)
    # 每周一早上9点抓取周榜
    schedule.every().monday.at("09:00").do(job)
    
    print("已设置定时任务:")
    print("- 每天 08:00 抓取GitHub趋势项目")
    print("- 每周一 09:00 抓取GitHub趋势项目")
    
    # 立即执行一次
    print("立即执行一次抓取任务...")
    job()
    
    # 持续运行定时任务
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次是否有待执行的任务
    except KeyboardInterrupt:
        print("\n定时任务已停止")

if __name__ == "__main__":
    schedule_jobs()