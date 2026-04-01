# 00 项目地图（Project Map）

## 1. 项目要解决什么问题

这个项目要做的不是“直接预测黄金价格然后宣称能赚钱”，而是搭建一个可学习、可复现、可审计的黄金量化研究框架。

研究主线是：

- 黄金（日频，Daily Frequency）作为主研究资产
- 宏观变量（Macro Variables）与风险变量（Risk Proxies）作为外生解释变量
- 先做基线（Baseline），再做升级（Upgrade）

## 2. 当前 `v0.1` 的系统结构

### 数据层（Data Layer）

- `src/quant_gold/data/`
- 职责：从 Alpha Vantage 和 FRED 拉取数据、缓存原始结果、标准化字段格式

### 特征层（Feature Engineering Layer）

- `src/quant_gold/features/`
- 职责：把标准化后的时间序列加工成模型可用特征

### 模型层（Model Layer）

- `src/quant_gold/models/`
- 职责：目标变量构造、时间序列切分、基线模型训练

### 评估层（Evaluation Layer）

- `src/quant_gold/evaluation/`
- 职责：计算分类与回归指标

### 流水线层（Pipeline Layer）

- `src/quant_gold/pipelines/`
- 职责：把“拉数 -> 特征 -> 建模 -> 评估 -> 报告”串成完整流程

### 文档层（Documentation Layer）

- `docs/`
- 职责：沉淀学习讲义、研究记录、下一步计划

## 3. 项目目录说明

- `configs/`：数据集配置（Dataset Config）与实验配置（Experiment Config）
- `data/raw/`：原始数据缓存（Raw Cache）
- `data/interim/`：中间结果（Interim Data）
- `data/processed/`：模型输入数据（Processed Data）
- `reports/generated/`：EDA 与模型报告（Reports）
- `examples/`：最小运行示例（Examples）
- `tests/`：单元测试（Unit Tests）

## 4. 版本路线图（Roadmap）

### `v0.1`

- 项目骨架
- 数据层
- 基础 EDA（Exploratory Data Analysis）
- 统计与机器学习基线

### `v0.2`

- 经典时间序列模型（Classical Time-Series Models）
- ARIMA / GARCH 等方法的教学与实现

### `v0.3`

- 更完整的机器学习基线（Machine Learning Baselines）
- 特征选择（Feature Selection）
- Walk-forward 验证（Walk-forward Validation）

### `v0.4`

- 信号生成（Signal Generation）
- 最小回测闭环（Minimal Backtest Loop）

## 5. 当前边界

- 当前主频率固定为日频（Daily）
- 当前不是高频研究（High Frequency Research）
- 当前不是实盘交易系统（Live Trading System）
- 当前还没有完整回测引擎（Backtest Engine）
- 当前没有处理真实发布时间与修订值（Release Timing / Vintage Data）

