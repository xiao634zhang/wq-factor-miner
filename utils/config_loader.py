"""
配置加载工具
"""

import os
import yaml
from typing import Dict, Any
from pathlib import Path


class ConfigLoader:
    """配置加载器"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        初始化配置加载器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config = {}
        
        self.load()
    
    def load(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        return self.config
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项
        
        Args:
            key: 配置键（支持点号分隔的嵌套键）
            default: 默认值
        
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        获取配置节
        
        Args:
            section: 节名称
        
        Returns:
            配置字典
        """
        return self.config.get(section, {})
    
    def set(self, key: str, value: Any):
        """
        设置配置项
        
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
    
    def save(self, path: str = None):
        """
        保存配置到文件
        
        Args:
            path: 文件路径（默认使用原路径）
        """
        path = path or self.config_path
        
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
    
    def reload(self):
        """重新加载配置"""
        self.load()
    
    def validate(self) -> bool:
        """
        验证配置
        
        Returns:
            是否有效
        """
        required_keys = [
            'worldquant.username',
            'worldquant.password'
        ]
        
        for key in required_keys:
            if self.get(key) is None:
                return False
        
        return True


def get_config(config_path: str = "config.yaml") -> ConfigLoader:
    """
    获取配置加载器实例
    
    Args:
        config_path: 配置文件路径
    
    Returns:
        ConfigLoader实例
    """
    return ConfigLoader(config_path)
