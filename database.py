"""
粤教服务 - 数据库连接层
管理数据库连接、会话和表创建
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import Base

# ========== 数据库连接 ==========

MYSQL_USER = "root"
MYSQL_PASSWORD = "123456"
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_DATABASE = "yuejiao"

MYSQL_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"

engine = create_engine(MYSQL_URL, pool_recycle=3600, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ========== 工具函数 ==========

def create_tables():
    """创建所有表（如果不存在）"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

