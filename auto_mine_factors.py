#!/usr/bin/env python3
"""
一键因子挖掘脚本
用法：python auto_mine_factors.py
"""

import os
import sys
import time
from datetime import datetime

# 设置代理
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

from api.wq_client import WQClient
from core.factor_generator import FactorGenerator
from core.backtest_engine import BacktestEngine
from core.analyzer import ResultAnalyzer
from generators.template_engine import TemplateEngine


def print_banner():
    """打印横幅"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║        🦞 WorldQuant Brain 一键因子挖掘系统                       ║
║                                                                  ║
║        无脑运行，自动生成、回测、分析因子                          ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)


def create_config():
    """创建配置文件"""
    config_content = """worldquant:
  username: "yuanningzhang421@163.com"
  password: "XiaoZhang&771219"

proxy:
  http: "http://127.0.0.1:7890"
  https: "http://127.0.0.1:7890"

backtest:
  max_concurrent: 1
  timeout: 300
  retry_attempts: 3
  delay_between_requests: 30
"""
    
    with open("config.yaml", "w") as f:
        f.write(config_content)
    
    print("✅ 配置文件已创建")


def mine_factors():
    """主函数：一键挖掘因子"""
    print_banner()
    
    # 1. 创建配置文件
    print("\n" + "="*70)
    print("步骤1：创建配置文件")
    print("="*70)
    create_config()
    
    # 2. 初始化
    print("\n" + "="*70)
    print("步骤2：初始化系统")
    print("="*70)
    print("正在连接WorldQuant Brain...")
    
    try:
        client = WQClient.from_config("config.yaml")
        engine = BacktestEngine(client)
        generator = FactorGenerator()
        template_engine = TemplateEngine()
        analyzer = ResultAnalyzer()
        print("✅ 系统初始化成功")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return
    
    # 3. 生成因子
    print("\n" + "="*70)
    print("步骤3：生成因子")
    print("="*70)
    
    all_factors = []
    
    # 3.1 从模板生成
    print("\n从模板生成因子...")
    categories = ["momentum", "value", "quality", "technical"]
    
    for category in categories:
        factors = template_engine.generate_from_category(category)
        all_factors.extend(factors)
        print(f"  {category}: {len(factors)} 个")
    
    # 3.2 从生成器生成
    print("\n从生成器生成因子...")
    
    momentum = generator.momentum_factors(windows=[5, 10, 20])
    all_factors.extend(momentum)
    print(f"  动量因子: {len(momentum)} 个")
    
    value = generator.value_factors()
    all_factors.extend(value)
    print(f"  价值因子: {len(value)} 个")
    
    technical = generator.technical_factors(windows=[10, 20])
    all_factors.extend(technical)
    print(f"  技术因子: {len(technical)} 个")
    
    # 去重
    all_factors = list(set(all_factors))
    print(f"\n✅ 总共生成 {len(all_factors)} 个唯一因子")
    
    # 4. 批量回测
    print("\n" + "="*70)
    print("步骤4：批量回测因子")
    print("="*70)
    print(f"开始回测 {len(all_factors)} 个因子...")
    print("⚠️  注意：由于API速率限制，这可能需要较长时间")
    print("⚠️  建议：先测试前10个因子，确认系统正常后再全部回测")
    
    # 先测试前10个
    test_factors = all_factors[:10]
    print(f"\n先测试前 {len(test_factors)} 个因子...")
    
    results = []
    for i, formula in enumerate(test_factors, 1):
        print(f"\n[{i}/{len(test_factors)}] 回测: {formula}")
        
        try:
            result = engine.run_backtest(formula)
            results.append(result)
            
            if result.get('success'):
                fitness = result.get('fitness', 0)
                sharpe = result.get('sharpe_ratio', 0)
                print(f"  ✅ Fitness: {fitness:.4f}, Sharpe: {sharpe:.2f}")
            else:
                print(f"  ❌ 失败: {result.get('error', 'Unknown')}")
            
            # 延迟避免API限制
            if i < len(test_factors):
                print("  等待30秒...")
                time.sleep(30)
                
        except Exception as e:
            print(f"  ❌ 错误: {e}")
            results.append({'formula': formula, 'success': False, 'error': str(e)})
    
    # 5. 分析结果
    print("\n" + "="*70)
    print("步骤5：分析结果")
    print("="*70)
    
    analysis = analyzer.analyze_batch_results(results)
    
    print(f"\n总因子数: {analysis['total']}")
    print(f"成功回测: {analysis['successful']}")
    print(f"有效因子: {analysis['valid']}")
    print(f"成功率: {analysis['success_rate']:.2%}")
    
    # 6. 显示最佳因子
    print("\n" + "="*70)
    print("步骤6：最佳因子")
    print("="*70)
    
    valid_results = [r for r in results if r.get('success') and r.get('fitness', 0) > 0]
    
    if valid_results:
        # 按Fitness排序
        valid_results.sort(key=lambda x: x.get('fitness', 0), reverse=True)
        
        print(f"\nTop 5 因子（按Fitness排序）:")
        for i, r in enumerate(valid_results[:5], 1):
            print(f"\n{i}. {r['formula']}")
            print(f"   Fitness: {r.get('fitness', 0):.4f}")
            print(f"   Sharpe: {r.get('sharpe_ratio', 0):.2f}")
            print(f"   Turnover: {r.get('turnover', 0):.2%}")
    else:
        print("\n没有找到有效因子")
        print("💡 建议：")
        print("  1. 尝试更多因子")
        print("  2. 调整因子参数")
        print("  3. 使用遗传规划挖掘新因子")
    
    # 7. 生成报告
    print("\n" + "="*70)
    print("步骤7：生成报告")
    print("="*70)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"factor_report_{timestamp}.txt"
    
    analyzer.generate_report(results, report_file)
    print(f"✅ 报告已保存到: {report_file}")
    
    # 8. 保存因子列表
    print("\n" + "="*70)
    print("步骤8：保存因子")
    print("="*70)
    
    factors_file = f"all_factors_{timestamp}.txt"
    with open(factors_file, "w") as f:
        for factor in all_factors:
            f.write(factor + "\n")
    
    print(f"✅ 所有因子已保存到: {factors_file}")
    
    # 9. 完成
    print("\n" + "="*70)
    print("🎉 因子挖掘完成！")
    print("="*70)
    
    print(f"\n📊 统计:")
    print(f"  生成因子: {len(all_factors)} 个")
    print(f"  测试因子: {len(test_factors)} 个")
    print(f"  有效因子: {len(valid_results)} 个")
    
    print(f"\n📁 生成的文件:")
    print(f"  - {report_file} (分析报告)")
    print(f"  - {factors_file} (因子列表)")
    
    print(f"\n💡 下一步:")
    print(f"  1. 查看报告: cat {report_file}")
    print(f"  2. 继续回测更多因子")
    print(f"  3. 优化最佳因子")
    print(f"  4. 使用遗传规划挖掘新因子")
    
    # 清理配置文件
    if os.path.exists("config.yaml"):
        os.remove("config.yaml")
        print("\n✅ 配置文件已清理")


if __name__ == "__main__":
    try:
        mine_factors()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        # 清理配置文件
        if os.path.exists("config.yaml"):
            os.remove("config.yaml")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        # 清理配置文件
        if os.path.exists("config.yaml"):
            os.remove("config.yaml")
