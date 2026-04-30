"""
算法基类 - 定义加热算法的统一接口
"""

from abc import ABC, abstractmethod
import json
import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)


class BaseAlgorithm(ABC):
    """加热算法基类"""

    def __init__(self, name: str, db_session):
        """
        初始化算法

        Args:
            name: 算法名称
            db_session: 数据库会话
        """
        self.name = name
        self.db_session = db_session
        logger.info(f"Algorithm {self.name} initialized")

    @abstractmethod
    def calculate(self, input_data: Dict[str, Any]) -> Tuple[int, float, Dict[str, Any]]:
        """
        执行加热计算

        Args:
            input_data: 输入数据字典，包含:
                - Task_ID: 任务ID
                - Steel_Grade: 钢种
                - Heat_Stage: 加热阶段
                - Current_Temp: 当前温度
                - Target_Temp: 目标温度
                - Process_Params: 工艺参数 (JSON字符串)
                - Realtime_Data: 实时数据 (JSON字符串)

        Returns:
            Tuple[int, float, Dict[str, Any]]:
                - heat_level: 加热档位 (1-10)
                - heat_duration: 加热时长 (分钟)
                - result_data: 详细结果数据字典
        """
        pass

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        验证输入数据有效性

        Args:
            input_data: 输入数据字典

        Returns:
            bool: 数据是否有效
        """
        required_fields = ['Task_ID', 'Steel_Grade', 'Heat_Stage', 'Target_Temp']

        for field in required_fields:
            if field not in input_data or input_data[field] is None:
                logger.error(f"Missing required field: {field}")
                return False

        # 验证温度范围 (0-2000℃)
        target_temp = float(input_data['Target_Temp'])
        if target_temp < 0 or target_temp > 2000:
            logger.error(f"Invalid target temperature: {target_temp}")
            return False

        if 'Current_Temp' in input_data and input_data['Current_Temp'] is not None:
            current_temp = float(input_data['Current_Temp'])
            if current_temp < 0 or current_temp > 2000:
                logger.error(f"Invalid current temperature: {current_temp}")
                return False

        return True

    def parse_json_field(self, json_str: str, field_name: str) -> Dict[str, Any]:
        """
        解析JSON字段

        Args:
            json_str: JSON字符串
            field_name: 字段名称 (用于日志)

        Returns:
            Dict[str, Any]: 解析后的字典，解析失败返回空字典
        """
        if not json_str:
            return {}

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse {field_name}: {e}")
            return {}

    def clamp_heat_level(self, heat_level: int, min_level: int = 1, max_level: int = 10) -> int:
        """
        限制加热档位在有效范围内

        Args:
            heat_level: 计算得到的加热档位
            min_level: 最小档位
            max_level: 最大档位

        Returns:
            int: 限制后的档位
        """
        return max(min_level, min(heat_level, max_level))

    def get_config_value(self, config_key: str, default_value: Any = None) -> Any:
        """
        从数据库读取配置值

        Args:
            config_key: 配置键
            default_value: 默认值

        Returns:
            Any: 配置值
        """
        try:
            from db.models import HeatConfig

            config = self.db_session.query(HeatConfig).filter_by(Config_Key=config_key).first()

            if config:
                # 根据配置类型转换值
                if config.Config_Type == 'INT':
                    return int(config.Config_Value)
                elif config.Config_Type == 'FLOAT':
                    return float(config.Config_Value)
                elif config.Config_Type == 'JSON':
                    return json.loads(config.Config_Value)
                else:
                    return config.Config_Value

            return default_value

        except Exception as e:
            logger.error(f"Failed to get config value for {config_key}: {e}")
            return default_value

    def log_calculation_result(self, input_data: Dict[str, Any], heat_level: int,
                                heat_duration: float, result_data: Dict[str, Any]):
        """
        记录计算结果日志

        Args:
            input_data: 输入数据
            heat_level: 计算得到的加热档位
            heat_duration: 计算得到的加热时长
            result_data: 详细结果数据
        """
        logger.info(
            f"Algorithm {self.name} calculated: "
            f"Task_ID={input_data['Task_ID']}, "
            f"Steel_Grade={input_data['Steel_Grade']}, "
            f"Heat_Stage={input_data['Heat_Stage']}, "
            f"Heat_Level={heat_level}, "
            f"Heat_Duration={heat_duration:.2f}min"
        )

    def __repr__(self):
        return f"<{self.__class__.__name__}(name={self.name})>"
