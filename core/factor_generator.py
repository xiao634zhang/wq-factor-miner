"""
因子生成器
"""

from typing import List, Dict
import itertools


class FactorGenerator:
    """因子生成器"""
    
    def __init__(self):
        """初始化"""
        pass
    
    def from_template(self, template: str, params: Dict) -> List[str]:
        """
        基于模板生成因子
        
        Args:
            template: 因子模板，如 "rank(ts_delta(close, {window}))"
            params: 参数字典，如 {"window": [5, 10, 20]}
        
        Returns:
            公式列表
        """
        formulas = []
        
        # 获取所有参数组合
        keys = params.keys()
        values = params.values()
        
        for combination in itertools.product(*values):
            param_dict = dict(zip(keys, combination))
            formula = template.format(**param_dict)
            formulas.append(formula)
        
        return formulas
    
    def from_templates(self, templates: List[str], params_list: List[Dict]) -> List[str]:
        """
        基于多个模板生成因子
        
        Args:
            templates: 模板列表
            params_list: 参数列表
        
        Returns:
            公式列表
        """
        all_formulas = []
        
        for template, params in zip(templates, params_list):
            formulas = self.from_template(template, params)
            all_formulas.extend(formulas)
        
        return all_formulas
    
    def momentum_factors(self, windows: List[int] = [5, 10, 20, 60]) -> List[str]:
        """生成动量因子"""
        templates = [
            "rank(ts_delta(close, {window}))",
            "rank(ts_delta(volume, {window}))",
            "rank(close / ts_mean(close, {window}))",
            "group_neutralize(rank(ts_delta(close, {window})), industry)",
        ]
        
        params = {"window": windows}
        
        return self.from_templates(templates, [params] * len(templates))
    
    def value_factors(self) -> List[str]:
        """生成价值因子"""
        templates = [
            "-rank(cap / earnings)",
            "-rank(cap / book_value)",
            "-rank(cap / earnings) - rank(cap / book_value)",
            "group_zscore(-rank(cap / earnings), industry)",
        ]
        
        return templates
    
    def quality_factors(self) -> List[str]:
        """生成质量因子"""
        templates = [
            "rank(earnings / book_value)",
            "rank(operating_cash_flow / earnings)",
            "rank(earnings / book_value) + rank(operating_cash_flow / earnings)",
        ]
        
        return templates
    
    def technical_factors(self, windows: List[int] = [10, 20, 30]) -> List[str]:
        """生成技术因子"""
        formulas = []
        
        for w in windows:
            formulas.extend([
                f"rank(ts_delta(close, {w}))",
                f"rank(ts_delta(volume, {w}))",
                f"rank(ts_corr(close, volume, {w}))",
                f"rank(ts_std_dev(returns, {w}))",
                f"rank(ts_rank(close, {w}))",
            ])
        
        return formulas


# 预定义模板
FACTOR_TEMPLATES = {
    "momentum": {
        "price_momentum": "rank(ts_delta(close, {window}))",
        "volume_momentum": "rank(ts_delta(volume, {window}))",
        "relative_strength": "rank(close / ts_mean(close, {window}))",
        "sector_momentum": "group_neutralize(rank(ts_delta(close, {window})), industry)",
    },
    "value": {
        "pe_ratio": "-rank(cap / earnings)",
        "pb_ratio": "-rank(cap / book_value)",
        "value_combo": "-rank(cap / earnings) - rank(cap / book_value)",
    },
    "quality": {
        "roe": "rank(earnings / book_value)",
        "earnings_quality": "rank(operating_cash_flow / earnings)",
    },
    "technical": {
        "volatility": "rank(ts_std_dev(returns, {window}))",
        "price_rank": "rank(ts_rank(close, {window}))",
        "volume_rank": "rank(ts_rank(volume, {window}))",
    }
}
