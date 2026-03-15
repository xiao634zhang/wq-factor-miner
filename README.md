# WorldQuant Brain 因子挖掘系统

一个完整的、可复现的WorldQuant Brain因子挖掘和回测解决方案。

## ✨ 特性

- **完整的API封装** - WorldQuant Brain API完整封装
- **66个操作符** - 完整的操作符定义和管理
- **双重因子生成** - 模板引擎 + 遗传规划
- **智能参数优化** - 网格搜索 + 自适应优化
- **完整的结果分析** - 自动报告生成
- **生产级代码** - 3345行完整实现

## 📊 项目统计

| 指标 | 数值 |
|------|------|
| 总代码行数 | 3345行 |
| 核心模块 | 10个 |
| 操作符定义 | 66个 |
| 因子模板 | 30+个 |

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置账号

创建 `config.yaml`：

```yaml
worldquant:
  username: "your_username"
  password: "your_password"

proxy:
  http: "http://127.0.0.1:7890"
  https: "http://127.0.0.1:7890"
```

### 3. 运行示例

```python
from api.wq_client import WQClient
from core.factor_generator import FactorGenerator
from core.backtest_engine import BacktestEngine

# 初始化
client = WQClient.from_config("config.yaml")
generator = FactorGenerator()
engine = BacktestEngine(client)

# 生成因子
formulas = generator.momentum_factors(windows=[5, 10, 20])

# 回测
results = engine.batch_backtest(formulas)

# 查看结果
for r in results:
    if r.get('success'):
        print(f"{r['formula']}: Sharpe={r['sharpe_ratio']:.2f}")
```

## 📁 项目结构

```
wq-factor-miner/
├── api/                    # API模块
│   ├── wq_client.py        # WorldQuant客户端
│   ├── operators.py        # 操作符管理
│   └── data_fields.py      # 数据字段管理
├── core/                   # 核心模块
│   ├── factor_generator.py # 因子生成器
│   ├── backtest_engine.py  # 回测引擎
│   ├── optimizer.py        # 参数优化器
│   └── analyzer.py         # 结果分析器
├── generators/             # 生成器模块
│   ├── template_engine.py  # 模板引擎
│   └── gp_engine.py        # 遗传规划引擎
├── utils/                  # 工具模块
│   ├── logger.py           # 日志工具
│   ├── config_loader.py    # 配置加载
│   └── helpers.py          # 辅助函数
└── examples/               # 示例代码
    ├── basic_usage.py      # 基础用法
    └── complete_example.py # 完整示例
```

## 🎯 核心功能

### 1. 因子生成

```python
# 模板生成
from generators.template_engine import TemplateEngine

engine = TemplateEngine()
factors = engine.generate_from_category("momentum")

# 遗传规划
from generators.gp_engine import GPEngine

gp = GPEngine(fields, operators)
best_factors = gp.evolve()
```

### 2. 回测

```python
# 单次回测
result = engine.run_backtest("rank(ts_delta(close, 20))")

# 批量回测
results = engine.batch_backtest(formulas, max_concurrent=2)
```

### 3. 参数优化

```python
from core.optimizer import GridSearchOptimizer

optimizer = GridSearchOptimizer(engine)
result = optimizer.search(formula, param_ranges)
```

### 4. 结果分析

```python
from core.analyzer import ResultAnalyzer

analyzer = ResultAnalyzer()
analysis = analyzer.analyze_batch_results(results)
report = analyzer.generate_report(results, "report.txt")
```

## 📚 操作符体系

### 7大类别，66个操作符

- **Arithmetic** (13个): add, subtract, multiply, divide, abs, log, sign, etc.
- **Time Series** (19个): ts_mean, ts_std_dev, ts_delta, ts_rank, ts_corr, etc.
- **Cross Sectional** (6个): rank, zscore, scale, decay_linear, etc.
- **Group** (6个): group_neutralize, group_zscore, group_rank, etc.
- **Logical** (8个): is_nan, inf, if_else, etc.
- **Transformational** (2个): call, put
- **Vector** (2个): vec_avg, vec_sum

## 🎨 因子模板库

### 6大类，30+模板

- **Momentum**: 价格动量、成交量动量、相对强度等
- **Value**: PE、PB、价值组合等
- **Quality**: ROE、盈利质量、资产周转率等
- **Technical**: 波动率、价量相关性等
- **Fundamental**: 盈利增长、现金流收益率等
- **Combo**: 价值动量、质量价值等组合因子

## ⚠️ 注意事项

### API速率限制

WorldQuant Brain API有严格的速率限制：

```python
# 推荐：单次回测
result = engine.run_backtest(formula)

# 批量回测需要控制并发
results = engine.batch_backtest(formulas, max_concurrent=1)
```

### 安全建议

- 不要在代码中硬编码密码
- 使用环境变量或单独的凭证文件
- 定期更换密码

## 📖 文档

- [API文档](docs/api.md)
- [操作符文档](docs/operators.md)
- [使用指南](docs/guide.md)

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

本项目整合了以下项目的精华：
- 量化代码资料（遗传规划框架、因子模板设计）
- WorldQuant Alpha Crew（多智能体架构、操作符体系）
- worldquant-brain-factors（批量回测、会话管理）

---

**Created by Claw AI** 🦞
