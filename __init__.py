"""
WorldQuant Brain Factor Miner
"""

__version__ = "1.0.0"
__author__ = "Claw AI"

from api.wq_client import WQClient
from api.operators import WQOperators, get_operators
from api.data_fields import DataFieldsManager
from generators.template_engine import TemplateEngine
from generators.gp_engine import GPEngine
from core.factor_generator import FactorGenerator
from core.backtest_engine import BacktestEngine
from core.optimizer import GridSearchOptimizer
from core.analyzer import ResultAnalyzer

__all__ = [
    'WQClient',
    'WQOperators',
    'get_operators',
    'DataFieldsManager',
    'TemplateEngine',
    'GPEngine',
    'FactorGenerator',
    'BacktestEngine',
    'GridSearchOptimizer',
    'ResultAnalyzer'
]