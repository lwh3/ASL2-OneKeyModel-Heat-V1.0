"""
配置管理模块 - 统一配置文件加载和管理
Configuration Manager - Unified configuration loading and management
"""

import os
import yaml
import json
import logging
from typing import Any, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置管理器

        Args:
            config_path: 配置文件路径，默认使用config.yaml
        """
        self.config_path = config_path or self._find_config_file()
        self.config = self._load_config()
        logger.info(f"Configuration loaded from: {self.config_path}")

    def _find_config_file(self) -> str:
        """查找配置文件"""
        possible_paths = [
            "./config.yaml",
            "./config.yml",
            "./Backend/config.yaml",
            "./Backend/config.yml",
            os.path.join(os.path.dirname(__file__), "config.yaml"),
            os.path.join(os.path.dirname(__file__), "config.yml"),
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        # 如果找不到，使用默认路径
        return os.path.join(os.path.dirname(__file__), "config.yaml")

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            if not os.path.exists(self.config_path):
                logger.warning(f"Config file not found: {self.config_path}, using defaults")
                return self._default_config()

            with open(self.config_path, 'r', encoding='utf-8') as f:
                if self.config_path.endswith('.json'):
                    config = json.load(f)
                else:
                    config = yaml.safe_load(f)

            return config or {}

        except Exception as e:
            logger.error(f"Failed to load config file: {e}")
            return self._default_config()

    def _default_config(self) -> Dict[str, Any]:
        """默认配置"""
        return {
            'database': {
                'type': 'sqlite',
                'sqlite_path': './heat_model.db',
                'create_tables': True
            },
            'daemon': {
                'polling_interval': 2,
                'max_retries': 3,
                'retry_delay': 5
            },
            'logging': {
                'level': 'INFO',
                'console': True,
                'file': True,
                'file_path': 'logs/heat_model.log'
            },
            'web_ui': {
                'enabled': True,
                'host': '0.0.0.0',
                'port': 5000,
                'debug': False
            },
            'algorithms': {
                'default': 'Algorithm1',
                'enabled': ['Algorithm1', 'Algorithm2']
            },
            'heating': {
                'min_level': 1,
                'max_level': 10,
                'min_temp': 0,
                'max_temp': 2000
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值 (支持点号分隔的层级访问)

        Args:
            key: 配置键，支持 "database.type" 格式
            default: 默认值

        Returns:
            配置值
        """
        keys = key.split('.')
        value = self.config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any):
        """
        设置配置值

        Args:
            key: 配置键
            value: 配置值
        """
        keys = key.split('.')
        config = self.config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def save(self, path: Optional[str] = None):
        """
        保存配置到文件

        Args:
            path: 保存路径，默认使用原路径
        """
        save_path = path or self.config_path

        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(save_path) or '.', exist_ok=True)

            with open(save_path, 'w', encoding='utf-8') as f:
                if save_path.endswith('.json'):
                    json.dump(self.config, f, indent=2, ensure_ascii=False)
                else:
                    yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False)

            logger.info(f"Configuration saved to: {save_path}")

        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            raise

    def reload(self):
        """重新加载配置"""
        self.config = self._load_config()
        logger.info("Configuration reloaded")

    def to_dict(self) -> Dict[str, Any]:
        """返回配置字典"""
        return self.config.copy()

    def __repr__(self):
        return f"<ConfigManager(config_path={self.config_path})>"


# 全局配置实例
_config_instance = None


def get_config() -> ConfigManager:
    """获取全局配置实例"""
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigManager()
    return _config_instance


def init_config(config_path: Optional[str] = None) -> ConfigManager:
    """初始化全局配置"""
    global _config_instance
    _config_instance = ConfigManager(config_path)
    return _config_instance
