"""
粤教服务 - 日志配置模块
"""

import logging
import os
from datetime import datetime


def setup_logging(log_dir: str = "log", log_level: str = "INFO"):
    """配置日志系统"""
    # 确保日志目录存在
    os.makedirs(log_dir, exist_ok=True)

    # 日志文件名（按日期）
    log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log")

    # 配置日志格式
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # 配置根日志记录器
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format=log_format,
        datefmt=date_format,
        handlers=[
            # 控制台输出
            logging.StreamHandler(),
            # 文件输出
            logging.FileHandler(log_file, encoding="utf-8")
        ]
    )

    return logging.getLogger(__name__)
