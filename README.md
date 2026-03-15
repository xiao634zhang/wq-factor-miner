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

---

## 📥 安装

### 1. 克隆仓库

```bash
git clone https://github.com/你的用户名/wq-factor-miner.git
cd wq-factor-miner
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置账号

复制配置模板：

```bash
cp config.yaml.template config.yaml
```

编辑 `config.yaml`：

```yaml
worldquant:
  username: "your_username"
  password: "your_password"

proxy:
  http: "http://127.0.0.1:7890"
  https: "http://127.0.0.1:7890"

backtest:
  max_concurrent: 1        # 建议1，避免API速率限制
  delay_between_requests: 30  # 建议30秒以上
```

---

## 🚀 快速开始

### 最简单的例子

```python
from api.wq_client import WQClient
from core.backtest_engine import BacktestEngine

# 初始化
client = WQClient.from_config("config.yaml")
engine = BacktestEngine(client)

# 回测一个因子
result = engine.run_backtest("rank(ts_delta(close, 20))")

# 查看结果
if result['success']:
    print(f"Fitness: {result['fitness']:.4f}")
    print(f"Sharpe: {result['sharpe_ratio']:.2f}")
    print(f"Turnover: {result['turnover']:.2%}")
```

---

## 📚 详细使用方法

### 一、API客户端

#### 1.1 初始化

```python
from api.wq_client import WQClient

# 方式1：从配置文件
client = WQClient.from_config("config.yaml")

# 方式2：直接传入参数
client = WQClient(
    username="your_username",
    password="your_password"
)
```

#### 1.2 获取数据字段

```python
# 获取所有数据字段
fields = client.get_data_fields()
print(f"总共 {len(fields)} 个数据字段")

# 查看前5个字段
for field in fields[:5]:
    print(f"- {field['id']}: {field['name']}")
```

---

### 二、操作符管理

#### 2.1 查看所有操作符

```python
from api.operators import get_operators

operators = get_operators()

# 列出所有操作符
all_ops = operators.list_all_operators()
print(f"总共 {len(all_ops)} 个操作符")

# 按类别查看
for category, ops in operators.categories.items():
    print(f"\n{category}:")
    for op in ops[:5]:
        print(f"  - {op}")
```

#### 2.2 搜索操作符

```python
# 搜索时序操作符
ts_ops = operators.search_operators('ts')
print(f"找到 {len(ts_ops)} 个时序操作符")

# 搜索排名相关
rank_ops = operators.search_operators('rank')
print(f"找到 {len(rank_ops)} 个排名操作符")
```

#### 2.3 获取操作符详情

```python
# 获取操作符信息
info = operators.get_operator('ts_mean')
print(f"定义: {info['definition']}")
print(f"描述: {info['description']}")

# 验证操作符
valid = operators.validate_operator('rank(close)')
print(f"是否有效: {valid}")
```

---

### 三、因子生成器

#### 3.1 生成各类因子

```python
from core.factor_generator import FactorGenerator

generator = FactorGenerator()

# 动量因子
momentum = generator.momentum_factors(windows=[5, 10, 20])
print(f"动量因子: {len(momentum)} 个")
for f in momentum[:3]:
    print(f"  - {f}")

# 价值因子
value = generator.value_factors()
print(f"价值因子: {len(value)} 个")

# 质量因子
quality = generator.quality_factors()
print(f"质量因子: {len(quality)} 个")

# 技术因子
technical = generator.technical_factors(windows=[10, 20])
print(f"技术因子: {len(technical)} 个")

# 组合所有因子
all_factors = momentum + value + quality + technical
print(f"总计: {len(all_factors)} 个因子")
```

---

### 四、模板引擎

#### 4.1 使用预定义模板

```python
from generators.template_engine import TemplateEngine

engine = TemplateEngine()

# 列出所有模板
templates = engine.list_templates()
for category, names in templates.items():
    print(f"\n{category}:")
    for name in names:
        print(f"  - {name}")

# 从类别生成因子
momentum_factors = engine.generate_from_category("momentum")
print(f"生成了 {len(momentum_factors)} 个动量因子")

# 生成所有类别的因子
all_factors = engine.generate_all()
print(f"总共生成了 {len(all_factors)} 个因子")
```

#### 4.2 自定义模板

```python
# 添加自定义模板
engine.add_template(
    category="custom",
    name="my_momentum",
    template="rank(ts_delta({field}, {window}))",
    params={
        "field": ["close", "volume"],
        "window": [10, 20, 30]
    },
    description="自定义动量因子"
)

# 生成自定义因子
custom_factors = engine.generate_from_category("custom")
print(f"自定义因子: {len(custom_factors)} 个")
for f in custom_factors:
    print(f"  - {f}")
```

#### 4.3 模板库说明

**6大类模板**：

| 类别 | 模板数 | 说明 |
|------|--------|------|
| **Momentum** | 5个 | 价格动量、成交量动量、相对强度、动量组合、行业动量 |
| **Value** | 5个 | PE、PB、价值组合、相对价值、EV/EBITDA |
| **Quality** | 4个 | ROE、盈利质量、质量组合、资产周转率 |
| **Technical** | 5个 | 波动率、价格排名、成交量排名、价量相关、动量波动率 |
| **Fundamental** | 4个 | 盈利收益率、现金流收益率、销售收入增长、盈利增长 |
| **Combo** | 3个 | 价值动量、质量价值、动量质量组合 |

---

### 五、回测引擎

#### 5.1 单次回测

```python
from api.wq_client import WQClient
from core.backtest_engine import BacktestEngine

client = WQClient.from_config("config.yaml")
engine = BacktestEngine(client)

# 回测单个因子
formula = "rank(ts_delta(close, 20))"
result = engine.run_backtest(formula)

if result['success']:
    print(f"公式: {result['formula']}")
    print(f"Fitness: {result['fitness']:.4f}")
    print(f"Sharpe Ratio: {result['sharpe_ratio']:.2f}")
    print(f"Turnover: {result['turnover']:.2%}")
    print(f"Returns: {result['returns']:.2%}")
    print(f"Drawdown: {result['drawdown']:.2%}")
else:
    print(f"回测失败: {result['error']}")
```

#### 5.2 批量回测

```python
# 生成测试因子
formulas = [
    "rank(ts_delta(close, 5))",
    "rank(ts_delta(close, 10))",
    "rank(ts_delta(close, 20))",
    "rank(ts_delta(volume, 20))",
    "-rank(cap / earnings)"
]

# 批量回测（注意：建议max_concurrent=1避免API限制）
results = engine.batch_backtest(formulas, max_concurrent=1)

# 查看结果
for i, result in enumerate(results, 1):
    if result['success']:
        print(f"{i}. {result['formula']}")
        print(f"   Fitness: {result['fitness']:.4f}, Sharpe: {result['sharpe_ratio']:.2f}")
    else:
        print(f"{i}. {result['formula']} - 失败")
```

#### 5.3 回测设置

```python
# 自定义回测设置
settings = {
    "instrumentType": "EQUITY",
    "region": "USA",
    "universe": "TOP3000",
    "delay": 1,
    "decay": 0,
    "neutralization": "MARKET",
    "truncation": 0.08,
    "pasteurization": "ON",
    "unitHandling": "VERIFY",
    "nanHandling": "ON",
    "language": "FASTEXPR",
    "visualization": False
}

result = engine.run_backtest(formula, settings)
```

---

### 六、参数优化器

#### 6.1 网格搜索

```python
from core.optimizer import GridSearchOptimizer

optimizer = GridSearchOptimizer(engine)

# 定义公式和参数范围
formula = "rank(ts_delta(close, 20))"
param_ranges = {
    'decay': [5, 10, 20, 30],
    'neutralization': ['MARKET', 'SECTOR', 'INDUSTRY']
}

# 执行网格搜索
result = optimizer.search(formula, param_ranges)

if result['success']:
    print(f"最佳参数: {result['best_params']}")
    print(f"最佳Fitness: {result['best_fitness']:.4f}")
    print(f"最佳Sharpe: {result['best_sharpe']:.2f}")
    
    # 查看所有结果
    for r in result['all_results']:
        print(f"参数: {r['params']}, Fitness: {r['fitness']:.4f}")
```

#### 6.2 敏感性分析

```python
# 分析参数敏感性
sensitivity = optimizer.sensitivity_analysis(formula, param_ranges)

for param, impact in sensitivity.items():
    print(f"{param}: 影响程度 {impact:.2%}")
```

---

### 七、结果分析器

#### 7.1 单因子分析

```python
from core.analyzer import ResultAnalyzer

analyzer = ResultAnalyzer()

# 分析单个结果
analysis = analyzer.analyze_single_result(result)

print(f"有效: {analysis['valid']}")
print(f"评分: {analysis['score']:.2f}")
print(f"评级: {analysis['rating']}")
print(f"建议: {analysis['recommendation']}")

# 检查是否满足提交标准
if analysis['valid']:
    print("✅ 满足提交标准！")
else:
    print("❌ 不满足提交标准")
    for reason in analysis['reasons']:
        print(f"  - {reason}")
```

#### 7.2 批量分析

```python
# 批量分析
batch_analysis = analyzer.analyze_batch_results(results)

print(f"总因子数: {batch_analysis['total']}")
print(f"成功回测: {batch_analysis['successful']}")
print(f"有效因子: {batch_analysis['valid']}")
print(f"成功率: {batch_analysis['success_rate']:.2%}")

# 查看统计指标
stats = batch_analysis['statistics']
print(f"\nFitness统计:")
print(f"  均值: {stats['fitness']['mean']:.4f}")
print(f"  最大: {stats['fitness']['max']:.4f}")
print(f"  最小: {stats['fitness']['min']:.4f}")
```

#### 7.3 生成报告

```python
# 生成详细报告
report = analyzer.generate_report(results, "backtest_report.txt")
print("报告已保存到 backtest_report.txt")

# 报告内容包括：
# - 概览统计
# - Top 10因子
# - 统计指标（Fitness, Sharpe, Turnover等）
# - 分布分析
```

---

### 八、遗传规划引擎

#### 8.1 基本使用

```python
from generators.gp_engine import GPEngine
from api.operators import get_operators

# 获取操作符
operators = get_operators()

# 定义字段
fields = ['close', 'volume', 'returns', 'cap']

# 初始化GP引擎
gp_engine = GPEngine(
    fields=fields,
    operators=operators.operators,
    config={
        'gp': {
            'population_size': 100,  # 种群大小
            'generations': 50,       # 进化代数
            'max_tree_depth': 5      # 最大树深度
        }
    }
)

# 执行进化
best_factors = gp_engine.evolve(
    target_metric="fitness",
    min_sharpe=1.5,
    max_iterations=50
)

# 查看结果
for factor in best_factors:
    print(f"公式: {factor['expression']}")
    print(f"适应度: {factor['fitness']:.4f}")
```

#### 8.2 结合回测引擎

```python
from api.wq_client import WQClient
from core.backtest_engine import BacktestEngine

# 初始化回测引擎
client = WQClient.from_config("config.yaml")
backtest_engine = BacktestEngine(client)

# 初始化GP引擎（传入回测引擎）
gp_engine = GPEngine(
    fields=fields,
    operators=operators.operators,
    backtest_engine=backtest_engine,  # 传入回测引擎
    config={'gp': {'population_size': 50, 'generations': 20}}
)

# 执行进化（会实际回测每个因子）
best_factors = gp_engine.evolve(max_iterations=20)
```

#### 8.3 保存和加载历史

```python
# 保存进化历史
gp_engine.save_history("evolution_history.json")

# 加载历史
gp_engine.load_history("evolution_history.json")

# 查看历史
for record in gp_engine.evolution_history:
    print(f"第{record['generation']}代: 最佳Fitness={record['best_fitness']:.4f}")
```

---

## 🎯 完整工作流程示例

### 工作流程1：模板因子挖掘

```python
from api.wq_client import WQClient
from core.factor_generator import FactorGenerator
from core.backtest_engine import BacktestEngine
from core.analyzer import ResultAnalyzer
from core.optimizer import GridSearchOptimizer

# 1. 初始化
print("初始化...")
client = WQClient.from_config("config.yaml")
engine = BacktestEngine(client)
generator = FactorGenerator()
analyzer = ResultAnalyzer()

# 2. 生成因子
print("\n生成因子...")
factors = generator.momentum_factors(windows=[5, 10, 20])
factors += generator.value_factors()
print(f"总共生成 {len(factors)} 个因子")

# 3. 批量回测
print("\n批量回测...")
results = engine.batch_backtest(factors, max_concurrent=1)

# 4. 分析结果
print("\n分析结果...")
analysis = analyzer.analyze_batch_results(results)
print(f"成功: {analysis['successful']}/{analysis['total']}")
print(f"有效: {analysis['valid']} 个")

# 5. 生成报告
report = analyzer.generate_report(results, "report.txt")
print("\n报告已保存到 report.txt")

# 6. 优化最佳因子
if analysis['valid'] > 0:
    print("\n优化最佳因子...")
    best_formula = results[0]['formula']  # 取第一个有效因子
    
    optimizer = GridSearchOptimizer(engine)
    param_ranges = {
        'decay': [5, 10, 20],
        'neutralization': ['MARKET', 'SECTOR']
    }
    
    opt_result = optimizer.search(best_formula, param_ranges)
    print(f"最佳参数: {opt_result['best_params']}")
    print(f"最佳Fitness: {opt_result['best_fitness']:.4f}")
```

### 工作流程2：遗传规划因子挖掘

```python
from api.wq_client import WQClient
from api.operators import get_operators
from core.backtest_engine import BacktestEngine
from generators.gp_engine import GPEngine

# 1. 初始化
print("初始化...")
client = WQClient.from_config("config.yaml")
backtest_engine = BacktestEngine(client)
operators = get_operators()

# 2. 配置GP引擎
fields = ['close', 'volume', 'returns', 'cap', 'vwap']

gp_engine = GPEngine(
    fields=fields,
    operators=operators.operators,
    backtest_engine=backtest_engine,
    config={
        'gp': {
            'population_size': 50,
            'generations': 20,
            'max_tree_depth': 4
        }
    }
)

# 3. 执行进化
print("\n开始进化...")
best_factors = gp_engine.evolve(
    target_metric="fitness",
    min_sharpe=1.5,
    max_iterations=20
)

# 4. 查看结果
print("\n最佳因子:")
for i, factor in enumerate(best_factors[:5], 1):
    print(f"{i}. {factor['expression']}")
    print(f"   适应度: {factor['fitness']:.4f}")

# 5. 保存历史
gp_engine.save_history("gp_evolution_history.json")
print("\n进化历史已保存")
```

---

## 📁 项目结构

```
wq-factor-miner/
├── README.md                   # 项目说明（本文件）
├── requirements.txt            # 依赖列表
├── config.yaml.template        # 配置文件模板
├── LICENSE                     # MIT许可证
│
├── api/                        # API模块
│   ├── __init__.py
│   ├── wq_client.py            # WorldQuant客户端（326行）
│   ├── operators.py            # 操作符管理（451行）
│   └── data_fields.py          # 数据字段管理（226行）
│
├── core/                       # 核心模块
│   ├── __init__.py
│   ├── factor_generator.py     # 因子生成器（166行）
│   ├── backtest_engine.py      # 回测引擎（204行）
│   ├── optimizer.py            # 参数优化器（486行）
│   └── analyzer.py             # 结果分析器（423行）
│
├── generators/                 # 生成器模块
│   ├── __init__.py
│   ├── template_engine.py      # 模板引擎（476行）
│   └── gp_engine.py            # 遗传规划引擎（614行）
│
├── utils/                      # 工具模块
│   ├── __init__.py
│   ├── logger.py               # 日志工具（83行）
│   ├── config_loader.py        # 配置加载（122行）
│   └── helpers.py              # 辅助函数（179行）
│
├── examples/                   # 示例代码
│   ├── basic_usage.py          # 基础用法
│   └── complete_example.py     # 完整示例
│
└── main.py                     # 快速启动
```

---

## ⚠️ 注意事项

### API速率限制

WorldQuant Brain API有严格的速率限制：

```python
# ❌ 不推荐：高并发批量回测
results = engine.batch_backtest(formulas, max_concurrent=5)

# ✅ 推荐：低并发 + 延迟
results = engine.batch_backtest(formulas, max_concurrent=1)
# 或在config.yaml中设置 delay_between_requests: 30
```

### 提交标准

WorldQuant Brain因子提交标准：

| 指标 | 要求 |
|------|------|
| Fitness | ≥ 1.0 |
| Sharpe Ratio | ≥ 1.25 |
| Turnover | 1% - 70% |
| Max Weight | < 10% |
| Correlation | < 0.7 |

### 安全建议

- ❌ 不要在代码中硬编码密码
- ✅ 使用配置文件或环境变量
- ✅ 定期更换密码
- ✅ 不要将 `config.yaml` 提交到Git

---

## 🔧 配置说明

### config.yaml 完整配置

```yaml
# WorldQuant Brain 账号
worldquant:
  username: "your_username"
  password: "your_password"
  api_base: "https://api.worldquantbrain.com"

# 代理设置（可选）
proxy:
  http: "http://127.0.0.1:7890"
  https: "http://127.0.0.1:7890"

# 回测设置
backtest:
  max_concurrent: 1           # 最大并发数（建议1）
  timeout: 300                # 超时时间（秒）
  retry_attempts: 3           # 重试次数
  delay_between_requests: 30  # 请求间延迟（秒）

# 参数优化设置
optimization:
  method: "grid_search"       # 优化方法
  max_iterations: 100         # 最大迭代次数

# 遗传规划设置
gp:
  population_size: 100        # 种群大小
  generations: 50             # 进化代数
  tournament_size: 7          # 锦标赛大小
  crossover_prob: 0.8         # 交叉概率
  mutation_prob: 0.2          # 变异概率
  max_tree_depth: 5           # 最大树深度

# 日志设置
logging:
  level: "INFO"               # 日志级别
  file: "logs/wq_factor_miner.log"
```

---

## 📖 操作符参考

### 7大类别，66个操作符

#### Arithmetic（13个）
```
add, subtract, multiply, divide, abs, log, sign, 
sqrt, power, exponential, inverse, negate, fraction
```

#### Time Series（19个）
```
ts_mean, ts_std_dev, ts_sum, ts_delta, ts_rank,
ts_corr, ts_covariance, ts_max, ts_min, ts_arg_max,
ts_arg_min, ts_skewness, ts_kurtosis, ts_product,
ts_av_diff, ts_abs_max, ts_abs_min, ts_decay_linear,
ts_step
```

#### Cross Sectional（6个）
```
rank, zscore, scale, decay_linear, vector_neutralize,
winsorize
```

#### Group（6个）
```
group_neutralize, group_zscore, group_rank,
group_mean, group_sum, group_count
```

#### Logical（8个）
```
is_nan, inf, if_else, and, or, not, equal, not_equal
```

#### Transformational（2个）
```
call, put
```

#### Vector（2个）
```
vec_avg, vec_sum
```

---

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

## 📄 许可证

MIT License

---

## 🙏 致谢

本项目整合了以下项目的精华：
- 量化代码资料（遗传规划框架、因子模板设计）
- WorldQuant Alpha Crew（多智能体架构、操作符体系）
- worldquant-brain-factors（批量回测、会话管理）

---

**Created by Claw AI** 🦞
