"""
主程序入口 - LF精炼炉加热模型守护进程
支持命令行参数配置数据库连接
"""

import argparse
import logging
import sys
import os

# 添加Backend目录到sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.session import init_database
from daemon import PollingDaemon


def setup_logging(log_level: str = 'INFO'):
    """
    配置日志

    Args:
        log_level: 日志级别 ('DEBUG', 'INFO', 'WARNING', 'ERROR')
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('heat_model_daemon.log', encoding='utf-8')
        ]
    )


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='LF精炼炉加热模型守护进程',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 使用PostgreSQL (默认)
  python main.py --db-type postgresql --host localhost --port 5432 --database heat_model --username postgres --password mypass

  # 使用MySQL
  python main.py --db-type mysql --host localhost --port 3306 --database heat_model --username root --password mypass

  # 使用SQLite (本地文件)
  python main.py --db-type sqlite --sqlite-path ./heat_model.db

  # 使用Oracle
  python main.py --db-type oracle --host localhost --port 1521 --service-name ORCL --username system --password mypass
        """
    )

    # 数据库配置
    parser.add_argument('--db-type', type=str, default='sqlite',
                        choices=['postgresql', 'mysql', 'oracle', 'sqlite'],
                        help='数据库类型 (默认: sqlite)')

    parser.add_argument('--host', type=str, default='localhost',
                        help='数据库主机地址 (默认: localhost)')

    parser.add_argument('--port', type=int, default=None,
                        help='数据库端口 (默认: PostgreSQL=5432, MySQL=3306, Oracle=1521)')

    parser.add_argument('--database', type=str, default='heat_model',
                        help='数据库名称 (默认: heat_model)')

    parser.add_argument('--username', type=str, default=None,
                        help='数据库用户名')

    parser.add_argument('--password', type=str, default=None,
                        help='数据库密码')

    parser.add_argument('--sqlite-path', type=str, default='./heat_model.db',
                        help='SQLite数据库文件路径 (仅SQLite需要, 默认: ./heat_model.db)')

    parser.add_argument('--service-name', type=str, default='ORCL',
                        help='Oracle服务名 (仅Oracle需要, 默认: ORCL)')

    # 守护进程配置
    parser.add_argument('--polling-interval', type=int, default=2,
                        help='轮询间隔 (秒, 默认: 2)')

    parser.add_argument('--create-tables', action='store_true',
                        help='启动时创建数据库表 (如果不存在)')

    # 日志配置
    parser.add_argument('--log-level', type=str, default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        help='日志级别 (默认: INFO)')

    return parser.parse_args()


def build_db_config(args):
    """构建数据库配置"""
    config = {
        'db_type': args.db_type,
        'database': args.database,
    }

    # 根据数据库类型设置默认端口
    if args.port:
        config['port'] = args.port
    else:
        if args.db_type == 'postgresql':
            config['port'] = 5432
        elif args.db_type == 'mysql':
            config['port'] = 3306
        elif args.db_type == 'oracle':
            config['port'] = 1521

    # SQLite特殊处理
    if args.db_type == 'sqlite':
        config['sqlite_path'] = args.sqlite_path
    else:
        config['host'] = args.host
        config['username'] = args.username or 'root'
        config['password'] = args.password or ''

    # Oracle特殊参数
    if args.db_type == 'oracle':
        config['service_name'] = args.service_name

    return config


def main():
    """主函数"""
    # 解析参数
    args = parse_arguments()

    # 配置日志
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info("LF精炼炉加热模型守护进程")
    logger.info("=" * 60)

    try:
        # 构建数据库配置
        db_config = build_db_config(args)
        logger.info(f"Database configuration: {db_config['db_type']}")

        # 初始化数据库
        db_factory = init_database(**db_config)

        # 测试连接
        if not db_factory.test_connection():
            logger.error("Database connection test failed. Exiting...")
            sys.exit(1)

        # 创建表 (如果需要)
        if args.create_tables:
            logger.info("Creating database tables...")
            db_factory.create_tables()

        # 启动守护进程
        daemon = PollingDaemon(
            db_factory=db_factory,
            polling_interval=args.polling_interval
        )

        logger.info("Starting daemon...")
        daemon.start()

    except KeyboardInterrupt:
        logger.info("Interrupted by user")

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

    finally:
        logger.info("Program terminated")


if __name__ == '__main__':
    main()
