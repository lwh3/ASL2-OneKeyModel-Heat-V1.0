"""
轮询守护进程 - 监听数据库标志位，执行加热算法计算
实现异常重试、断线重连、优雅退出机制
"""

import time
import logging
import signal
import sys
from datetime import datetime
from typing import Optional
import json

from sqlalchemy import and_
from sqlalchemy.exc import OperationalError, DBAPIError

from db.session import DatabaseSessionFactory
from db.models import InputBuffer, OutputBuffer
from algorithms import Algorithm1Historical, Algorithm2Formula

logger = logging.getLogger(__name__)


class PollingDaemon:
    """轮询守护进程"""

    def __init__(self, db_factory: DatabaseSessionFactory, polling_interval: int = 2):
        """
        初始化守护进程

        Args:
            db_factory: 数据库会话工厂
            polling_interval: 轮询间隔 (秒)
        """
        self.db_factory = db_factory
        self.polling_interval = polling_interval
        self.running = False
        self.session = None

        # 算法实例
        self.algorithms = {}

        # 统计信息
        self.stats = {
            'total_processed': 0,
            'success_count': 0,
            'error_count': 0,
            'start_time': None
        }

        # 注册信号处理器
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        logger.info(f"PollingDaemon initialized with interval={polling_interval}s")

    def start(self):
        """启动守护进程"""
        self.running = True
        self.stats['start_time'] = datetime.now()
        logger.info("PollingDaemon starting...")

        while self.running:
            try:
                # 获取数据库会话
                if self.session is None:
                    self.session = self.db_factory.get_session()
                    self._initialize_algorithms()

                # 执行轮询
                self._poll_and_process()

                # 休眠
                time.sleep(self.polling_interval)

            except (OperationalError, DBAPIError) as e:
                # 数据库连接错误，尝试重连
                logger.error(f"Database connection error: {e}")
                self._reconnect_database()
                time.sleep(5)  # 等待5秒后重试

            except Exception as e:
                # 其他异常
                logger.error(f"Unexpected error in polling loop: {e}", exc_info=True)
                time.sleep(self.polling_interval)

        # 退出前清理
        self._cleanup()
        logger.info("PollingDaemon stopped")

    def stop(self):
        """停止守护进程"""
        logger.info("Stopping PollingDaemon...")
        self.running = False

    def _poll_and_process(self):
        """轮询并处理任务"""
        try:
            # 查询待处理任务 (Start_Flag=1, Data_Ready=1)
            tasks = self.session.query(InputBuffer).filter(
                and_(
                    InputBuffer.Start_Flag == 1,
                    InputBuffer.Data_Ready == 1
                )
            ).all()

            if not tasks:
                return

            logger.info(f"Found {len(tasks)} tasks to process")

            for task in tasks:
                self._process_task(task)

        except Exception as e:
            logger.error(f"Error in poll_and_process: {e}", exc_info=True)

    def _process_task(self, task: InputBuffer):
        """
        处理单个任务

        Args:
            task: 输入任务
        """
        task_id = task.Task_ID
        start_time = time.time()

        try:
            logger.info(f"Processing Task_ID={task_id}")

            # 构建输入数据
            input_data = {
                'Task_ID': task.Task_ID,
                'Steel_Grade': task.Steel_Grade,
                'Heat_Stage': task.Heat_Stage,
                'Current_Temp': task.Current_Temp,
                'Target_Temp': task.Target_Temp,
                'Process_Params': task.Process_Params,
                'Realtime_Data': task.Realtime_Data
            }

            # 选择算法
            algorithm = self._select_algorithm()

            # 执行计算
            heat_level, heat_duration, result_data = algorithm.calculate(input_data)

            # 计算处理耗时
            process_time = time.time() - start_time

            # 写入输出表
            self._write_output(
                task_id=task_id,
                heat_level=heat_level,
                heat_duration=heat_duration,
                algorithm_used=algorithm.name,
                result_data=result_data,
                process_time=process_time
            )

            # 重置Start_Flag
            task.Start_Flag = 0
            self.session.commit()

            # 更新统计
            self.stats['total_processed'] += 1
            self.stats['success_count'] += 1

            logger.info(f"Task {task_id} processed successfully in {process_time:.2f}s")

        except Exception as e:
            logger.error(f"Failed to process Task_ID={task_id}: {e}", exc_info=True)

            # 写入错误信息
            self._write_error_output(task_id, str(e))

            # 重置Start_Flag
            task.Start_Flag = 0
            self.session.commit()

            # 更新统计
            self.stats['total_processed'] += 1
            self.stats['error_count'] += 1

    def _select_algorithm(self) -> object:
        """
        选择算法

        Returns:
            算法实例
        """
        # 从配置表读取默认算法
        try:
            from db.models import HeatConfig
            config = self.session.query(HeatConfig).filter_by(Config_Key='DEFAULT_ALGORITHM').first()

            if config and config.Config_Value in self.algorithms:
                return self.algorithms[config.Config_Value]

        except Exception as e:
            logger.warning(f"Failed to get default algorithm from config: {e}")

        # 默认使用Algorithm1
        return self.algorithms.get('Algorithm1', list(self.algorithms.values())[0])

    def _write_output(self, task_id: str, heat_level: int, heat_duration: float,
                      algorithm_used: str, result_data: dict, process_time: float):
        """写入输出表"""
        try:
            # 查找或创建输出记录
            output = self.session.query(OutputBuffer).filter_by(Task_ID=task_id).first()

            if output is None:
                output = OutputBuffer(Task_ID=task_id)
                self.session.add(output)

            # 更新输出数据
            output.Heat_Level = heat_level
            output.Heat_Duration = heat_duration
            output.Predicted_Temp = result_data.get('predicted_temp', 0)
            output.Algorithm_Used = algorithm_used
            output.Result_Data = json.dumps(result_data, ensure_ascii=False)
            output.Finish_Flag = 1
            output.Error_Code = 0
            output.Error_Message = None
            output.Process_Time = process_time
            output.Updated_At = datetime.now()

            self.session.commit()
            logger.debug(f"Output written for Task_ID={task_id}")

        except Exception as e:
            logger.error(f"Failed to write output for Task_ID={task_id}: {e}")
            self.session.rollback()
            raise

    def _write_error_output(self, task_id: str, error_message: str):
        """写入错误输出"""
        try:
            output = self.session.query(OutputBuffer).filter_by(Task_ID=task_id).first()

            if output is None:
                output = OutputBuffer(Task_ID=task_id)
                self.session.add(output)

            output.Finish_Flag = 1
            output.Error_Code = 1
            output.Error_Message = error_message
            output.Updated_At = datetime.now()

            self.session.commit()

        except Exception as e:
            logger.error(f"Failed to write error output for Task_ID={task_id}: {e}")
            self.session.rollback()

    def _initialize_algorithms(self):
        """初始化算法实例"""
        try:
            self.algorithms = {
                'Algorithm1': Algorithm1Historical(self.session),
                'Algorithm2': Algorithm2Formula(self.session)
            }
            logger.info(f"Algorithms initialized: {list(self.algorithms.keys())}")

        except Exception as e:
            logger.error(f"Failed to initialize algorithms: {e}")
            raise

    def _reconnect_database(self):
        """重连数据库"""
        logger.info("Attempting to reconnect to database...")

        try:
            if self.session:
                self.session.close()
                self.session = None

            # 等待一段时间
            time.sleep(2)

            # 测试连接
            if self.db_factory.test_connection():
                self.session = self.db_factory.get_session()
                self._initialize_algorithms()
                logger.info("Database reconnection successful")
            else:
                logger.error("Database reconnection failed")

        except Exception as e:
            logger.error(f"Error during database reconnection: {e}")

    def _cleanup(self):
        """清理资源"""
        logger.info("Cleaning up resources...")

        if self.session:
            try:
                self.session.close()
            except Exception as e:
                logger.error(f"Error closing session: {e}")

        # 打印统计信息
        self._print_statistics()

    def _print_statistics(self):
        """打印统计信息"""
        if self.stats['start_time']:
            runtime = datetime.now() - self.stats['start_time']
            logger.info("=" * 60)
            logger.info("Daemon Statistics:")
            logger.info(f"  Runtime: {runtime}")
            logger.info(f"  Total Processed: {self.stats['total_processed']}")
            logger.info(f"  Success Count: {self.stats['success_count']}")
            logger.info(f"  Error Count: {self.stats['error_count']}")
            logger.info("=" * 60)

    def _signal_handler(self, signum, frame):
        """信号处理器 (优雅退出)"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop()
