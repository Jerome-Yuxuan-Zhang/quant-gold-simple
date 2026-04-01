# quant-gold-simple

`quant-gold-simple` is a research-first Python project for daily gold forecasting and baseline backtesting.

It is designed as a clean, reproducible starter for quantitative research rather than a performance-marketing repository. The focus is on data hygiene, transparent assumptions, walk-forward evaluation, and educational clarity.

## What This Project Is

- A daily-frequency gold research starter
- A modular example of how to structure a small quant project
- A baseline pipeline covering data ingestion, feature engineering, modeling, reporting, and backtesting
- A teaching-oriented repository with detailed notes and walkthrough documents

## What This Project Is Not

- Not a production trading system
- Not a high-frequency strategy
- Not a claim of deployable edge
- Not a full institutional backtesting platform

## Current Scope

The current `v0.1` version includes:

- Alpha Vantage and FRED datasource abstractions
- Local raw-data caching
- A shared normalization contract for time series
- Daily feature engineering for gold and macro/risk proxies
- Classification targets for next-period gold direction
- Time-ordered train/validation/test splits
- Baseline ML model comparison
- Walk-forward prediction generation
- A minimal long/flat backtest
- Markdown, JSON, CSV, and PNG outputs
- Unit tests and CI

## Research Design Principles

This repository is intentionally opinionated about a few things:

- Reproducibility matters more than hype
- Test sets should not drive model selection
- Forecast target definition and trading logic should be semantically aligned
- Reports should reflect the actual code path, not hand-wavy storytelling
- Simpler, auditable baselines should come before more complex models

## Data Universe

Primary asset:

- Gold

Supporting proxies:

- Silver
- U.S. 2Y and 10Y yields
- Real-yield / breakeven inflation proxies
- U.S. dollar proxy
- VIX proxy
- Equity proxy
- WTI oil proxy

Recommended data sources:

- Alpha Vantage: `GOLD_SILVER_HISTORY`
- FRED: `DGS2`, `DGS10`, `DFII10`, `T10YIE`, `DTWEXBGS`, `VIXCLS`, `SP500`, `DCOILWTICO`

## Repository Layout

```text
quant_gold_simple/
├─ configs/                  # Dataset and experiment configuration
├─ data/                     # Local cache and derived data
├─ docs/                     # Notes, walkthroughs, and learning material
├─ examples/                 # Small runnable entry points
├─ reports/                  # Generated reports and figures
├─ src/quant_gold/           # Package source code
├─ tests/                    # Test suite
└─ pyproject.toml            # Dependencies and tool configuration
```

## Quickstart

Install dependencies:

```bash
uv sync --extra dev
```

Set API keys in a local `.env` file:

```bash
ALPHAVANTAGE_API_KEY=your_alpha_vantage_key
FRED_API_KEY=your_fred_key
```

Run the sample pipeline:

```bash
uv run quant-gold-v01 --mode sample
```

Run the remote-data pipeline:

```bash
uv run quant-gold-v01 --mode remote
```

## Outputs

Typical generated artifacts include:

- `data/interim/feature_frame.csv`
- `data/processed/model_frame.csv`
- `data/processed/backtest_predictions_10y.csv`
- `reports/generated/*.md`
- `reports/generated/*.json`
- `reports/generated/*.png`

These are treated as local outputs rather than version-controlled source files.

## Documentation

If you want the big-picture walkthrough first:

- [Project Map](./docs/00_project_map.md)
- [Architecture Walkthrough (Chinese)](./docs/11_architecture_walkthrough_zh.md)

If you want the research notes:

- [Feature Engineering Notes](./docs/03_feature_engineering_notes.md)
- [Time Series Notes](./docs/04_time_series_notes.md)
- [Machine Learning Notes](./docs/05_machine_learning_notes.md)
- [Backtesting Notes](./docs/06_backtesting_notes.md)
- [Risk Management Notes](./docs/07_risk_management_notes.md)

If you want the repository / publishing docs:

- [Git and GitHub Textbook Guide (Chinese)](./docs/12_git_and_github_textbook_zh.md)
- [Release Checklist (Chinese)](./docs/13_release_checklist_zh.md)

## Development

Useful commands:

```bash
uv run ruff check .
uv run pytest
uv run pytest --cov=src/quant_gold --cov-report=term-missing
```

For contribution and repository policy:

- [Contributing Guide](./CONTRIBUTING.md)
- [Security Policy](./SECURITY.md)
- [Changelog](./CHANGELOG.md)

## Roadmap

- `v0.1`: reproducible baseline research pipeline
- `v0.2`: stronger time-series modeling and validation
- `v0.3`: broader ML baseline suite
- `v0.4`: richer signal and risk-control layer
- `v0.5+`: attribution, regimes, and broader research platform expansion

## License

Released under the [MIT License](./LICENSE).
