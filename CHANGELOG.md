# Changelog

All notable changes to this project will be documented in this file.

The format is inspired by Keep a Changelog.

## [0.1.0] - 2026-04-01

### Added

- GitHub Actions CI, issue templates, PR template, dependabot, pre-commit, editor config
- 教材级 Git / GitHub 发布文档
- 更完整的贡献与安全说明
- 针对远程 API 错误载荷和多日持仓语义的新测试

### Changed

- 多日预测目标下的持仓构造升级为 horizon-aligned position
- 模型比较报告避免使用测试集排序选“最佳模型”
- 回测配置支持显式指定 `model_name` / `model_params`
- Markdown 报告渲染在缺少 `tabulate` 时提供降级方案

### Fixed

- 远程数据抓取时对 Alpha Vantage / FRED 错误返回缺少显式校验
- EDA markdown 输出对可选依赖过度脆弱
