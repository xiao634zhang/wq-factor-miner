"""
WorldQuant操作符管理
"""

import json
from typing import Dict, List, Optional
from pathlib import Path


class WQOperators:
    """WorldQuant操作符管理"""
    
    def __init__(self, operators_file: str = None):
        """
        初始化操作符管理器
        
        Args:
            operators_file: 操作符JSON文件路径
        """
        self.operators = {}
        self.categories = {}
        
        if operators_file:
            self.load_from_file(operators_file)
        else:
            self._load_default_operators()
    
    def load_from_file(self, filepath: str):
        """从文件加载操作符"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, dict) and 'operators' in data:
            operators_list = data['operators']
        else:
            operators_list = data
        
        for op in operators_list:
            if isinstance(op, dict):
                name = op.get('name')
                if name:
                    self.operators[name] = op
                    
                    # 分类
                    category = op.get('category', 'Unknown')
                    if category not in self.categories:
                        self.categories[category] = []
                    self.categories[category].append(name)
    
    def _load_default_operators(self):
        """加载默认操作符"""
        default_operators = [
            # Arithmetic
            {"name": "add", "category": "Arithmetic", "definition": "add(x, y, filter=false)", 
             "description": "Add all inputs (at least 2 inputs required)"},
            {"name": "subtract", "category": "Arithmetic", "definition": "subtract(x, y, filter=false)", 
             "description": "x - y"},
            {"name": "multiply", "category": "Arithmetic", "definition": "multiply(x, y, filter=false)", 
             "description": "Multiply all inputs"},
            {"name": "divide", "category": "Arithmetic", "definition": "divide(x, y)", 
             "description": "x / y"},
            {"name": "abs", "category": "Arithmetic", "definition": "abs(x)", 
             "description": "Absolute value of x"},
            {"name": "log", "category": "Arithmetic", "definition": "log(x)", 
             "description": "Natural logarithm"},
            {"name": "sqrt", "category": "Arithmetic", "definition": "sqrt(x)", 
             "description": "Square root of x"},
            {"name": "power", "category": "Arithmetic", "definition": "power(x, y)", 
             "description": "x ^ y"},
            {"name": "sign", "category": "Arithmetic", "definition": "sign(x)", 
             "description": "Sign of x (-1, 0, or 1)"},
            {"name": "inverse", "category": "Arithmetic", "definition": "inverse(x)", 
             "description": "1 / x"},
            {"name": "reverse", "category": "Arithmetic", "definition": "reverse(x)", 
             "description": "-x"},
            {"name": "min", "category": "Arithmetic", "definition": "min(x, y, ...)", 
             "description": "Minimum value"},
            {"name": "max", "category": "Arithmetic", "definition": "max(x, y, ...)", 
             "description": "Maximum value"},
            
            # Time Series
            {"name": "ts_mean", "category": "Time Series", "definition": "ts_mean(x, d)", 
             "description": "Mean of x for the past d days"},
            {"name": "ts_std_dev", "category": "Time Series", "definition": "ts_std_dev(x, d)", 
             "description": "Standard deviation of x for the past d days"},
            {"name": "ts_sum", "category": "Time Series", "definition": "ts_sum(x, d)", 
             "description": "Sum of x for the past d days"},
            {"name": "ts_max", "category": "Time Series", "definition": "ts_max(x, d)", 
             "description": "Maximum of x for the past d days"},
            {"name": "ts_min", "category": "Time Series", "definition": "ts_min(x, d)", 
             "description": "Minimum of x for the past d days"},
            {"name": "ts_rank", "category": "Time Series", "definition": "ts_rank(x, d)", 
             "description": "Rank of x over past d days"},
            {"name": "ts_delta", "category": "Time Series", "definition": "ts_delta(x, d)", 
             "description": "x - ts_delay(x, d)"},
            {"name": "ts_delay", "category": "Time Series", "definition": "ts_delay(x, d)", 
             "description": "Value of x d days ago"},
            {"name": "ts_corr", "category": "Time Series", "definition": "ts_corr(x, y, d)", 
             "description": "Correlation of x and y for the past d days"},
            {"name": "ts_covariance", "category": "Time Series", "definition": "ts_covariance(y, x, d)", 
             "description": "Covariance of y and x for the past d days"},
            {"name": "ts_zscore", "category": "Time Series", "definition": "ts_zscore(x, d)", 
             "description": "Z-score of x for the past d days"},
            {"name": "ts_decay_linear", "category": "Time Series", "definition": "ts_decay_linear(x, d)", 
             "description": "Linear decay of x for the past d days"},
            {"name": "ts_arg_max", "category": "Time Series", "definition": "ts_arg_max(x, d)", 
             "description": "Index of max value over past d days"},
            {"name": "ts_arg_min", "category": "Time Series", "definition": "ts_arg_min(x, d)", 
             "description": "Index of min value over past d days"},
            {"name": "ts_regression", "category": "Time Series", "definition": "ts_regression(y, x, d, lag=0, rettype=0)", 
             "description": "Time series regression"},
            {"name": "ts_scale", "category": "Time Series", "definition": "ts_scale(x, d, constant=0)", 
             "description": "Scale x over past d days"},
            {"name": "ts_product", "category": "Time Series", "definition": "ts_product(x, d)", 
             "description": "Product of x for the past d days"},
            {"name": "ts_quantile", "category": "Time Series", "definition": "ts_quantile(x, d, driver='gaussian')", 
             "description": "Quantile of x over past d days"},
            {"name": "ts_av_diff", "category": "Time Series", "definition": "ts_av_diff(x, d)", 
             "description": "x - ts_mean(x, d)"},
            
            # Cross Sectional
            {"name": "rank", "category": "Cross Sectional", "definition": "rank(x, rate=2)", 
             "description": "Rank x among all instruments (0 to 1)"},
            {"name": "zscore", "category": "Cross Sectional", "definition": "zscore(x)", 
             "description": "Z-score of x across all instruments"},
            {"name": "scale", "category": "Cross Sectional", "definition": "scale(x, scale=1, longscale=1, shortscale=1)", 
             "description": "Scale x to target booksize"},
            {"name": "normalize", "category": "Cross Sectional", "definition": "normalize(x, useStd=false, limit=0.0)", 
             "description": "Normalize x by subtracting mean"},
            {"name": "quantile", "category": "Cross Sectional", "definition": "quantile(x, driver='gaussian', sigma=1.0)", 
             "description": "Quantile transformation"},
            {"name": "winsorize", "category": "Cross Sectional", "definition": "winsorize(x, std=4)", 
             "description": "Winsorize x to limit outliers"},
            
            # Group
            {"name": "group_rank", "category": "Group", "definition": "group_rank(x, group)", 
             "description": "Rank within group"},
            {"name": "group_neutralize", "category": "Group", "definition": "group_neutralize(x, group)", 
             "description": "Neutralize against group"},
            {"name": "group_zscore", "category": "Group", "definition": "group_zscore(x, group)", 
             "description": "Z-score within group"},
            {"name": "group_mean", "category": "Group", "definition": "group_mean(x, weight, group)", 
             "description": "Mean within group"},
            {"name": "group_scale", "category": "Group", "definition": "group_scale(x, group)", 
             "description": "Scale within group"},
            {"name": "group_backfill", "category": "Group", "definition": "group_backfill(x, group, d, std=4.0)", 
             "description": "Backfill missing values within group"},
            
            # Logical
            {"name": "if_else", "category": "Logical", "definition": "if_else(input1, input2, input3)", 
             "description": "If input1 then input2 else input3"},
            {"name": "and", "category": "Logical", "definition": "and(input1, input2)", 
             "description": "Logical AND"},
            {"name": "or", "category": "Logical", "definition": "or(input1, input2)", 
             "description": "Logical OR"},
            {"name": "not", "category": "Logical", "definition": "not(x)", 
             "description": "Logical NOT"},
            {"name": "greater", "category": "Logical", "definition": "input1 > input2", 
             "description": "Greater than"},
            {"name": "less", "category": "Logical", "definition": "input1 < input2", 
             "description": "Less than"},
            {"name": "equal", "category": "Logical", "definition": "input1 == input2", 
             "description": "Equal to"},
            {"name": "is_nan", "category": "Logical", "definition": "is_nan(input)", 
             "description": "Check if NaN"},
            
            # Transformational
            {"name": "bucket", "category": "Transformational", "definition": "bucket(rank(x), range='0, 1, 0.1')", 
             "description": "Convert to bucket indices"},
            {"name": "trade_when", "category": "Transformational", "definition": "trade_when(x, y, z)", 
             "description": "Trade only under condition"},
            
            # Vector
            {"name": "vec_sum", "category": "Vector", "definition": "vec_sum(x)", 
             "description": "Sum of vector field"},
            {"name": "vec_avg", "category": "Vector", "definition": "vec_avg(x)", 
             "description": "Average of vector field"},
        ]
        
        for op in default_operators:
            name = op['name']
            self.operators[name] = op
            
            category = op['category']
            if category not in self.categories:
                self.categories[category] = []
            self.categories[category].append(name)
    
    def get_operator(self, name: str) -> Optional[Dict]:
        """获取操作符信息"""
        return self.operators.get(name)
    
    def get_operators_by_category(self, category: str) -> List[str]:
        """获取某类别的所有操作符"""
        return self.categories.get(category, [])
    
    def list_all_operators(self) -> List[str]:
        """列出所有操作符"""
        return list(self.operators.keys())
    
    def validate_operator(self, name: str) -> bool:
        """验证操作符是否存在"""
        return name in self.operators
    
    def get_operator_definition(self, name: str) -> Optional[str]:
        """获取操作符定义"""
        op = self.operators.get(name)
        return op.get('definition') if op else None
    
    def get_operator_description(self, name: str) -> Optional[str]:
        """获取操作符描述"""
        op = self.operators.get(name)
        return op.get('description') if op else None
    
    def search_operators(self, keyword: str) -> List[str]:
        """搜索操作符"""
        keyword = keyword.lower()
        results = []
        
        for name, op in self.operators.items():
            if keyword in name.lower():
                results.append(name)
            elif keyword in op.get('description', '').lower():
                results.append(name)
            elif keyword in op.get('category', '').lower():
                results.append(name)
        
        return results
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "operators": list(self.operators.values()),
            "categories": self.categories,
            "total_count": len(self.operators)
        }
    
    def save_to_file(self, filepath: str):
        """保存到文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)


# 全局实例
_operators_instance = None


def get_operators() -> WQOperators:
    """获取全局操作符实例"""
    global _operators_instance
    if _operators_instance is None:
        _operators_instance = WQOperators()
    return _operators_instance
