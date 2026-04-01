# 02 数据字典（Data Dictionary）

## 1. 本模块解决的问题

这个模块解决的是：项目里到底有哪些字段（Fields），它们分别来自哪里，单位是什么，频率是什么，为什么值得纳入黄金研究。

## 2. 当前 `v0.1` 首批字段

| 字段名 | 中文含义 | 英文含义 | 来源 | 频率 | 单位 |
| --- | --- | --- | --- | --- | --- |
| `gold_close` | 黄金收盘价 | Gold Close | Alpha Vantage | 日频 | 美元/盎司 |
| `silver_close` | 白银收盘价 | Silver Close | Alpha Vantage | 日频 | 美元/盎司 |
| `yield_2y` | 美国 2 年期国债收益率 | 2Y Treasury Yield | FRED | 日频 | 百分比 |
| `yield_10y` | 美国 10 年期国债收益率 | 10Y Treasury Yield | FRED | 日频 | 百分比 |
| `real_yield_proxy` | 实际利率代理 | Real Yield Proxy | FRED | 日频 | 百分比 |
| `breakeven_proxy` | 盈亏平衡通胀代理 | Breakeven Inflation Proxy | FRED | 日频 | 百分比 |
| `usd_proxy` | 美元指数代理 | U.S. Dollar Proxy | FRED | 日频 | 指数 |
| `vix_proxy` | 波动率指数代理 | Volatility Proxy (VIX) | FRED | 日频 | 指数 |
| `equity_proxy` | 美股指数代理 | Equity Proxy (S&P 500) | FRED | 日频 | 指数 |
| `oil_close` | 原油价格 | Oil Close | FRED | 日频 | 美元/桶 |

## 3. 为什么这些字段与黄金有关

### `silver_close`

- 白银（Silver）和黄金同属贵金属（Precious Metals）
- 可作为商品板块内部相对关系的参考

### `yield_2y` 与 `yield_10y`

- 可反映利率环境（Rate Environment）
- 长短端利差（Yield Spread）有助于描述宏观预期

### `real_yield_proxy`

- 实际利率（Real Yield）常被认为是黄金的重要驱动因素之一

### `breakeven_proxy`

- 通胀预期（Inflation Expectations）会影响黄金的通胀对冲叙事（Inflation Hedge Narrative）

### `usd_proxy`

- 美元和黄金常表现为相互牵制关系

### `vix_proxy`

- VIX 常被拿来观察风险厌恶（Risk Aversion）或市场压力

### `equity_proxy`

- 可帮助区分风险偏好（Risk-on）与风险规避（Risk-off）环境

### `oil_close`

- 原油（Oil）与通胀、商品链条和宏观预期有关

## 4. 当前数据契约（Data Contract）

标准化后的时间序列至少保留：

- `date`：日期
- `value`：数值
- `series_id`：序列名称
- `source`：数据源
- `native_frequency`：原始频率
- `unit`：单位
- `last_updated`：最近更新时间
- `description`：字段说明

## 5. 当前已生成的数据文件

你现在可以在下面这些位置找到数据层产物：

- `data/interim/data_dictionary.csv`
- `data/interim/feature_frame.csv`
- `data/processed/model_frame.csv`

## 6. 常见错误

- 同名字段含义不一致
- 频率不统一直接拼接
- 缺失值（Missing Values）不处理
- 单位不核对
- 用今天不可得的数据预测今天或明天

## 7. 下一步衔接

下一步进入特征工程（Feature Engineering），把这些原始字段转成模型能直接使用的解释变量。

