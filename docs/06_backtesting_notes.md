# 06 回测笔记（Backtesting Notes）

## 1. 当前状态

`v0.1` 还没有完整回测系统（Backtesting System），但现在就要把边界写清楚，避免后面“模型有效”和“策略可交易”被混为一谈。

## 2. 一个最小回测系统至少要回答什么

- 信号是什么（Signal）
- 信号何时生效（Signal Lag）
- 仓位如何生成（Position Sizing）
- 交易成本怎么算（Transaction Costs）
- 滑点如何处理（Slippage）
- 换仓频率是什么（Rebalancing Frequency）
- 绩效怎么评估（Performance Evaluation）

## 3. 当前必须警惕的偏差

- 前视偏差（Look-ahead Bias）
- 数据窥探（Data Snooping）
- 过拟合（Overfitting）
- 生存者偏差（Survivorship Bias）

## 4. 为什么这里先不急着做

因为如果数据层、特征层、预测目标、时间对齐都没有打牢，回测结果看起来再漂亮，也可能只是研究设计有漏洞。

## 5. 下一步衔接

等 `v0.2` 和 `v0.3` 稳定后，再进入最小信号层和最小回测层，会更稳。

## 6. 当前十年回测原型（10Y Prototype Backtest）

目前项目已经有了第一版十年滚动样本外回测（10-year Walk-forward Out-of-sample Backtest）。

当前设置是：

- 目标期限：5 日方向（5-day Direction）
- 特征子集：`gold_only`
- 模型：逻辑回归（Logistic Regression）
- 信号：预测上涨则次日做多，否则空仓（Long / Flat）
- 再训练频率：每 21 个交易日
- 交易成本：5 bps

## 7. 当前回测结论

这版原型的意义是“验证信号是否值得继续研究”，而不是宣称策略已经可交易。

当前结果显示：

- 策略可以形成正收益
- 但相对买入持有（Buy and Hold）并未取得优势
- 最大回撤（Max Drawdown）也没有明显更优

这意味着：

- 当前模型与信号仍处于研究原型阶段
- 后续更值得做的是信号规则、持仓规则和模型稳健性改造
- 不能因为分类准确率改善，就直接假定交易表现也改善
