"""
数据库会话管理 - 多数据库连接工厂
支持: PostgreSQL, MySQL, Oracle, SQLite
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
import os
import logging

from .models import Base

logger = logging.getLogger(__name__)


class DatabaseSessionFactory:
    """数据库会话工厂 - 支持多种数据库"""

    def __init__(self, db_type='postgresql', **kwargs):
        """
        初始化数据库连接

        Args:
            db_type: 数据库类型 ('postgresql', 'mysql', 'oracle', 'sqlite')
            **kwargs: 数据库连接参数
                - host: 数据库主机
                - port: 数据库端口
                - database: 数据库名称
                - username: 用户名
                - password: 密码
                - sqlite_path: SQLite数据库文件路径 (仅SQLite需要)
        """
        self.db_type = db_type.lower()
        self.engine = None
        self.SessionLocal = None

        # 构建连接字符串
        connection_string = self._build_connection_string(**kwargs)

        # 创建引擎
        self._create_engine(connection_string)

        # 创建会话工厂
        self.SessionLocal = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        )

        logger.info(f"Database session factory initialized for {self.db_type}")

    def _build_connection_string(self, **kwargs):
        """根据数据库类型构建连接字符串"""

        if self.db_type == 'postgresql':
            host = kwargs.get('host', 'localhost')
            port = kwargs.get('port', 5432)
            database = kwargs.get('database', 'heat_model')
            username = kwargs.get('username', 'postgres')
            password = kwargs.get('password', '')
            return f"postgresql://{username}:{password}@{host}:{port}/{database}"

        elif self.db_type == 'mysql':
            host = kwargs.get('host', 'localhost')
            port = kwargs.get('port', 3306)
            database = kwargs.get('database', 'heat_model')
            username = kwargs.get('username', 'root')
            password = kwargs.get('password', '')
            return f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}?charset=utf8mb4"

        elif self.db_type == 'oracle':
            host = kwargs.get('host', 'localhost')
            port = kwargs.get('port', 1521)
            service_name = kwargs.get('service_name', 'ORCL')
            username = kwargs.get('username', 'system')
            password = kwargs.get('password', '')
            return f"oracle+cx_oracle://{username}:{password}@{host}:{port}/?service_name={service_name}"

        elif self.db_type == 'sqlite':
            sqlite_path = kwargs.get('sqlite_path', './heat_model.db')
            return f"sqlite:///{sqlite_path}"

        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")

    def _create_engine(self, connection_string):
        """创建数据库引擎"""

        engine_kwargs = {
            'echo': False,  # 生产环境设为False
            'pool_pre_ping': True,  # 连接池健康检查
        }

        # SQLite不需要连接池
        if self.db_type != 'sqlite':
            engine_kwargs.update({
                'poolclass': QueuePool,
                'pool_size': 10,
                'max_overflow': 20,
                'pool_recycle': 3600,  # 1小时回收连接
            })

        self.engine = create_engine(connection_string, **engine_kwargs)
        logger.info(f"Database engine created: {self.db_type}")

    def create_tables(self):
        """创建所有表"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("All tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise

    def get_session(self):
        """获取数据库会话"""
        return self.SessionLocal()

    def close_session(self, session):
        """关闭数据库会话"""
        try:
            session.close()
            logger.debug("Database session closed")
        except Exception as e:
            logger.error(f"Error closing session: {e}")

    def dispose_engine(self):
        """销毁引擎连接池"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database engine disposed")

    def test_connection(self):
        """测试数据库连接"""
        try:
            session = self.get_session()
            session.execute("SELECT 1")
            self.close_session(session)
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False


# 全局数据库会话工厂实例
db_factory = None


def init_database(db_type='postgresql', **kwargs):
    """
    初始化全局数据库连接

    Args:
        db_type: 数据库类型
        **kwargs: 数据库连接参数

    Returns:
        DatabaseSessionFactory实例
    """
    global db_factory
    db_factory = DatabaseSessionFactory(db_type=db_type, **kwargs)
    return db_factory


def get_db_session():
    """获取数据库会话 (全局工厂方法)"""
    if db_factory is None:
        raise RuntimeError("Database factory not initialized. Call init_database() first.")
    return db_factory.get_session()
