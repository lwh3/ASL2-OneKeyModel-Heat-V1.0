"""
增强日志模块 - 支持日志轮转、颜色输出、多级别控制
Enhanced Logging Module - Log rotation, colored output, multi-level control
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional
import colorlog


def setup_logging(config_manager=None, log_level: str = 'INFO', log_file: Optional[str] = None):
    """
    配置增强日志系统

    Args:
        config_manager: 配置管理器
        log_level: 日志级别
        log_file: 日志文件路径
    """
    # 从配置管理器获取配置
    if config_manager:
        log_level = config_manager.get('logging.level', 'INFO')
        log_file = config_manager.get('logging.file_path', 'logs/heat_model.log')
        max_bytes = config_manager.get('logging.max_bytes', 10485760)  # 10MB
        backup_count = config_manager.get('logging.backup_count', 5)
        console_enabled = config_manager.get('logging.console', True)
        file_enabled = config_manager.get('logging.file', True)
        log_format = config_manager.get('logging.format',
                                        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    else:
        max_bytes = 10485760  # 10MB
        backup_count = 5
        console_enabled = True
        file_enabled = True
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # 获取根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # 清除已有的处理器
    root_logger.handlers.clear()

    handlers = []

    # 控制台处理器 (带颜色)
    if console_enabled:
        console_handler = colorlog.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))

        # 彩色格式
        color_formatter = colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
        console_handler.setFormatter(color_formatter)
        handlers.append(console_handler)

    # 文件处理器 (带轮转)
    if file_enabled and log_file:
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

        # 使用RotatingFileHandler实现日志轮转
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))

        # 文件格式 (不需要颜色)
        file_formatter = logging.Formatter(
            log_format,
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        handlers.append(file_handler)

    # 添加所有处理器到根日志记录器
    for handler in handlers:
        root_logger.addHandler(handler)

    logging.info("=" * 80)
    logging.info("Logging system initialized")
    logging.info(f"Log level: {log_level}")
    logging.info(f"Console output: {console_enabled}")
    logging.info(f"File output: {file_enabled}")
    if file_enabled and log_file:
        logging.info(f"Log file: {log_file}")
    logging.info("=" * 80)


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        logging.Logger: 日志记录器
    """
    return logging.getLogger(name)


class PerformanceLogger:
    """性能日志记录器 - 用于记录函数执行时间"""

    def __init__(self, logger: logging.Logger, operation: str):
        """
        初始化性能日志记录器

        Args:
            logger: 日志记录器
            operation: 操作名称
        """
        self.logger = logger
        self.operation = operation
        self.start_time = None

    def __enter__(self):
        """进入上下文"""
        import time
        self.start_time = time.time()
        self.logger.debug(f"Starting: {self.operation}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文"""
        import time
        elapsed = time.time() - self.start_time
        if exc_type is None:
            self.logger.info(f"Completed: {self.operation} (took {elapsed:.3f}s)")
        else:
            self.logger.error(f"Failed: {self.operation} (took {elapsed:.3f}s) - {exc_val}")


# 导出便捷函数
def log_performance(logger: logging.Logger, operation: str):
    """
    性能日志装饰器

    Usage:
        @log_performance(logger, "my_operation")
        def my_function():
            ...
    """
    def decorator(func):
        import functools

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with PerformanceLogger(logger, operation):
                return func(*args, **kwargs)

        return wrapper

    return decorator
