#!/usr/bin/env python3
"""
WorldQuant Brain因子挖掘快速启动脚本
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.wq_client import WQClient
from core.factor_generator import FactorGenerator, FACTOR_TEMPLATES
from core.backtest_engine import BacktestEngine


def quick_start():
    """快速开始"""
    
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║        🦞 WorldQuant Brain 因子挖掘系统 v1.0                      ║
║                                                                  ║
║        一个完整的、可复现的因子挖掘和回测解决方案                   ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    # 检查配置文件
    if not os.path.exists("config.yaml"):
        print("❌ 未找到config.yaml，请先配置:")
        print("   1. 复制 config.yaml 为 credentials.yaml")
        print("   2. 填入你的WorldQuant Brain用户名和密码")
        return
    
    print("✅ 找到配置文件")
    
    # 显示可用模板
    print("\n📊 可用因子模板:")
    print("-" * 50)
    
    for category, templates in FACTOR_TEMPLATES.items():
        print(f"\n{category.upper()}:")
        for name, template in templates.items():
            print(f"  - {name}: {template[:40]}...")
    
    print("\n" + "="*70)
    print("使用方法:")
    print("="*70)
    print("""
from api.wq_client import WQClient
from core.factor_generator import FactorGenerator
from core.backtest_engine import BacktestEngine

# 1. 初始化
client = WQClient.from_config("config.yaml")
generator = FactorGenerator()
engine = BacktestEngine(client)

# 2. 生成因子
formulas = generator.momentum_factors(windows=[5, 10, 20])

# 3. 回测
results = engine.batch_backtest(formulas)

# 4. 查看结果
for r in results:
    if r.get("success"):
        print(f"{r['formula']}: Sharpe={r['sharpe_ratio']:.2f}")
    """)


if __name__ == "__main__":
    quick_start()