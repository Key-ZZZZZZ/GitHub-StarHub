from sqlalchemy import Column, Integer, String, Date, DateTime, Text, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

# 定义TrendingProject模型
Base = declarative_base()

class TrendingProject(Base):
    __tablename__ = 'trending_projects'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    url = Column(String(512), nullable=False)
    description = Column(Text)
    language = Column(String(64))
    stars = Column(Integer)
    forks = Column(Integer)
    today_stars = Column(Integer)
    period = Column(String(16), nullable=False)  # 'daily' or 'weekly'
    date = Column(Date, nullable=False)
    updated_at = Column(DateTime)
    captured_at = Column(DateTime)  # 记录项目抓取时间
    execution_record_id = Column(Integer, ForeignKey('execution_records.id'))  # 新增字段，关联到执行记录

class SchedulerSetting(Base):
    __tablename__ = 'scheduler_settings'
    id = Column(Integer, primary_key=True, autoincrement=True)
    daily_time = Column(String(8), nullable=False, default='08:00')  # 格式: HH:MM
    weekly_time = Column(String(8), nullable=False, default='09:00')  # 格式: HH:MM

class ExecutionRecord(Base):
    __tablename__ = 'execution_records'
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(16), nullable=False)  # 'daily' or 'weekly'
    start_time = Column(DateTime, nullable=False)  # 开始执行时间
    end_time = Column(DateTime)  # 结束执行时间
    status = Column(String(16), default='running')  # 'running', 'completed', 'failed'
    project_count = Column(Integer, default=0)  # 抓取的项目数量
    stars_count = Column(Integer, default=0)  # 星标总数
    updates_count = Column(Integer, default=0)  # 更新项目数
    duration = Column(Float)  # 执行耗时(秒)