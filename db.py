from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# 配置数据库连接信息
DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/github_trending?charset=utf8mb4"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from models import Base

def create_db_tables():
    Base.metadata.create_all(engine)