"""
结果分析器
"""

import json
import logging
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime


class ResultAnalyzer:
    """结果分析器"""
    
    def __init__(self, config: Dict = None):
        """
        初始化结果分析器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # 提交标准
        self.criteria = self.config.get('submission_criteria', {
            'fitness': 1.0,
            'sharpe_ratio': 1.25,
            'turnover_min': 0.01,
            'turnover_max': 0.70,
            'max_weight': 0.10
        })
    
    def analyze_single_result(self, result: Dict) -> Dict:
        """
        分析单个回测结果
        
        Args:
            result: 回测结果
        
        Returns:
            分析结果
        """
        if not result.get('success'):
            return {
                'valid': False,
                'reason': result.get('error', 'Unknown error')
            }
        
        # 提取指标
        fitness = result.get('fitness', 0)
        sharpe = result.get('sharpe_ratio', 0)
        turnover = result.get('turnover', 0)
        returns = result.get('returns', 0)
        drawdown = result.get('drawdown', 0)
        margin = result.get('margin', 0)
        
        # 检查各项标准
        checks = {
            'fitness': fitness >= self.criteria['fitness'],
            'sharpe': sharpe >= self.criteria['sharpe_ratio'],
            'turnover_min': turnover >= self.criteria['turnover_min'],
            'turnover_max': turnover <= self.criteria['turnover_max']
        }
        
        all_passed = all(checks.values())
        
        # 计算评分
        score = self._calculate_score(result)
        
        # 生成评级
        rating = self._get_rating(score)
        
        # 生成建议
        recommendation = self._get_recommendation(checks, score)
        
        return {
            'valid': all_passed,
            'checks': checks,
            'score': score,
            'rating': rating,
            'recommendation': recommendation,
            'metrics': {
                'fitness': fitness,
                'sharpe_ratio': sharpe,
                'turnover': turnover,
                'returns': returns,
                'drawdown': drawdown,
                'margin': margin
            }
        }
    
    def analyze_batch_results(self, results: List[Dict]) -> Dict:
        """
        分析批量回测结果
        
        Args:
            results: 回测结果列表
        
        Returns:
            批量分析结果
        """
        total = len(results)
        successful = sum(1 for r in results if r.get('success'))
        valid = sum(1 for r in results if self.analyze_single_result(r).get('valid'))
        
        # 提取有效结果
        valid_results = [r for r in results if r.get('success')]
        
        if not valid_results:
            return {
                'total': total,
                'successful': successful,
                'valid': valid,
                'error': 'No valid results'
            }
        
        # 统计指标
        fitness_values = [r.get('fitness', 0) for r in valid_results]
        sharpe_values = [r.get('sharpe_ratio', 0) for r in valid_results]
        turnover_values = [r.get('turnover', 0) for r in valid_results]
        
        # 排序
        sorted_by_fitness = sorted(valid_results, key=lambda x: x.get('fitness', 0), reverse=True)
        sorted_by_sharpe = sorted(valid_results, key=lambda x: x.get('sharpe_ratio', 0), reverse=True)
        
        # Top 10
        top_10_fitness = sorted_by_fitness[:10]
        top_10_sharpe = sorted_by_sharpe[:10]
        
        return {
            'total': total,
            'successful': successful,
            'valid': valid,
            'success_rate': successful / total if total > 0 else 0,
            'valid_rate': valid / total if total > 0 else 0,
            'statistics': {
                'fitness': {
                    'mean': sum(fitness_values) / len(fitness_values),
                    'max': max(fitness_values),
                    'min': min(fitness_values),
                    'std': self._std(fitness_values)
                },
                'sharpe': {
                    'mean': sum(sharpe_values) / len(sharpe_values),
                    'max': max(sharpe_values),
                    'min': min(sharpe_values),
                    'std': self._std(sharpe_values)
                },
                'turnover': {
                    'mean': sum(turnover_values) / len(turnover_values),
                    'max': max(turnover_values),
                    'min': min(turnover_values),
                    'std': self._std(turnover_values)
                }
            },
            'top_10_by_fitness': [
                {
                    'formula': r.get('formula', ''),
                    'fitness': r.get('fitness', 0),
                    'sharpe': r.get('sharpe_ratio', 0)
                }
                for r in top_10_fitness
            ],
            'top_10_by_sharpe': [
                {
                    'formula': r.get('formula', ''),
                    'fitness': r.get('fitness', 0),
                    'sharpe': r.get('sharpe_ratio', 0)
                }
                for r in top_10_sharpe
            ]
        }
    
    def _calculate_score(self, result: Dict) -> float:
        """计算综合评分"""
        fitness = result.get('fitness', 0)
        sharpe = result.get('sharpe_ratio', 0)
        turnover = result.get('turnover', 0)
        
        # 加权评分
        score = (
            fitness * 40 +  # Fitness权重40%
            min(sharpe / 2, 1) * 40 +  # Sharpe权重40%
            (1 - abs(turnover - 0.35) / 0.35) * 20  # Turnover权重20%（最优值0.35）
        )
        
        return score
    
    def _get_rating(self, score: float) -> str:
        """获取评级"""
        if score >= 80:
            return "优秀"
        elif score >= 70:
            return "良好"
        elif score >= 60:
            return "合格"
        elif score >= 50:
            return "一般"
        else:
            return "较差"
    
    def _get_recommendation(self, checks: Dict, score: float) -> str:
        """生成建议"""
        failed = [k for k, v in checks.items() if not v]
        
        if not failed:
            if score >= 80:
                return "强烈推荐提交"
            else:
                return "可以提交"
        else:
            suggestions = []
            if 'fitness' in failed:
                suggestions.append("提高因子预测能力")
            if 'sharpe' in failed:
                suggestions.append("优化风险调整收益")
            if 'turnover_min' in failed:
                suggestions.append("增加换手率")
            if 'turnover_max' in failed:
                suggestions.append("降低换手率")
            
            return "需要改进: " + ", ".join(suggestions)
    
    def _std(self, values: List[float]) -> float:
        """计算标准差"""
        if len(values) < 2:
            return 0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def generate_report(self, results: List[Dict], output_file: str = None) -> str:
        """
        生成分析报告
        
        Args:
            results: 回测结果列表
            output_file: 输出文件路径
        
        Returns:
            报告文本
        """
        analysis = self.analyze_batch_results(results)
        
        report = []
        report.append("="*70)
        report.append("WorldQuant Brain 因子回测分析报告")
        report.append("="*70)
        report.append(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 概览
        report.append("\n" + "-"*70)
        report.append("一、概览")
        report.append("-"*70)
        report.append(f"总因子数: {analysis['total']}")
        report.append(f"成功回测: {analysis['successful']}")
        report.append(f"有效因子: {analysis['valid']}")
        report.append(f"成功率: {analysis['success_rate']:.2%}")
        report.append(f"有效率: {analysis['valid_rate']:.2%}")
        
        # 统计
        report.append("\n" + "-"*70)
        report.append("二、统计指标")
        report.append("-"*70)
        
        stats = analysis.get('statistics', {})
        
        report.append("\nFitness:")
        report.append(f"  均值: {stats['fitness']['mean']:.4f}")
        report.append(f"  最大: {stats['fitness']['max']:.4f}")
        report.append(f"  最小: {stats['fitness']['min']:.4f}")
        report.append(f"  标准差: {stats['fitness']['std']:.4f}")
        
        report.append("\nSharpe Ratio:")
        report.append(f"  均值: {stats['sharpe']['mean']:.4f}")
        report.append(f"  最大: {stats['sharpe']['max']:.4f}")
        report.append(f"  最小: {stats['sharpe']['min']:.4f}")
        report.append(f"  标准差: {stats['sharpe']['std']:.4f}")
        
        report.append("\nTurnover:")
        report.append(f"  均值: {stats['turnover']['mean']:.2%}")
        report.append(f"  最大: {stats['turnover']['max']:.2%}")
        report.append(f"  最小: {stats['turnover']['min']:.2%}")
        report.append(f"  标准差: {stats['turnover']['std']:.4f}")
        
        # Top 10
        report.append("\n" + "-"*70)
        report.append("三、Top 10 因子 (按Fitness)")
        report.append("-"*70)
        
        for i, r in enumerate(analysis.get('top_10_by_fitness', []), 1):
            report.append(f"\n{i}. {r['formula'][:60]}...")
            report.append(f"   Fitness: {r['fitness']:.4f}, Sharpe: {r['sharpe']:.2f}")
        
        # 保存报告
        report_text = "\n".join(report)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            self.logger.info(f"报告已保存到: {output_file}")
        
        return report_text
