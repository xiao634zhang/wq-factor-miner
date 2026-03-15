"""
辅助函数
"""

import json
import time
import hashlib
from typing import Dict, List, Any
from datetime import datetime


def save_json(data: Any, filepath: str, indent: int = 2):
    """
    保存JSON文件
    
    Args:
        data: 数据
        filepath: 文件路径
        indent: 缩进
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def load_json(filepath: str) -> Any:
    """
    加载JSON文件
    
    Args:
        filepath: 文件路径
    
    Returns:
        数据
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_id(formula: str) -> str:
    """
    生成因子ID
    
    Args:
        formula: 因子公式
    
    Returns:
        ID字符串
    """
    return hashlib.md5(formula.encode()).hexdigest()[:8]


def format_time(timestamp: float = None) -> str:
    """
    格式化时间
    
    Args:
        timestamp: 时间戳
    
    Returns:
        时间字符串
    """
    if timestamp is None:
        timestamp = time.time()
    
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


def calculate_statistics(values: List[float]) -> Dict[str, float]:
    """
    计算统计指标
    
    Args:
        values: 数值列表
    
    Returns:
        统计字典
    """
    if not values:
        return {
            'count': 0,
            'mean': 0,
            'std': 0,
            'min': 0,
            'max': 0,
            'median': 0
        }
    
    n = len(values)
    mean = sum(values) / n
    
    if n > 1:
        variance = sum((x - mean) ** 2 for x in values) / n
        std = variance ** 0.5
    else:
        std = 0
    
    sorted_values = sorted(values)
    median = sorted_values[n // 2] if n % 2 == 1 else (sorted_values[n//2-1] + sorted_values[n//2]) / 2
    
    return {
        'count': n,
        'mean': mean,
        'std': std,
        'min': min(values),
        'max': max(values),
        'median': median
    }


def batch_process(items: List[Any], process_func: callable, 
                 batch_size: int = 10, delay: float = 1.0) -> List[Any]:
    """
    批量处理
    
    Args:
        items: 项目列表
        process_func: 处理函数
        batch_size: 批次大小
        delay: 批次间延迟
    
    Returns:
        结果列表
    """
    results = []
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i+batch_size]
        
        for item in batch:
            result = process_func(item)
            results.append(result)
        
        # 批次间延迟
        if i + batch_size < len(items):
            time.sleep(delay)
    
    return results


def retry_on_failure(func: callable, max_retries: int = 3, 
                    delay: float = 5.0, exceptions: tuple = (Exception,)) -> Any:
    """
    失败重试
    
    Args:
        func: 函数
        max_retries: 最大重试次数
        delay: 重试延迟
        exceptions: 异常类型
    
    Returns:
        函数结果
    """
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            return func()
        except exceptions as e:
            last_exception = e
            if attempt < max_retries - 1:
                time.sleep(delay)
    
    raise last_exception


def flatten_dict(d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
    """
    展平字典
    
    Args:
        d: 字典
        parent_key: 父键
        sep: 分隔符
    
    Returns:
        展平后的字典
    """
    items = []
    
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep).items())
        else:
            items.append((new_key, v))
    
    return dict(items)


def deep_merge(dict1: Dict, dict2: Dict) -> Dict:
    """
    深度合并字典
    
    Args:
        dict1: 字典1
        dict2: 字典2
    
    Returns:
        合并后的字典
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result
