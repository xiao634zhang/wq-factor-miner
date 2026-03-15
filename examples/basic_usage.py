"""
WorldQuant Brain因子挖掘完整示例
"""

import sys
sys.path.append('..')

from api.wq_client import WQClient
from core.factor_generator import FactorGenerator
from core.backtest_engine import BacktestEngine


def main():
    """主函数"""
    
    print("="*70)
    print("🦞 WorldQuant Brain 因子挖掘系统")
    print("="*70)
    
    # 1. 初始化客户端
    print("\n步骤1: 初始化WorldQuant客户端...")
    try:
        client = WQClient.from_config("../config.yaml")
        print("✅ 客户端初始化成功")
    except Exception as e:
        print(f"❌ 客户端初始化失败: {e}")
        print("请检查config.yaml中的用户名和密码")
        return
    
    # 2. 初始化因子生成器
    print("\n步骤2: 初始化因子生成器...")
    generator = FactorGenerator()
    
    # 3. 生成因子
    print("\n步骤3: 生成因子...")
    
    # 方式1: 使用预定义模板
    momentum_factors = generator.momentum_factors(windows=[5, 10, 20])
    print(f"   动量因子: {len(momentum_factors)} 个")
    
    value_factors = generator.value_factors()
    print(f"   价值因子: {len(value_factors)} 个")
    
    quality_factors = generator.quality_factors()
    print(f"   质量因子: {len(quality_factors)} 个")
    
    technical_factors = generator.technical_factors(windows=[10, 20])
    print(f"   技术因子: {len(technical_factors)} 个")
    
    # 合并所有因子
    all_factors = momentum_factors + value_factors + quality_factors + technical_factors
    print(f"\n   总计: {len(all_factors)} 个因子")
    
    # 4. 初始化回测引擎
    print("\n步骤4: 初始化回测引擎...")
    engine = BacktestEngine(client)
    
    # 5. 执行回测（示例：只回测前3个因子）
    print("\n步骤5: 执行回测...")
    test_factors = all_factors[:3]  # 只测试前3个
    
    results = engine.batch_backtest(
        formulas=test_factors,
        max_concurrent=2,
        save_progress=True
    )
    
    # 6. 分析结果
    print("\n步骤6: 分析结果...")
    print("\n" + "="*70)
    print("回测结果汇总")
    print("="*70)
    
    for i, result in enumerate(results, 1):
        if result.get("success"):
            print(f"\n{i}. {result['formula'][:50]}...")
            print(f"   Sharpe Ratio: {result['sharpe_ratio']:.2f}")
            print(f"   Fitness: {result['fitness']:.2f}")
            print(f"   Turnover: {result['turnover']:.2%}")
            print(f"   满足提交标准: {'✅ 是' if result['meets_criteria'] else '❌ 否'}")
        else:
            print(f"\n{i}. {result['formula'][:50]}... - ❌ 失败")
    
    # 7. 筛选有效因子
    print("\n" + "="*70)
    print("有效因子（满足提交标准）")
    print("="*70)
    
    valid_factors = [r for r in results if r.get("meets_criteria")]
    
    if valid_factors:
        for i, factor in enumerate(valid_factors, 1):
            print(f"\n{i}. {factor['formula']}")
            print(f"   Sharpe: {factor['sharpe_ratio']:.2f}, Fitness: {factor['fitness']:.2f}")
    else:
        print("\n暂无满足提交标准的因子")
    
    print("\n" + "="*70)
    print("完成！")
    print("="*70)


if __name__ == "__main__":
    main()