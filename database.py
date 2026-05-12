"""
粤教服务 - 数据库连接层
管理数据库连接、会话和表创建
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import Base

# ========== 数据库连接 ==========
# SQLite 数据库文件会创建在当前目录下的 yuejiao.db
engine = create_engine(
    "sqlite:///./yuejiao.db",
    connect_args={"check_same_thread": False}  # 允许多线程访问
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
