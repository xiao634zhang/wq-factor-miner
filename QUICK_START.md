# 🦞 WorldQuant Brain 因子挖掘 - 无脑使用指南

## 🚀 超简单3步使用

### 第1步：进入项目目录

```bash
cd /root/.openclaw/workspace/wq-factor-miner
```

### 第2步：运行一键脚本

```bash
python3 auto_mine_factors.py
```

### 第3步：等待结果

脚本会自动：
1. ✅ 连接WorldQuant Brain
2. ✅ 生成100+个因子
3. ✅ 回测前10个因子
4. ✅ 分析结果
5. ✅ 生成报告

**就这么简单！**

---

## 📊 运行后会生成什么？

### 1. 分析报告
```
factor_report_20260315_164000.txt
```
包含：
- 总因子数、成功数、有效数
- Top 5最佳因子
- 统计指标

### 2. 因子列表
```
all_factors_20260315_164000.txt
```
包含：
- 所有生成的因子公式
- 可以直接复制使用

---

## ⚙️ 高级用法

### 回测更多因子

编辑 `auto_mine_factors.py`，找到这一行：

```python
test_factors = all_factors[:10]  # 改成 [:20] 或 [:50]
```

### 只测试特定类型因子

```python
# 只测试动量因子
test_factors = generator.momentum_factors(windows=[5, 10, 20])
```

### 自定义因子

```python
# 直接回测你想要的因子
my_factors = [
    "rank(ts_delta(close, 5))",
    "rank(ts_delta(close, 10))",
    "-rank(cap / earnings)"
]
results = engine.batch_backtest(my_factors, max_concurrent=1)
```

---

## 🎯 完整示例代码

### 示例1：最简单的回测

```python
from api.wq_client import WQClient
from core.backtest_engine import BacktestEngine

# 初始化
client = WQClient.from_config("config.yaml")
engine = BacktestEngine(client)

# 回测一个因子
result = engine.run_backtest("rank(ts_delta(close, 20))")

# 查看结果
print(f"Fitness: {result['fitness']:.4f}")
print(f"Sharpe: {result['sharpe_ratio']:.2f}")
```

### 示例2：批量生成和回测

```python
from api.wq_client import WQClient
from core.factor_generator import FactorGenerator
from core.backtest_engine import BacktestEngine

# 初始化
client = WQClient.from_config("config.yaml")
engine = BacktestEngine(client)
generator = FactorGenerator()

# 生成因子
factors = generator.momentum_factors(windows=[5, 10, 20])

# 批量回测
results = engine.batch_backtest(factors, max_concurrent=1)

# 查看结果
for r in results:
    if r['success']:
        print(f"{r['formula']}: Sharpe={r['sharpe_ratio']:.2f}")
```

### 示例3：使用模板引擎

```python
from generators.template_engine import TemplateEngine

engine = TemplateEngine()

# 生成动量因子
momentum = engine.generate_from_category("momentum")
print(f"生成了 {len(momentum)} 个动量因子")

# 自定义模板
engine.add_template(
    category="custom",
    name="my_factor",
    template="rank(ts_delta({field}, {window}))",
    params={"field": ["close", "volume"], "window": [10, 20]}
)

custom = engine.generate_from_category("custom")
print(f"生成了 {len(custom)} 个自定义因子")
```

---

## ⚠️ 重要提示

### API速率限制

WorldQuant Brain有严格的速率限制：

- ❌ 不要快速连续回测
- ✅ 每次回测间隔30秒以上
- ✅ 使用 `max_concurrent=1`

### 提交标准

有效因子需要满足：

| 指标 | 要求 |
|------|------|
| Fitness | ≥ 1.0 |
| Sharpe Ratio | ≥ 1.25 |
| Turnover | 1% - 70% |

---

## 🆘 常见问题

### Q: 提示"429 Too Many Requests"怎么办？

**A**: API速率限制，等待1-2分钟后再试。

### Q: 回测结果都是0怎么办？

**A**: 正常现象，说明这个因子已经被很多人用过了，需要挖掘新因子。

### Q: 如何找到有效因子？

**A**: 
1. 多生成一些因子
2. 使用遗传规划自动挖掘
3. 尝试不同的参数组合

### Q: 可以加快回测速度吗？

**A**: 不建议，会触发API限制。耐心等待是最佳策略。

---

## 📚 更多资源

- **GitHub仓库**: https://github.com/xiao634zhang/wq-factor-miner
- **详细文档**: README.md
- **示例代码**: examples/

---

## 🎉 开始使用

```bash
cd /root/.openclaw/workspace/wq-factor-miner
python3 auto_mine_factors.py
```

**就这么简单！**

---

**Created by Claw AI** 🦞
