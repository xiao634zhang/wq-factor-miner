"""
完整示例：模板因子生成和回测
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.wq_client import WQClient
from api.operators import get_operators
from api.data_fields import DataFieldsManager
from generators.template_engine import TemplateEngine
from core.factor_generator import FactorGenerator
from core.backtest_engine import BacktestEngine
from core.optimizer import GridSearchOptimizer
from core.analyzer import ResultAnalyzer


def example_template_generation():
    """示例：模板因子生成"""
    print("\n" + "="*70)
    print("示例1：模板因子生成")
    print("="*70)
    
    # 初始化模板引擎
    engine = TemplateEngine()
    
    # 列出所有模板
    print("\n可用模板类别:")
    templates = engine.list_templates()
    for category, names in templates.items():
        print(f"\n{category}:")
        for name in names:
            info = engine.get_template_info(category, name)
            print(f"  - {name}: {info['description']}")
    
    # 生成动量因子
    print("\n生成动量因子:")
    momentum_factors = engine.generate_from_category("momentum")
    for i, formula in enumerate(momentum_factors[:5], 1):
        print(f"{i}. {formula}")
    print(f"共 {len(momentum_factors)} 个动量因子")
    
    # 生成价值因子
    print("\n生成价值因子:")
    value_factors = engine.generate_from_category("value")
    for i, formula in enumerate(value_factors, 1):
        print(f"{i}. {formula}")
    
    # 自定义模板
    print("\n添加自定义模板:")
    engine.add_template(
        category="custom",
        name="my_momentum",
        template="rank(ts_delta({field}, {window}))",
        params={"field": ["close", "volume"], "window": [10, 20]},
        description="自定义动量因子"
    )
    
    custom_factors = engine.generate_from_category("custom")
    print(f"自定义因子: {custom_factors}")
    
    return engine


def example_factor_generation():
    """示例：因子生成器"""
    print("\n" + "="*70)
    print("示例2：因子生成器")
    print("="*70)
    
    # 初始化因子生成器
    generator = FactorGenerator()
    
    # 生成各类因子
    momentum = generator.momentum_factors(windows=[5, 10, 20])
    print(f"\n动量因子: {len(momentum)} 个")
    
    value = generator.value_factors()
    print(f"价值因子: {len(value)} 个")
    
    quality = generator.quality_factors()
    print(f"质量因子: {len(quality)} 个")
    
    technical = generator.technical_factors(windows=[10, 20])
    print(f"技术因子: {len(technical)} 个")
    
    # 合并所有因子
    all_factors = momentum + value + quality + technical
    print(f"\n总计: {len(all_factors)} 个因子")
    
    return generator, all_factors


def example_backtest():
    """示例：回测流程"""
    print("\n" + "="*70)
    print("示例3：回测流程（需要配置WorldQuant账号）")
    print("="*70)
    
    # 检查配置文件
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml")
    
    if not os.path.exists(config_path):
        print("\n❌ 未找到配置文件，请先创建config.yaml")
        print("示例配置:")
        print("""
worldquant:
  username: "your_username"
  password: "your_password"
        """)
        return None, None
    
    try:
        # 初始化客户端
        print("\n初始化WorldQuant客户端...")
        client = WQClient.from_config(config_path)
        print("✅ 客户端初始化成功")
        
        # 初始化回测引擎
        print("\n初始化回测引擎...")
        engine = BacktestEngine(client)
        print("✅ 回测引擎初始化成功")
        
        # 生成测试因子
        print("\n生成测试因子...")
        generator = FactorGenerator()
        test_factors = generator.momentum_factors(windows=[5, 10])[:3]
        print(f"测试因子: {len(test_factors)} 个")
        
        # 执行回测
        print("\n执行回测...")
        results = engine.batch_backtest(test_factors, max_concurrent=2)
        
        # 分析结果
        print("\n分析结果...")
        analyzer = ResultAnalyzer()
        analysis = analyzer.analyze_batch_results(results)
        
        print(f"\n总因子数: {analysis['total']}")
        print(f"成功回测: {analysis['successful']}")
        print(f"有效因子: {analysis['valid']}")
        
        # 生成报告
        report = analyzer.generate_report(results, "backtest_report.txt")
        print("\n报告已保存到: backtest_report.txt")
        
        return engine, results
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        return None, None


def example_optimization():
    """示例：参数优化"""
    print("\n" + "="*70)
    print("示例4：参数优化")
    print("="*70)
    
    # 检查配置
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml")
    
    if not os.path.exists(config_path):
        print("\n❌ 未找到配置文件，跳过优化示例")
        return None
    
    try:
        # 初始化
        client = WQClient.from_config(config_path)
        engine = BacktestEngine(client)
        optimizer = GridSearchOptimizer(engine)
        
        # 定义测试公式
        formula = "rank(ts_delta(close, 20))"
        
        # 定义参数范围
        param_ranges = {
            'decay': [10, 20, 30],
            'neutralization': ['MARKET', 'SECTOR']
        }
        
        print(f"\n测试公式: {formula}")
        print(f"参数范围: {param_ranges}")
        
        # 执行网格搜索
        print("\n执行网格搜索...")
        result = optimizer.search(formula, param_ranges)
        
        if result['success']:
            print(f"\n最佳参数: {result['best_params']}")
            print(f"最佳Fitness: {result['best_fitness']:.4f}")
        else:
            print("\n优化失败")
        
        return optimizer, result
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        return None


def example_operators():
    """示例：操作符管理"""
    print("\n" + "="*70)
    print("示例5：操作符管理")
    print("="*70)
    
    # 获取操作符实例
    operators = get_operators()
    
    # 列出所有操作符
    all_ops = operators.list_all_operators()
    print(f"\n总操作符数: {len(all_ops)}")
    
    # 按类别列出
    print("\n操作符分类:")
    for category, ops in operators.categories.items():
        print(f"\n{category} ({len(ops)} 个):")
        for op in ops[:5]:  # 只显示前5个
            desc = operators.get_operator_description(op)
            print(f"  - {op}: {desc[:40]}...")
    
    # 搜索操作符
    print("\n搜索 'rank' 相关操作符:")
    results = operators.search_operators('rank')
    for op in results:
        print(f"  - {op}")
    
    # 获取操作符详情
    print("\n操作符详情 - ts_mean:")
    op_info = operators.get_operator('ts_mean')
    if op_info:
        print(f"  定义: {op_info['definition']}")
        print(f"  描述: {op_info['description']}")
    
    return operators


def main():
    """主函数"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║        🦞 WorldQuant Brain 因子挖掘系统 - 完整示例                ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    # 示例1：模板因子生成
    template_engine = example_template_generation()
    
    # 示例2：因子生成器
    generator, all_factors = example_factor_generation()
    
    # 示例3：操作符管理
    operators = example_operators()
    
    # 示例4：回测流程（需要配置）
    engine, results = example_backtest()
    
    # 示例5：参数优化（需要配置）
    optimizer, opt_result = example_optimization()
    
    print("\n" + "="*70)
    print("所有示例执行完成！")
    print("="*70)


if __name__ == "__main__":
    main()
