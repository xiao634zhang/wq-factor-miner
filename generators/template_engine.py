"""
因子模板引擎
"""

import itertools
import logging
from typing import Dict, List, Optional
from string import Template


class TemplateEngine:
    """因子模板引擎"""
    
    def __init__(self, fields: List[str] = None):
        """
        初始化模板引擎
        
        Args:
            fields: 数据字段列表
        """
        self.fields = fields or []
        self.logger = logging.getLogger(__name__)
        
        # 预定义模板库
        self.templates = self._load_default_templates()
    
    def _load_default_templates(self) -> Dict[str, Dict]:
        """加载默认模板库"""
        return {
            # 动量因子模板
            "momentum": {
                "price_momentum": {
                    "template": "rank(ts_delta(close, {window}))",
                    "params": {"window": [5, 10, 20, 60]},
                    "description": "价格动量因子"
                },
                "volume_momentum": {
                    "template": "rank(ts_delta(volume, {window}))",
                    "params": {"window": [5, 10, 20, 60]},
                    "description": "成交量动量因子"
                },
                "relative_strength": {
                    "template": "rank(close / ts_mean(close, {window}))",
                    "params": {"window": [10, 20, 60]},
                    "description": "相对强度因子"
                },
                "momentum_combo": {
                    "template": "rank(ts_delta(close, {short_window})) * rank(ts_delta(volume, {long_window}))",
                    "params": {
                        "short_window": [5, 10],
                        "long_window": [20, 30]
                    },
                    "description": "动量组合因子"
                },
                "sector_momentum": {
                    "template": "group_neutralize(rank(ts_delta(close, {window})), industry)",
                    "params": {"window": [10, 20]},
                    "description": "行业动量因子"
                }
            },
            
            # 价值因子模板
            "value": {
                "pe_ratio": {
                    "template": "-rank(cap / earnings)",
                    "params": {},
                    "description": "市盈率因子"
                },
                "pb_ratio": {
                    "template": "-rank(cap / book_value)",
                    "params": {},
                    "description": "市净率因子"
                },
                "value_combo": {
                    "template": "-rank(cap / earnings) - rank(cap / book_value)",
                    "params": {},
                    "description": "价值组合因子"
                },
                "relative_value": {
                    "template": "group_zscore(-rank(cap / earnings), industry)",
                    "params": {},
                    "description": "相对价值因子"
                },
                "ev_ebitda": {
                    "template": "-rank(enterprise_value / ebitda)",
                    "params": {},
                    "description": "EV/EBITDA因子"
                }
            },
            
            # 质量因子模板
            "quality": {
                "roe": {
                    "template": "rank(earnings / book_value)",
                    "params": {},
                    "description": "ROE因子"
                },
                "earnings_quality": {
                    "template": "rank(operating_cash_flow / earnings)",
                    "params": {},
                    "description": "盈利质量因子"
                },
                "quality_combo": {
                    "template": "rank(earnings / book_value) + rank(operating_cash_flow / earnings)",
                    "params": {},
                    "description": "质量组合因子"
                },
                "asset_turnover": {
                    "template": "rank(sales / book_value)",
                    "params": {},
                    "description": "资产周转率因子"
                }
            },
            
            # 技术因子模板
            "technical": {
                "volatility": {
                    "template": "rank(ts_std_dev(returns, {window}))",
                    "params": {"window": [10, 20, 30]},
                    "description": "波动率因子"
                },
                "price_rank": {
                    "template": "rank(ts_rank(close, {window}))",
                    "params": {"window": [10, 20, 30]},
                    "description": "价格排名因子"
                },
                "volume_rank": {
                    "template": "rank(ts_rank(volume, {window}))",
                    "params": {"window": [10, 20, 30]},
                    "description": "成交量排名因子"
                },
                "price_volume_corr": {
                    "template": "rank(ts_corr(close, volume, {window}))",
                    "params": {"window": [10, 20, 30]},
                    "description": "价量相关因子"
                },
                "momentum_volatility": {
                    "template": "rank(ts_delta(close, {window})) / rank(ts_std_dev(returns, {window}))",
                    "params": {"window": [10, 20]},
                    "description": "动量波动率因子"
                }
            },
            
            # 基本面因子模板
            "fundamental": {
                "earnings_yield": {
                    "template": "rank(earnings / cap)",
                    "params": {},
                    "description": "盈利收益率因子"
                },
                "cash_flow_yield": {
                    "template": "rank(operating_cash_flow / cap)",
                    "params": {},
                    "description": "现金流收益率因子"
                },
                "sales_growth": {
                    "template": "rank(ts_delta(sales, {window}))",
                    "params": {"window": [60, 120]},
                    "description": "销售收入增长因子"
                },
                "earnings_growth": {
                    "template": "rank(ts_delta(earnings, {window}))",
                    "params": {"window": [60, 120]},
                    "description": "盈利增长因子"
                }
            },
            
            # 组合因子模板
            "combo": {
                "value_momentum": {
                    "template": "-rank(cap / earnings) + rank(ts_delta(close, {window}))",
                    "params": {"window": [20, 60]},
                    "description": "价值动量组合因子"
                },
                "quality_value": {
                    "template": "rank(earnings / book_value) - rank(cap / earnings)",
                    "params": {},
                    "description": "质量价值组合因子"
                },
                "momentum_quality": {
                    "template": "rank(ts_delta(close, {window})) * rank(earnings / book_value)",
                    "params": {"window": [20, 60]},
                    "description": "动量质量组合因子"
                }
            }
        }
    
    def generate_from_template(self, template: str, params: Dict) -> List[str]:
        """
        从模板生成因子
        
        Args:
            template: 模板字符串
            params: 参数字典
        
        Returns:
            公式列表
        """
        formulas = []
        
        if not params:
            # 无参数，直接返回模板
            return [template]
        
        # 获取所有参数组合
        keys = list(params.keys())
        values = list(params.values())
        
        for combination in itertools.product(*values):
            param_dict = dict(zip(keys, combination))
            
            try:
                formula = template.format(**param_dict)
                formulas.append(formula)
            except KeyError as e:
                self.logger.warning(f"模板参数错误: {e}")
        
        return formulas
    
    def generate_from_category(self, category: str) -> List[str]:
        """
        从类别生成所有因子
        
        Args:
            category: 类别名称
        
        Returns:
            公式列表
        """
        if category not in self.templates:
            self.logger.warning(f"未找到类别: {category}")
            return []
        
        formulas = []
        category_templates = self.templates[category]
        
        for name, template_info in category_templates.items():
            template = template_info['template']
            params = template_info.get('params', {})
            
            generated = self.generate_from_template(template, params)
            formulas.extend(generated)
        
        self.logger.info(f"从类别 '{category}' 生成了 {len(formulas)} 个因子")
        return formulas
    
    def generate_all(self) -> List[str]:
        """
        生成所有预定义因子
        
        Returns:
            公式列表
        """
        all_formulas = []
        
        for category in self.templates:
            formulas = self.generate_from_category(category)
            all_formulas.extend(formulas)
        
        self.logger.info(f"总共生成了 {len(all_formulas)} 个因子")
        return all_formulas
    
    def add_template(self, category: str, name: str, template: str, 
                    params: Dict = None, description: str = ""):
        """
        添加自定义模板
        
        Args:
            category: 类别名称
            name: 模板名称
            template: 模板字符串
            params: 参数字典
            description: 描述
        """
        if category not in self.templates:
            self.templates[category] = {}
        
        self.templates[category][name] = {
            "template": template,
            "params": params or {},
            "description": description
        }
        
        self.logger.info(f"添加模板: {category}.{name}")
    
    def list_templates(self) -> Dict[str, List[str]]:
        """
        列出所有模板
        
        Returns:
            模板字典
        """
        result = {}
        
        for category, templates in self.templates.items():
            result[category] = list(templates.keys())
        
        return result
    
    def get_template_info(self, category: str, name: str) -> Optional[Dict]:
        """
        获取模板信息
        
        Args:
            category: 类别名称
            name: 模板名称
        
        Returns:
            模板信息
        """
        if category not in self.templates:
            return None
        
        return self.templates[category].get(name)
    
    def validate_template(self, template: str) -> bool:
        """
        验证模板格式
        
        Args:
            template: 模板字符串
        
        Returns:
            是否有效
        """
        # 检查括号匹配
        stack = []
        for char in template:
            if char == '(':
                stack.append(char)
            elif char == ')':
                if not stack:
                    return False
                stack.pop()
        
        if stack:
            return False
        
        # 检查参数占位符
        try:
            # 尝试格式化（使用空参数）
            template.format(**{})
        except KeyError:
            # 有未填充的参数，这是正常的
            pass
        except Exception:
            return False
        
        return True
