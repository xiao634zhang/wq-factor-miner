"""
遗传规划因子挖掘引擎
"""

import random
import logging
import json
import time
from typing import Dict, List, Optional, Tuple, Callable
from copy import deepcopy
import re


class GPEngine:
    """遗传规划因子挖掘引擎"""
    
    def __init__(self, fields: List[str], operators: Dict,
                 config: Dict = None, backtest_engine=None):
        """
        初始化遗传规划引擎
        
        Args:
            fields: 数据字段列表
            operators: 操作符字典
            config: 配置字典
            backtest_engine: 回测引擎实例
        """
        self.fields = fields
        self.operators = operators
        self.config = config or {}
        self.backtest_engine = backtest_engine
        self.logger = logging.getLogger(__name__)
        
        # 遗传规划参数
        self.population_size = self.config.get('gp', {}).get('population_size', 100)
        self.generations = self.config.get('gp', {}).get('generations', 50)
        self.tournament_size = self.config.get('gp', {}).get('tournament_size', 7)
        self.crossover_prob = self.config.get('gp', {}).get('crossover_prob', 0.8)
        self.mutation_prob = self.config.get('gp', {}).get('mutation_prob', 0.2)
        self.max_tree_depth = self.config.get('gp', {}).get('max_tree_depth', 5)
        
        # 操作符分类
        self.unary_ops = []  # 一元操作符
        self.binary_ops = []  # 二元操作符
        self.ternary_ops = []  # 三元操作符
        
        self._classify_operators()
        
        # 进化历史
        self.evolution_history = []
    
    def _classify_operators(self):
        """分类操作符"""
        for op_name, op_info in self.operators.items():
            definition = op_info.get('definition', '')
            
            # 根据参数数量分类
            param_count = definition.count(',') + 1 if '(' in definition else 1
            
            if param_count == 1:
                self.unary_ops.append(op_name)
            elif param_count == 2:
                self.binary_ops.append(op_name)
            elif param_count >= 3:
                self.ternary_ops.append(op_name)
        
        self.logger.info(f"操作符分类: 一元={len(self.unary_ops)}, 二元={len(self.binary_ops)}, 三元={len(self.ternary_ops)}")
    
    def generate_random_tree(self, max_depth: int = None) -> str:
        """
        生成随机表达式树
        
        Args:
            max_depth: 最大深度
        
        Returns:
            表达式字符串
        """
        max_depth = max_depth or self.max_tree_depth
        
        if max_depth == 0 or random.random() < 0.3:
            # 终止节点：随机选择字段
            return random.choice(self.fields)
        
        # 随机选择操作符类型
        op_type = random.choice(['unary', 'binary', 'field'])
        
        if op_type == 'unary' and self.unary_ops:
            # 一元操作符
            op = random.choice(self.unary_ops)
            child = self.generate_random_tree(max_depth - 1)
            
            # 特殊处理时序操作符
            if op.startswith('ts_'):
                window = random.choice([5, 10, 20, 30, 60])
                return f"{op}({child}, {window})"
            else:
                return f"{op}({child})"
        
        elif op_type == 'binary' and self.binary_ops:
            # 二元操作符
            op = random.choice(self.binary_ops)
            left = self.generate_random_tree(max_depth - 1)
            right = self.generate_random_tree(max_depth - 1)
            
            # 特殊处理
            if op in ['ts_corr', 'ts_covariance']:
                window = random.choice([10, 20, 30])
                return f"{op}({left}, {right}, {window})"
            else:
                return f"{op}({left}, {right})"
        
        else:
            # 字段
            return random.choice(self.fields)
    
    def generate_population(self, size: int = None) -> List[str]:
        """
        生成初始种群
        
        Args:
            size: 种群大小
        
        Returns:
            表达式列表
        """
        size = size or self.population_size
        
        population = []
        for _ in range(size):
            expr = self.generate_random_tree()
            population.append(expr)
        
        self.logger.info(f"生成初始种群: {size} 个个体")
        return population
    
    def evaluate_fitness(self, formula: str) -> float:
        """
        评估适应度
        
        Args:
            formula: 因子公式
        
        Returns:
            适应度值
        """
        if not self.backtest_engine:
            # 如果没有回测引擎，使用启发式评估
            return self._heuristic_evaluate(formula)
        
        # 使用回测引擎评估
        try:
            result = self.backtest_engine.run_backtest(formula)
            
            if result.get('success'):
                # 综合评分
                fitness = result.get('fitness', 0)
                sharpe = result.get('sharpe_ratio', 0)
                
                # 适应度 = fitness * 0.6 + min(sharpe/2, 1) * 0.4
                score = fitness * 0.6 + min(sharpe / 2, 1) * 0.4
                return score
            else:
                return 0.0
        
        except Exception as e:
            self.logger.error(f"评估失败: {e}")
            return 0.0
    
    def _heuristic_evaluate(self, formula: str) -> float:
        """
        启发式评估（无回测引擎时使用）
        
        Args:
            formula: 因子公式
        
        Returns:
            启发式评分
        """
        score = 0.0
        
        # 检查公式复杂度
        depth = formula.count('(')
        if 2 <= depth <= 5:
            score += 0.3
        elif depth > 5:
            score -= 0.1
        
        # 检查操作符多样性
        ops_used = set()
        for op in self.operators.keys():
            if op in formula:
                ops_used.add(op)
        
        if len(ops_used) >= 2:
            score += 0.2
        if len(ops_used) >= 3:
            score += 0.2
        
        # 检查字段数量
        field_count = sum(1 for f in self.fields if f in formula)
        if field_count >= 2:
            score += 0.2
        if field_count >= 3:
            score += 0.1
        
        return min(score, 1.0)
    
    def tournament_selection(self, population: List[str], 
                            fitness_scores: List[float]) -> str:
        """
        锦标赛选择
        
        Args:
            population: 种群
            fitness_scores: 适应度分数
        
        Returns:
            选中的个体
        """
        tournament_indices = random.sample(
            range(len(population)), 
            min(self.tournament_size, len(population))
        )
        
        best_idx = max(tournament_indices, key=lambda i: fitness_scores[i])
        return population[best_idx]
    
    def crossover(self, parent1: str, parent2: str) -> Tuple[str, str]:
        """
        交叉操作
        
        Args:
            parent1: 父代1
            parent2: 父代2
        
        Returns:
            子代元组
        """
        # 简化的交叉：随机交换子表达式
        if random.random() > self.crossover_prob:
            return parent1, parent2
        
        # 提取子表达式
        parts1 = self._extract_parts(parent1)
        parts2 = self._extract_parts(parent2)
        
        if parts1 and parts2:
            # 随机交换
            idx1 = random.randint(0, len(parts1) - 1)
            idx2 = random.randint(0, len(parts2) - 1)
            
            child1 = parent1.replace(parts1[idx1], parts2[idx2], 1)
            child2 = parent2.replace(parts2[idx2], parts1[idx1], 1)
            
            return child1, child2
        
        return parent1, parent2
    
    def _extract_parts(self, formula: str) -> List[str]:
        """提取公式的子表达式"""
        parts = []
        
        # 提取括号内的内容
        stack = []
        start = -1
        
        for i, char in enumerate(formula):
            if char == '(':
                if not stack:
                    start = i
                stack.append(char)
            elif char == ')':
                if stack:
                    stack.pop()
                    if not stack and start >= 0:
                        parts.append(formula[start:i+1])
        
        # 提取字段
        for field in self.fields:
            if field in formula:
                parts.append(field)
        
        return list(set(parts))
    
    def mutate(self, individual: str) -> str:
        """
        变异操作
        
        Args:
            individual: 个体
        
        Returns:
            变异后的个体
        """
        if random.random() > self.mutation_prob:
            return individual
        
        # 随机选择变异类型
        mutation_type = random.choice(['replace_field', 'replace_op', 'add_op', 'remove_op'])
        
        if mutation_type == 'replace_field':
            # 替换字段
            for field in self.fields:
                if field in individual:
                    new_field = random.choice([f for f in self.fields if f != field])
                    return individual.replace(field, new_field, 1)
        
        elif mutation_type == 'replace_op':
            # 替换操作符
            for op in self.operators.keys():
                if op in individual:
                    # 选择同类操作符替换
                    if op in self.unary_ops:
                        new_op = random.choice([o for o in self.unary_ops if o != op])
                    elif op in self.binary_ops:
                        new_op = random.choice([o for o in self.binary_ops if o != op])
                    else:
                        new_op = op
                    
                    return individual.replace(op, new_op, 1)
        
        elif mutation_type == 'add_op':
            # 添加操作符
            op = random.choice(self.unary_ops)
            return f"{op}({individual})"
        
        elif mutation_type == 'remove_op':
            # 移除操作符（简化）
            parts = self._extract_parts(individual)
            if parts:
                # 选择一个子表达式替换为字段
                part_to_replace = random.choice(parts)
                field = random.choice(self.fields)
                return individual.replace(part_to_replace, field, 1)
        
        return individual
    
    def evolve(self, target_metric: str = "fitness", min_sharpe: float = 1.5,
               max_iterations: int = None, callback: Callable = None) -> List[Dict]:
        """
        执行进化
        
        Args:
            target_metric: 目标指标
            min_sharpe: 最小夏普比率
            max_iterations: 最大迭代次数
            callback: 回调函数
        
        Returns:
            最优因子列表
        """
        max_iterations = max_iterations or self.generations
        
        self.logger.info(f"开始进化，共 {max_iterations} 代")
        
        # 生成初始种群
        population = self.generate_population()
        
        best_individuals = []
        best_fitness = 0
        best_individual = None
        
        for gen in range(max_iterations):
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"第 {gen+1}/{max_iterations} 代")
            self.logger.info(f"{'='*60}")
            
            # 评估适应度
            fitness_scores = []
            for i, individual in enumerate(population):
                fitness = self.evaluate_fitness(individual)
                fitness_scores.append(fitness)
                
                self.logger.info(f"个体 {i+1}/{len(population)}: Fitness={fitness:.4f}")
                
                if callback:
                    callback(gen, max_iterations, i, len(population), individual, fitness)
            
            # 记录最佳个体
            gen_best_idx = max(range(len(fitness_scores)), key=lambda i: fitness_scores[i])
            gen_best_fitness = fitness_scores[gen_best_idx]
            gen_best_individual = population[gen_best_idx]
            
            if gen_best_fitness > best_fitness:
                best_fitness = gen_best_fitness
                best_individual = gen_best_individual
                self.logger.info(f"发现更好的个体: {gen_best_individual[:50]}... Fitness={gen_best_fitness:.4f}")
            
            # 记录历史
            self.evolution_history.append({
                'generation': gen + 1,
                'best_fitness': gen_best_fitness,
                'avg_fitness': sum(fitness_scores) / len(fitness_scores),
                'best_individual': gen_best_individual
            })
            
            # 选择、交叉、变异生成新一代
            new_population = []
            
            # 精英保留
            elite_count = max(1, len(population) // 10)
            elite_indices = sorted(range(len(fitness_scores)), 
                                  key=lambda i: fitness_scores[i], 
                                  reverse=True)[:elite_count]
            
            for idx in elite_indices:
                new_population.append(population[idx])
            
            # 生成新个体
            while len(new_population) < self.population_size:
                # 选择父代
                parent1 = self.tournament_selection(population, fitness_scores)
                parent2 = self.tournament_selection(population, fitness_scores)
                
                # 交叉
                child1, child2 = self.crossover(parent1, parent2)
                
                # 变异
                child1 = self.mutate(child1)
                child2 = self.mutate(child2)
                
                new_population.extend([child1, child2])
            
            # 保持种群大小
            population = new_population[:self.population_size]
        
        # 返回最优个体
        self.logger.info(f"\n进化完成！最佳适应度: {best_fitness:.4f}")
        self.logger.info(f"最佳个体: {best_individual}")
        
        return [{
            'expression': best_individual,
            'fitness': best_fitness,
            'history': self.evolution_history
        }]
    
    def save_history(self, filepath: str):
        """保存进化历史"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.evolution_history, f, indent=2, ensure_ascii=False)
    
    def load_history(self, filepath: str):
        """加载进化历史"""
        with open(filepath, 'r', encoding='utf-8') as f:
            self.evolution_history = json.load(f)
