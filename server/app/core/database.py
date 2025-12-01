from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings #引入环境变量

"""
1、数据库连接地址
"""
engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)

Base = declarative_base()

#依赖注入函数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()