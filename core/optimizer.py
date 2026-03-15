"""
参数优化器 - 网格搜索
"""

import itertools
import logging
import json
import time
from typing import Dict, List, Optional, Callable
from pathlib import Path


class GridSearchOptimizer:
    """网格搜索优化器"""
    
    def __init__(self, backtest_engine, config: Dict = None):
        """
        初始化网格搜索优化器
        
        Args:
            backtest_engine: 回测引擎实例
            config: 配置字典
        """
        self.engine = backtest_engine
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # 默认参数范围
        self.default_param_ranges = {
            'decay': [5, 10, 15, 20, 25, 30],
            'neutralization': ['MARKET', 'INDUSTRY', 'SECTOR', 'SUBINDUSTRY'],
            'truncation': [0.01, 0.05, 0.08, 0.10]
        }
        
        # 优化历史
        self.optimization_history = []
    
    def search(self, formula: str, param_ranges: Dict = None,
              base_settings: Dict = None, max_iterations: int = None,
              callback: Callable = None) -> Dict:
        """
        网格搜索最优参数
        
        Args:
            formula: 因子公式
            param_ranges: 参数范围字典
            base_settings: 基础设置
            max_iterations: 最大迭代次数
            callback: 回调函数
        
        Returns:
            优化结果
        """
        param_ranges = param_ranges or self.default_param_ranges
        base_settings = base_settings or self.engine.default_settings
        max_iterations = max_iterations or self.config.get('grid_search', {}).get('max_iterations', 50)
        
        self.logger.info(f"开始网格搜索: {formula}")
        self.logger.info(f"参数范围: {param_ranges}")
        
        # 生成所有参数组合
        keys = list(param_ranges.keys())
        values = list(param_ranges.values())
        combinations = list(itertools.product(*values))
        
        self.logger.info(f"总共有 {len(combinations)} 个参数组合")
        
        # 限制迭代次数
        if len(combinations) > max_iterations:
            self.logger.warning(f"参数组合数量 {len(combinations)} 超过最大迭代次数 {max_iterations}")
            combinations = combinations[:max_iterations]
        
        # 执行搜索
        results = []
        best_result = None
        best_params = None
        best_fitness = -float('inf')
        
        for i, combination in enumerate(combinations):
            # 构建参数字典
            params = dict(zip(keys, combination))
            
            # 更新设置
            settings = base_settings.copy()
            settings.update(params)
            
            self.logger.info(f"进度: {i+1}/{len(combinations)}, 参数: {params}")
            
            # 执行回测
            result = self.engine.run_backtest(formula, settings)
            
            if result.get('success'):
                fitness = result.get('fitness', 0)
                results.append({
                    'params': params,
                    'result': result,
                    'fitness': fitness
                })
                
                # 更新最佳结果
                if fitness > best_fitness:
                    best_fitness = fitness
                    best_result = result
                    best_params = params
                    self.logger.info(f"发现更好的参数: {params}, Fitness: {fitness:.4f}")
                
                # 回调
                if callback:
                    callback(i, len(combinations), params, result)
            
            # 避免请求过快
            time.sleep(2)
        
        # 保存历史
        optimization_record = {
            'formula': formula,
            'param_ranges': param_ranges,
            'total_combinations': len(combinations),
            'results': results,
            'best_params': best_params,
            'best_fitness': best_fitness,
            'best_result': best_result
        }
        self.optimization_history.append(optimization_record)
        
        # 返回结果
        return {
            'success': best_result is not None,
            'formula': formula,
            'best_params': best_params,
            'best_fitness': best_fitness,
            'best_result': best_result,
            'all_results': results,
            'total_tested': len(results)
        }
    
    def adaptive_search(self, formula: str, initial_ranges: Dict = None,
                       base_settings: Dict = None, iterations: int = 3,
                       improvement_threshold: float = 0.05) -> Dict:
        """
        自适应搜索 - 多轮优化
        
        Args:
            formula: 因子公式
            initial_ranges: 初始参数范围
            base_settings: 基础设置
            iterations: 迭代轮数
            improvement_threshold: 改进阈值
        
        Returns:
            优化结果
        """
        self.logger.info(f"开始自适应搜索，共 {iterations} 轮")
        
        current_ranges = initial_ranges or self.default_param_ranges.copy()
        best_overall = None
        all_rounds = []
        
        for round_num in range(1, iterations + 1):
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"第 {round_num}/{iterations} 轮搜索")
            self.logger.info(f"{'='*60}")
            
            # 执行当前轮次的网格搜索
            result = self.search(
                formula=formula,
                param_ranges=current_ranges,
                base_settings=base_settings
            )
            
            all_rounds.append({
                'round': round_num,
                'ranges': current_ranges.copy(),
                'result': result
            })
            
            # 更新最佳结果
            if result['success']:
                if best_overall is None or result['best_fitness'] > best_overall['best_fitness']:
                    best_overall = result
                    self.logger.info(f"更新最佳结果: Fitness={result['best_fitness']:.4f}")
            
            # 调整参数范围（缩小到最佳参数附近）
            if result['success'] and round_num < iterations:
                current_ranges = self._refine_ranges(
                    result['best_params'],
                    current_ranges
                )
                self.logger.info(f"调整参数范围: {current_ranges}")
        
        return {
            'success': best_overall is not None,
            'formula': formula,
            'best_params': best_overall['best_params'] if best_overall else None,
            'best_fitness': best_overall['best_fitness'] if best_overall else None,
            'best_result': best_overall['best_result'] if best_overall else None,
            'all_rounds': all_rounds,
            'total_rounds': iterations
        }
    
    def _refine_ranges(self, best_params: Dict, current_ranges: Dict) -> Dict:
        """调整参数范围（缩小到最佳参数附近）"""
        refined_ranges = {}
        
        for param, best_value in best_params.items():
            if param not in current_ranges:
                continue
            
            current_values = current_ranges[param]
            
            if isinstance(best_value, (int, float)):
                # 数值型参数：在最佳值附近生成新范围
                if isinstance(best_value, int):
                    # 整数参数
                    step = max(1, int((max(current_values) - min(current_values)) / 4))
                    new_values = list(range(
                        max(min(current_values), best_value - step * 2),
                        min(max(current_values), best_value + step * 2) + 1,
                        step
                    ))
                    if best_value not in new_values:
                        new_values.append(best_value)
                    new_values = sorted(new_values)
                else:
                    # 浮点数参数
                    span = max(current_values) - min(current_values)
                    step = span / 4
                    new_values = [
                        max(min(current_values), best_value - step),
                        best_value,
                        min(max(current_values), best_value + step)
                    ]
                    new_values = sorted(set(new_values))
                
                refined_ranges[param] = new_values
            
            elif isinstance(best_value, str):
                # 字符串参数：保持不变或缩小范围
                if len(current_values) > 2:
                    # 选择最佳值和相邻的值
                    idx = current_values.index(best_value)
                    new_values = [current_values[max(0, idx-1)], best_value]
                    if idx + 1 < len(current_values):
                        new_values.append(current_values[idx+1])
                    refined_ranges[param] = new_values
                else:
                    refined_ranges[param] = current_values
            
            else:
                refined_ranges[param] = current_values
        
        return refined_ranges
    
    def analyze_parameter_sensitivity(self, formula: str, param_name: str,
                                     param_values: List, base_settings: Dict = None) -> Dict:
        """
        参数敏感性分析
        
        Args:
            formula: 因子公式
            param_name: 参数名称
            param_values: 参数值列表
            base_settings: 基础设置
        
        Returns:
            敏感性分析结果
        """
        self.logger.info(f"分析参数 '{param_name}' 的敏感性")
        
        base_settings = base_settings or self.engine.default_settings.copy()
        
        results = []
        for value in param_values:
            settings = base_settings.copy()
            settings[param_name] = value
            
            result = self.engine.run_backtest(formula, settings)
            
            if result.get('success'):
                results.append({
                    'value': value,
                    'fitness': result.get('fitness', 0),
                    'sharpe': result.get('sharpe_ratio', 0),
                    'turnover': result.get('turnover', 0)
                })
            
            time.sleep(2)
        
        # 计算敏感性指标
        if results:
            fitness_values = [r['fitness'] for r in results]
            sharpe_values = [r['sharpe'] for r in results]
            
            sensitivity = {
                'param_name': param_name,
                'results': results,
                'fitness_range': [min(fitness_values), max(fitness_values)],
                'fitness_std': float(np.std(fitness_values)) if len(fitness_values) > 1 else 0,
                'sharpe_range': [min(sharpe_values), max(sharpe_values)],
                'best_value': results[np.argmax(fitness_values)]['value']
            }
        else:
            sensitivity = {
                'param_name': param_name,
                'results': [],
                'error': '所有回测均失败'
            }
        
        return sensitivity
    
    def get_optimization_history(self) -> List[Dict]:
        """获取优化历史"""
        return self.optimization_history
    
    def save_history(self, filepath: str):
        """保存优化历史"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.optimization_history, f, indent=2, ensure_ascii=False)
    
    def load_history(self, filepath: str):
        """加载优化历史"""
        with open(filepath, 'r', encoding='utf-8') as f:
            self.optimization_history = json.load(f)


# 需要numpy
try:
    import numpy as np
except ImportError:
    np = None
