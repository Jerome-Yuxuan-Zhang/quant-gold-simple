# 13 发布前检查清单

这份清单适合你每次准备上传 GitHub、发版本、或者给别人看仓库之前过一遍。

## 1. 安全检查

- [ ] `.env` 没有被 Git 跟踪
- [ ] README、docs、截图里没有 API key
- [ ] 没有把本地绝对路径写进公开文档
- [ ] 没有把 `data/raw/` 真实缓存提交上去

## 2. 工程检查

- [ ] `uv sync --extra dev` 可以成功
- [ ] `uv run ruff check .` 通过
- [ ] `uv run pytest` 通过
- [ ] `uv run quant-gold-v01 --mode sample` 可以跑通
- [ ] `.github/workflows/ci.yml` 存在

## 3. 研究检查

- [ ] 目标定义与回测执行口径一致
- [ ] 模型选择没有使用测试集做排序
- [ ] Walk-forward 训练没有使用未来信息
- [ ] 报告文字和真实实现一致

## 4. 仓库展示检查

- [ ] README 清楚说明项目目的、边界、用法
- [ ] LICENSE 存在
- [ ] CONTRIBUTING / SECURITY 存在
- [ ] issue / PR template 存在
- [ ] 文档目录能帮助新手快速理解项目

## 5. Git 检查

- [ ] `git status` 干净或只包含本次改动
- [ ] commit message 清晰
- [ ] 默认分支是 `main`
- [ ] 远程仓库 `origin` 已绑定正确地址

## 6. 发布后检查

- [ ] GitHub 仓库首页显示正常
- [ ] Actions 首次 CI 通过
- [ ] `.gitignore` 工作正常
- [ ] 生成文件和缓存没有意外出现
