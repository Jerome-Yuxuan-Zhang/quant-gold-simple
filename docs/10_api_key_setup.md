# 10 API 密钥配置说明（API Key Setup）

## 1. 你不要把 API key 写在哪里

不要写进下面这些地方：

- Python 源码文件
- `configs/*.json`
- Notebook 输出
- README
- Git 提交记录（Git History）

一句话原则：**密钥（Secrets）只放本地环境，不放仓库内容。**

## 2. 当前项目推荐做法

本项目已经支持从项目根目录的 `.env` 文件自动读取：

- `ALPHAVANTAGE_API_KEY`
- `FRED_API_KEY`

也支持从系统环境变量（Environment Variables）读取。

## 3. 推荐步骤

### 第一步：复制模板

参考：

- `.env.example`

在项目根目录新建 `.env`，内容类似：

```env
ALPHAVANTAGE_API_KEY=你的_alpha_vantage_key
FRED_API_KEY=你的_fred_key
```

### 第二步：确认 `.gitignore` 已忽略

当前仓库已经忽略：

```text
.env
```

所以正常情况下不会被提交到 Git。

### 第三步：运行远程模式

```bash
.venv\Scripts\python.exe -m quant_gold.pipelines.v01_pipeline --mode remote
```

## 4. “隐蔽嵌入”正确理解

更安全的说法不是“隐蔽嵌入”，而是：

- 本地注入（Local Injection）
- 环境变量加载（Environment Variable Loading）
- 与代码解耦（Decoupled from Code）

因为真正安全的目标不是“藏得深”，而是“不要进仓库”。

## 5. 如果以后要发 GitHub

发布前请再检查：

- 没有提交 `.env`
- 没有提交真实 raw 数据缓存
- 没有在报告里打印 API key
- 没有把本地绝对路径暴露到文档截图里

## 6. 当前文档在哪里

你要的分文件 Markdown 学习文档现在都在：

- `docs/00_project_map.md`
- `docs/01_math_finance_foundations.md`
- `docs/02_data_dictionary.md`
- `docs/03_feature_engineering_notes.md`
- `docs/04_time_series_notes.md`
- `docs/05_machine_learning_notes.md`
- `docs/06_backtesting_notes.md`
- `docs/07_risk_management_notes.md`
- `docs/08_research_log.md`
- `docs/09_todo_and_next_steps.md`
- `docs/10_api_key_setup.md`
