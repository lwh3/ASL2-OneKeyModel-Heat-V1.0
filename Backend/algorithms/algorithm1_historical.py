"""
算法1: 历史数据预测算法
基于历史加热数据进行预测，适用于钢种和加热阶段固定的场景
"""

import logging
from typing import Dict, Any, Tuple
from sqlalchemy import and_

from .base import BaseAlgorithm
from db.models import HeatHistory

logger = logging.getLogger(__name__)


class Algorithm1Historical(BaseAlgorithm):
    """历史数据预测算法"""

    def __init__(self, db_session):
        super().__init__(name="Algorithm1_Historical", db_session=db_session)

    def calculate(self, input_data: Dict[str, Any]) -> Tuple[int, float, Dict[str, Any]]:
        """
        基于历史数据预测加热档位和时长

        策略:
        1. 查询相同钢种、相同加热阶段的历史成功记录
        2. 计算平均加热档位和时长
        3. 根据温差进行微调

        Args:
            input_data: 输入数据

        Returns:
            Tuple[加热档位, 加热时长(分钟), 详细结果]
        """
        # 验证输入
        if not self.validate_input(input_data):
            raise ValueError("Invalid input data")

        steel_grade = input_data['Steel_Grade']
        heat_stage = input_data['Heat_Stage']
        current_temp = float(input_data.get('Current_Temp', 0))
        target_temp = float(input_data['Target_Temp'])
        temp_diff = target_temp - current_temp

        # 查询历史数据
        historical_records = self._query_historical_data(steel_grade, heat_stage)

        if not historical_records or len(historical_records) == 0:
            # 没有历史数据，使用默认策略
            logger.warning(
                f"No historical data found for Steel_Grade={steel_grade}, Heat_Stage={heat_stage}. "
                f"Using default strategy."
            )
            return self._default_strategy(temp_diff)

        # 计算历史平均值
        avg_heat_level, avg_duration = self._calculate_averages(historical_records)

        # 根据温差进行微调
        adjusted_level, adjusted_duration = self._adjust_by_temp_diff(
            avg_heat_level, avg_duration, temp_diff, historical_records
        )

        # 限制档位范围
        final_level = self.clamp_heat_level(adjusted_level)

        # 构建详细结果
        result_data = {
            'algorithm': self.name,
            'steel_grade': steel_grade,
            'heat_stage': heat_stage,
            'historical_records_count': len(historical_records),
            'avg_historical_level': round(avg_heat_level, 2),
            'avg_historical_duration': round(avg_duration, 2),
            'temp_diff': round(temp_diff, 2),
            'adjusted_level': final_level,
            'adjusted_duration': round(adjusted_duration, 2),
            'confidence': self._calculate_confidence(len(historical_records))
        }

        self.log_calculation_result(input_data, final_level, adjusted_duration, result_data)

        return final_level, adjusted_duration, result_data

    def _query_historical_data(self, steel_grade: str, heat_stage: str):
        """
        查询历史数据

        Args:
            steel_grade: 钢种
            heat_stage: 加热阶段

        Returns:
            历史记录列表
        """
        try:
            # 查询最近50条成功记录
            records = self.db_session.query(HeatHistory).filter(
                and_(
                    HeatHistory.Steel_Grade == steel_grade,
                    HeatHistory.Heat_Stage == heat_stage,
                    HeatHistory.Success == 1
                )
            ).order_by(HeatHistory.Timestamp.desc()).limit(50).all()

            return records

        except Exception as e:
            logger.error(f"Failed to query historical data: {e}")
            return []

    def _calculate_averages(self, records):
        """
        计算历史数据的平均加热档位和时长

        Args:
            records: 历史记录列表

        Returns:
            Tuple[平均档位, 平均时长]
        """
        total_level = sum(float(r.Heat_Level) for r in records)
        total_duration = sum(float(r.Heat_Duration) for r in records)

        avg_level = total_level / len(records)
        avg_duration = total_duration / len(records)

        return avg_level, avg_duration

    def _adjust_by_temp_diff(self, base_level: float, base_duration: float,
                              temp_diff: float, records) -> Tuple[int, float]:
        """
        根据温差对基准值进行微调

        策略:
        - 温差每增加100℃，档位+1，时长按比例增加
        - 参考历史数据中的温差分布进行修正

        Args:
            base_level: 基准档位
            base_duration: 基准时长
            temp_diff: 温度差
            records: 历史记录

        Returns:
            Tuple[调整后档位, 调整后时长]
        """
        # 计算历史平均温差
        avg_historical_temp_diff = sum(
            float(r.End_Temp - r.Start_Temp) for r in records
        ) / len(records)

        # 温差系数
        if avg_historical_temp_diff > 0:
            temp_ratio = temp_diff / avg_historical_temp_diff
        else:
            temp_ratio = 1.0

        # 调整档位和时长
        adjusted_level = int(round(base_level * temp_ratio))
        adjusted_duration = base_duration * temp_ratio

        # 确保时长不小于5分钟
        adjusted_duration = max(5.0, adjusted_duration)

        return adjusted_level, adjusted_duration

    def _default_strategy(self, temp_diff: float) -> Tuple[int, float, Dict[str, Any]]:
        """
        默认策略 (无历史数据时使用)

        简单规则:
        - 温差 0-100℃: 档位5, 时长10分钟
        - 温差 100-200℃: 档位7, 时长20分钟
        - 温差 200-300℃: 档位9, 时长30分钟
        - 温差 >300℃: 档位10, 时长40分钟

        Args:
            temp_diff: 温度差

        Returns:
            Tuple[档位, 时长, 结果数据]
        """
        if temp_diff <= 100:
            level, duration = 5, 10.0
        elif temp_diff <= 200:
            level, duration = 7, 20.0
        elif temp_diff <= 300:
            level, duration = 9, 30.0
        else:
            level, duration = 10, 40.0

        result_data = {
            'algorithm': self.name,
            'strategy': 'default',
            'temp_diff': round(temp_diff, 2),
            'level': level,
            'duration': duration,
            'confidence': 0.5  # 默认策略置信度较低
        }

        return level, duration, result_data

    def _calculate_confidence(self, record_count: int) -> float:
        """
        计算预测置信度

        Args:
            record_count: 历史记录数量

        Returns:
            float: 置信度 (0-1)
        """
        # 简单规则: 记录越多，置信度越高
        if record_count >= 50:
            return 0.95
        elif record_count >= 30:
            return 0.85
        elif record_count >= 10:
            return 0.75
        else:
            return 0.60
