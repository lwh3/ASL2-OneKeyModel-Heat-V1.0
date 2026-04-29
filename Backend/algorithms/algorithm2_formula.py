"""
算法2: 公式计算算法
基于配置的数学公式计算加热档位和时长
适用于已知工艺参数的场景
"""

import logging
import math
from typing import Dict, Any, Tuple

from .base import BaseAlgorithm

logger = logging.getLogger(__name__)


class Algorithm2Formula(BaseAlgorithm):
    """公式计算算法"""

    def __init__(self, db_session):
        super().__init__(name="Algorithm2_Formula", db_session=db_session)
        self._load_formula_params()

    def _load_formula_params(self):
        """从数据库加载公式参数"""
        default_params = {
            'base_coefficient': 1.2,      # 基础系数
            'temp_factor': 0.015,          # 温度因子
            'stage_multiplier': {          # 阶段乘数
                '初加热': 1.0,
                '精炼': 0.8,
                '保温': 0.5,
                '升温': 1.2
            },
            'steel_grade_modifier': {      # 钢种修正系数
                '碳钢': 1.0,
                '合金钢': 1.1,
                '不锈钢': 1.2,
                '高温合金': 1.3
            },
            'min_duration': 5.0,           # 最小加热时长 (分钟)
            'max_duration': 120.0          # 最大加热时长 (分钟)
        }

        # 尝试从数据库读取配置
        config_params = self.get_config_value('FORMULA_PARAMS', default_params)

        if isinstance(config_params, dict):
            self.formula_params = config_params
        else:
            self.formula_params = default_params

        logger.info(f"Formula parameters loaded: {self.formula_params}")

    def calculate(self, input_data: Dict[str, Any]) -> Tuple[int, float, Dict[str, Any]]:
        """
        基于公式计算加热档位和时长

        核心公式:
        1. 加热档位 = base_coefficient × (1 + temp_factor × ΔT) × stage_multiplier × steel_modifier
        2. 加热时长 = (ΔT / 10) × stage_multiplier × steel_modifier

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

        # 解析工艺参数 (可能包含额外的修正系数)
        process_params = self.parse_json_field(input_data.get('Process_Params', ''), 'Process_Params')

        # 获取公式参数
        base_coeff = self.formula_params.get('base_coefficient', 1.2)
        temp_factor = self.formula_params.get('temp_factor', 0.015)

        # 获取阶段乘数
        stage_multipliers = self.formula_params.get('stage_multiplier', {})
        stage_mult = stage_multipliers.get(heat_stage, 1.0)

        # 获取钢种修正系数
        steel_modifiers = self.formula_params.get('steel_grade_modifier', {})
        steel_mod = self._find_steel_modifier(steel_grade, steel_modifiers)

        # 应用工艺参数中的额外修正系数
        custom_mult = process_params.get('custom_multiplier', 1.0)

        # 计算加热档位
        heat_level_raw = base_coeff * (1 + temp_factor * temp_diff) * stage_mult * steel_mod * custom_mult
        heat_level = int(round(heat_level_raw))
        heat_level = self.clamp_heat_level(heat_level)

        # 计算加热时长 (分钟)
        duration_raw = (temp_diff / 10.0) * stage_mult * steel_mod * custom_mult
        heat_duration = max(
            self.formula_params.get('min_duration', 5.0),
            min(duration_raw, self.formula_params.get('max_duration', 120.0))
        )

        # 构建详细结果
        result_data = {
            'algorithm': self.name,
            'steel_grade': steel_grade,
            'heat_stage': heat_stage,
            'temp_diff': round(temp_diff, 2),
            'base_coefficient': base_coeff,
            'temp_factor': temp_factor,
            'stage_multiplier': stage_mult,
            'steel_modifier': steel_mod,
            'custom_multiplier': custom_mult,
            'raw_level': round(heat_level_raw, 2),
            'final_level': heat_level,
            'raw_duration': round(duration_raw, 2),
            'final_duration': round(heat_duration, 2),
            'confidence': 0.85  # 公式计算置信度固定
        }

        self.log_calculation_result(input_data, heat_level, heat_duration, result_data)

        return heat_level, heat_duration, result_data

    def _find_steel_modifier(self, steel_grade: str, modifiers: Dict[str, float]) -> float:
        """
        查找钢种修正系数

        策略: 如果完全匹配则使用，否则尝试部分匹配，最后使用默认值1.0

        Args:
            steel_grade: 钢种名称
            modifiers: 钢种修正系数字典

        Returns:
            float: 修正系数
        """
        # 完全匹配
        if steel_grade in modifiers:
            return modifiers[steel_grade]

        # 部分匹配 (例如 "Q235碳钢" 匹配 "碳钢")
        for key, value in modifiers.items():
            if key in steel_grade:
                logger.info(f"Partial match for steel grade: {steel_grade} -> {key}")
                return value

        # 默认值
        logger.warning(f"No modifier found for steel grade: {steel_grade}, using default 1.0")
        return 1.0

    def update_formula_params(self, new_params: Dict[str, Any]):
        """
        更新公式参数

        Args:
            new_params: 新的公式参数
        """
        self.formula_params.update(new_params)
        logger.info(f"Formula parameters updated: {self.formula_params}")

        # 可选: 持久化到数据库
        try:
            import json
            from db.models import HeatConfig

            config = self.db_session.query(HeatConfig).filter_by(Config_Key='FORMULA_PARAMS').first()
            if config:
                config.Config_Value = json.dumps(self.formula_params)
                self.db_session.commit()
                logger.info("Formula parameters saved to database")
        except Exception as e:
            logger.error(f"Failed to save formula parameters to database: {e}")
            self.db_session.rollback()
