"""
日志工具
"""

import logging
import sys
from pathlib import Path
from loguru import logger


def setup_logger(name: str = "WQFactorMiner", 
                log_file: str = "logs/wq_factor_miner.log",
                level: str = "INFO",
                max_size_mb: int = 10,
                backup_count: int = 5) -> logging.Logger:
    """
    设置日志
    
    Args:
        name: 日志名称
        log_file: 日志文件路径
        level: 日志级别
        max_size_mb: 最大文件大小(MB)
        backup_count: 备份文件数量
    
    Returns:
        Logger实例
    """
    # 创建日志目录
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 移除默认处理器
    logger.remove()
    
    # 添加控制台处理器
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=level,
        colorize=True
    )
    
    # 添加文件处理器
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=level,
        rotation=f"{max_size_mb} MB",
        retention=backup_count,
        compression="zip"
    )
    
    return logger


class LoggerAdapter:
    """日志适配器 - 兼容标准logging"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs)