# 12 Git 与 GitHub 上传教程（教科书级）

这份文档假设你不是“会一点 Git”，而是希望真正理解：

- Git 在解决什么问题
- 每条命令是什么意思
- 什么时候该 commit
- 怎么把本地项目稳稳上传到 GitHub

## 1. Git 是干什么的

Git 不是“上传工具”，而是版本管理系统。

它解决的核心问题是：

- 我改了什么
- 我什么时候改的
- 如果改坏了，能不能回到以前
- 多人协作时怎么合并变化

GitHub 则是 Git 仓库的远程托管平台。

## 2. 上传前要先做哪些准备

在这个项目里，上传前最重要的不是 `git push`，而是先保证仓库“适合公开”。

你必须先确认：

1. `.env` 没有提交
2. API key 没有写进代码和文档
3. `data/raw/` 等缓存没有提交
4. `reports/generated/` 临时报表没有误提交
5. README、LICENSE、测试、CI 至少是可用状态

## 3. 这个项目推荐的本地流程

### 3.1 初始化仓库

如果当前目录还不是 Git 仓库：

```bash
git init -b main
```

解释：

- `git init`：把当前目录变成一个 Git 仓库
- `-b main`：直接把默认分支设为 `main`

### 3.2 查看当前状态

```bash
git status
```

这是 Git 里最值得高频使用的命令。

它会告诉你：

- 哪些文件被跟踪
- 哪些文件未被跟踪
- 哪些文件已暂存
- 当前分支是什么

### 3.3 把该忽略的内容先忽略掉

这个项目已经配置了 `.gitignore`，用于忽略：

- `.env`
- `.venv`
- `data/raw/`
- `data/interim/`
- `data/processed/`
- `reports/generated/`
- 缓存和覆盖率文件

你可以用下面的命令确认：

```bash
git status --short
```

如果某些不该出现的文件还出现了，先修 `.gitignore`，不要急着 commit。

## 4. commit 到底是什么

很多人以为 commit 就是“保存”。

更准确地说，commit 是：

“为当前这一组有意义的修改创建一个可回溯的历史节点。”

所以好 commit 的标准不是“攒够很多文件”，而是：

- 主题单一
- 逻辑完整
- 别人以后能看懂

### 4.1 先暂存

```bash
git add .
```

或者更稳妥一点，按文件加：

```bash
git add README.md pyproject.toml src/ tests/ .github/
```

### 4.2 再提交

```bash
git commit -m "chore: prepare repository for GitHub release"
```

建议 commit message 风格：

- `feat: add walk-forward horizon-aligned position logic`
- `fix: validate remote API error payloads before caching`
- `docs: rewrite README and add GitHub publishing guide`
- `chore: add CI, pre-commit, and repository templates`

## 5. 为什么推荐小步提交

因为以后你回头看历史时，会很感谢今天的自己。

坏例子：

```text
update
fix
change files
```

好例子：

```text
fix: align multi-day forecast horizon with backtest position logic
docs: add textbook-level GitHub publishing guide
chore: add CI and repository governance files
```

## 6. 在 GitHub 上创建远程仓库

登录 GitHub 后：

1. 点击 `New repository`
2. 仓库名建议和本地一致，例如 `quant_gold_simple`
3. 选择 `Public`
4. 不要勾选自动生成 README、`.gitignore`、LICENSE

为什么不要勾？

因为你本地已经有这些内容了，再生成一次容易造成不必要的合并。

## 7. 绑定远程仓库

假设你的 GitHub 用户名是 `yourname`，仓库名是 `quant_gold_simple`：

```bash
git remote add origin https://github.com/yourname/quant_gold_simple.git
```

检查远程：

```bash
git remote -v
```

## 8. 首次推送

```bash
git push -u origin main
```

解释：

- `push`：把本地提交推到远程
- `-u`：建立本地 `main` 和远程 `origin/main` 的跟踪关系

以后再推送时，你通常只要：

```bash
git push
```

## 9. 以后日常更新怎么做

推荐循环：

1. 修改代码
2. `git status`
3. 跑测试
4. `git add ...`
5. `git commit -m "..."`
6. `git push`

## 10. 什么时候不要 push

以下情况先别 push：

- 测试没跑
- README 和代码明显不一致
- 误把 `.env` 或缓存纳入跟踪
- 你自己都说不清这次改动是干什么的

## 11. GitHub 仓库首页最重要的第一印象

一个像样的开源仓库，首页通常至少有：

- 清楚的 README
- LICENSE
- 可运行的命令
- 测试和 CI
- 贡献说明
- issue / PR 模板

这次升级已经把这些基础件补上了。

## 12. 最后一组你会一直用到的命令

```bash
git status
git add .
git commit -m "..."
git log --oneline --decorate --graph
git diff
git remote -v
git push
```

## 13. 这份项目最推荐的首次上传命令清单

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

## 14. 上传后立刻要做的三件事

1. 把仓库描述补好
2. 检查 GitHub Actions 是否通过
3. 打开仓库首页，确认 README 展示正常、没有敏感内容、没有大文件误传

如果这三件事都过了，你这个项目就已经从“本地练习”迈到“可公开展示的作品”了。
