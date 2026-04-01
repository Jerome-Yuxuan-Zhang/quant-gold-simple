# quant-gold-simple

`quant-gold-simple` 是一个面向黄金（日频）研究的 Python 项目模板，重点放在三件事上：

- 研究流程可复现
- 代码结构可维护
- 文档足够清楚，适合学习和二次扩展

它不是“收益炫技仓库”，也不是“几百个模型堆在一起的 demo”。  
它更像一个认真打底的量化研究起点：把数据、特征、目标、评估、walk-forward、报告生成这些基础件先搭稳。

## 项目定位

这个仓库适合你在以下场景使用：

- 做一个能公开放到 GitHub 的量化研究作品
- 学习如何把 notebook 式研究整理成工程化项目
- 以黄金为例，练习日频时间序列特征、分类任务和基础回测
- 以后扩展到更多资产、更多模型、更多风控模块

这个仓库暂时不解决的问题：

- 高频交易
- 生产级交易执行
- 完整的成交撮合与滑点建模
- vintage-aware 宏观发布时间处理
- 实盘部署

## 当前版本做了什么

当前 `v0.1` 版本已经包含：

- Alpha Vantage + FRED 数据源抽象
- 原始数据缓存
- 标准化数据契约（normalizer）
- 特征构造
- 多日目标构造
- 时间顺序切分
- 基线模型与模型比较
- walk-forward 预测
- 最小可用 long/flat 回测
- Markdown / JSON / PNG 报告输出
- 基础单元测试
- GitHub Actions CI
- 贡献规范、Issue/PR 模板、发布清单

## 为什么这个仓库和很多“量化练手项目”不一样

这个仓库特别强调下面几个研究原则：

1. 不把测试集拿去做模型选择
2. 不把“能跑通”误当成“结论可信”
3. 预测目标与回测执行必须语义一致
4. 生成报告必须能回溯到具体代码和配置
5. 文档不仅是说明书，也要尽量承担教学功能

## 项目结构

```text
quant_gold_simple/
├─ configs/                  # 数据集与实验配置
├─ data/                     # 本地缓存与派生数据（默认不入库）
├─ docs/                     # 学习文档、研究说明、发布指南
├─ examples/                 # 可直接运行的示例
├─ reports/                  # 生成报告目录（默认不入库）
├─ src/quant_gold/           # 项目源码
│  ├─ backtest/              # walk-forward 与回测执行
│  ├─ data/                  # 数据源、缓存、标准化
│  ├─ evaluation/            # 指标计算
│  ├─ features/              # 特征工程
│  ├─ models/                # 基线模型、模型比较、优化、目标、切分
│  ├─ pipelines/             # 端到端实验入口
│  └─ utils/                 # IO 与样本数据辅助函数
├─ tests/                    # 单元测试
├─ .github/                  # CI、Issue/PR 模板、Dependabot
└─ pyproject.toml            # 项目依赖与工具配置
```

## 快速开始

### 1. 安装依赖

推荐使用 `uv`：

```bash
uv sync --extra dev
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env`：

```bash
ALPHAVANTAGE_API_KEY=your_alpha_vantage_key
FRED_API_KEY=your_fred_key
```

请不要把真实密钥写进：

- 源码
- `configs/*.json`
- README
- issue / PR

### 3. 运行样本模式

```bash
uv run quant-gold-v01 --mode sample
```

这个模式不依赖远程 API，适合先验证项目能不能完整跑通。

### 4. 运行远程模式

```bash
uv run quant-gold-v01 --mode remote
```

这个模式会读取 `.env` 中的 API key，拉取真实数据并写入本地缓存。

## 常用命令

```bash
uv run ruff check .
uv run pytest
uv run pytest --cov=src/quant_gold --cov-report=term-missing
uv run quant-gold-v01 --mode sample
pre-commit install
```

## 输出内容

运行 pipeline 后，通常会生成：

- `data/interim/feature_frame.csv`
- `data/processed/model_frame.csv`
- `reports/generated/*.md`
- `reports/generated/*.json`
- `reports/generated/*.png`

这些目录默认被 `.gitignore` 忽略，不建议直接提交到 GitHub。

## 教学文档入口

如果你是为了“学明白”这个项目，建议按这个顺序读：

1. [项目地图](./docs/00_project_map.md)
2. [项目架构拆解（教材版）](./docs/11_architecture_walkthrough_zh.md)
3. [Git 与 GitHub 上传教程（教科书级）](./docs/12_git_and_github_textbook_zh.md)
4. [发布前检查清单](./docs/13_release_checklist_zh.md)

如果你是为了研究方法，继续读：

- [特征工程笔记](./docs/03_feature_engineering_notes.md)
- [时间序列笔记](./docs/04_time_series_notes.md)
- [机器学习笔记](./docs/05_machine_learning_notes.md)
- [回测笔记](./docs/06_backtesting_notes.md)
- [风控笔记](./docs/07_risk_management_notes.md)

## GitHub 上传建议

首次上传建议按下面顺序做：

```bash
git init -b main
git status
uv sync --extra dev
uv run ruff check .
uv run pytest
git add .
git commit -m "chore: prepare repository for GitHub release"
git remote add origin https://github.com/<your-github-username>/quant_gold_simple.git
git push -u origin main
```

详细解释见：

- [Git 与 GitHub 上传教程（教科书级）](./docs/12_git_and_github_textbook_zh.md)

## 工程化特性

这个仓库已经包含以下适合公开发布的基础设施：

- `MIT` License
- `CONTRIBUTING.md`
- `SECURITY.md`
- `CHANGELOG.md`
- GitHub Actions CI
- Dependabot
- Issue / PR 模板
- `.editorconfig`
- `.gitattributes`
- `pre-commit`

## 研究注意事项

请把这个仓库视为“研究基线”，而不是“交易承诺”。

尤其注意：

- 分类准确率不等于交易价值
- 回测收益不等于未来收益
- 样本外表现比训练集表现更重要
- 多日预测目标必须和持仓构造一致

## 路线图

- `v0.1`：项目骨架 + 数据层 + 特征 + 基线模型 + 基础回测
- `v0.2`：更系统的时间序列模型与更严格评估
- `v0.3`：更丰富的 ML baseline 与特征诊断
- `v0.4`：更严谨的信号层与风险控制
- `v0.5+`：归因、regime、组合层与更完整的研究平台化

## 许可证

本项目采用 [MIT License](./LICENSE)。
