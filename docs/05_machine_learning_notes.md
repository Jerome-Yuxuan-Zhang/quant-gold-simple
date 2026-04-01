# 05 机器学习笔记（Machine Learning Notes）

## 1. 本模块解决的问题

这个模块解决的是：在 `v0.1` 阶段，怎样用一个尽量透明、容易审计的机器学习基线，去完成黄金下一日方向预测。

## 2. 当前任务定义

### 主任务

- 下一交易日方向分类（Next-day Direction Classification）

目标字段：

- `target_direction_1d`

定义：

```text
如果下一日收益率 > 0，则记为 1；否则记为 0
```

### 次级任务

- 下一交易日收益率回归（Next-day Return Regression）

目标字段：

- `target_return_1d`

## 3. 为什么先用逻辑回归（Logistic Regression）

- 结构简单
- 可解释性较强
- 适合作为基线（Baseline）
- 更容易发现特征工程和数据对齐的问题

这里的原则不是“它一定最好”，而是“它足够清楚，适合做第一层 benchmark（基准）”。

## 4. 当前评估指标

### 分类指标

- 准确率（Accuracy）
- 精确率（Precision）
- 召回率（Recall）
- 命中率（Hit Ratio）

### 回归指标

- 平均绝对误差（MAE, Mean Absolute Error）
- 均方根误差（RMSE, Root Mean Squared Error）

## 5. 为什么不能只看准确率

- 类别分布不平衡时，准确率会误导
- 分类做得不错，不等于交易上可赚钱
- 没考虑交易成本（Transaction Costs）与滑点（Slippage）

## 6. 当前验证方式

- 按时间顺序切分（Chronological Split）
- 训练集（Train）
- 验证集（Validation）
- 测试集（Test）

禁止：

- 随机打乱（Shuffle）
- 随机切分（Random Split）

## 7. 当前结果文件在哪里

你现在可以在这些位置找到模型相关 Markdown 与结果：

- `reports/generated/v01_model_report.md`
- `reports/generated/v01_model_report.json`

## 8. 下一步衔接

后续可以逐步扩展到：

- Ridge / Lasso / Elastic Net
- 树模型（Tree Models）
- Walk-forward 验证
- 更严格的时序评估

## 9. 当前最新研究发现

基于真实数据的多目标与特征子集诊断，目前有一个非常重要的现象：

- `1d` 方向任务较弱
- `3d` 和 `5d` 任务相对更稳定
- 在 `5d` 目标下，纯价格类特征子集（`gold_only`）明显优于全量特征

这说明：

- 单日方向（1-day Direction）可能噪声太大
- 直接把所有宏观变量混进模型，不一定比更精简的价格行为特征更好
- 当前应该先做“高信噪比基线（High Signal-to-Noise Baseline）”，再考虑继续扩充特征
