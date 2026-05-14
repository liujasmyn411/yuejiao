"""
粤教服务 - 数据库连接层
管理数据库连接、会话和表创建
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import Base

load_dotenv()

# ========== 数据库连接 ==========

DB_TYPE = os.getenv("DB_TYPE", "sqlite")

if DB_TYPE == "mysql":
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "123456")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "yuejiao")
    MYSQL_CHARSET = os.getenv("MYSQL_CHARSET", "utf8mb4")

    DATABASE_URL = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
        f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset={MYSQL_CHARSET}"
    )
else:
    DATABASE_URL = os.getenv("SQLITE_URL", "sqlite:///./yuejiao.db")

engine = create_engine(
    DATABASE_URL,
    pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "3600")),
    pool_pre_ping=True,
    pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
    max_overflow=int(os.getenv("DB_POOL_OVERFLOW", "20")),
)
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
