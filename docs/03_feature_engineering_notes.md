# 03 特征工程笔记（Feature Engineering Notes）

## 1. 本模块解决的问题

原始时间序列不能直接等同于“好特征”。特征工程（Feature Engineering）要解决的是：怎样把价格、利率、美元、波动率这些原始变量加工成更有解释力的模型输入。

## 2. 当前 `v0.1` 已实现的特征

### 黄金自身特征

- `return_1d`：1 日收益率（1-day Return）
- `log_return_1d`：1 日对数收益率（1-day Log Return）
- `momentum_5d`：5 日动量（5-day Momentum）
- `momentum_20d`：20 日动量（20-day Momentum）
- `rolling_mean_ratio_5`：价格相对 5 日均值偏离
- `rolling_mean_ratio_20`：价格相对 20 日均值偏离
- `rolling_vol_10d`：10 日滚动波动率
- `rolling_vol_20d`：20 日滚动波动率

### 跨资产特征

- `silver_gold_ratio`：金银比（Silver/Gold Ratio）
- `oil_return_5d`：原油 5 日收益率
- `equity_return_5d`：股票指数 5 日收益率

### 宏观与风险特征

- `yield_spread_10y_2y`：10 年减 2 年利差（Yield Spread）
- `real_rate_gap`：实际利率代理
- `usd_proxy_z20`：美元 20 日 Z-score
- `vix_proxy_z20`：VIX 20 日 Z-score

## 3. 为什么这些特征值得做

### 动量（Momentum）

一句人话：看短期涨跌趋势有没有延续性。

### 滚动均值偏离（Rolling Mean Deviation）

一句人话：看当前价格是否偏离近期平均水平太远。

### 滚动波动率（Rolling Volatility）

一句人话：看最近市场是不是更躁动。

### 利差（Yield Spread）

一句人话：看长短端利率结构能否反映宏观状态变化。

### Z-score

一句人话：看美元或 VIX 当前是否显著高于或低于自己的近期常态。

## 4. 当前最重要的工程规则

### 外生变量统一滞后 1 天

为了避免明显前视偏差（Look-ahead Bias），`v0.1` 里除黄金主序列外，其他外生变量默认先滞后 1 个交易日再进入建模。

这个规则是保守的，但对研究卫生（Research Hygiene）很重要。

## 5. 常见误区

- 机械堆特征，不解释金融逻辑
- 直接把全部原始字段喂给模型
- 不做时间对齐（Timestamp Alignment）
- 忽略宏观数据真实发布时间（Release Timing）

## 6. 下一步衔接

下一步进入时间序列（Time Series）基础，理解为什么这些特征背后其实是在捕捉趋势、均值回复、波动聚集等结构。

