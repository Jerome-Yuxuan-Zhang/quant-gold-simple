from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from quant_gold.backtest.simulator import run_long_flat_backtest
from quant_gold.backtest.walk_forward import WalkForwardConfig, generate_walk_forward_predictions
from quant_gold.data.cache import RawCache
from quant_gold.data.contracts import FeatureSpec, SplitSpec, TargetSpec, dataset_specs_from_config
from quant_gold.data.normalizers import Normalizer
from quant_gold.data.sources import AlphaVantageDataSource, FredDataSource
from quant_gold.features.builders import FeatureBuilder
from quant_gold.models.baselines import run_baselines
from quant_gold.models.model_selection import compare_classification_models
from quant_gold.models.optimizer import optimize_model_spec
from quant_gold.models.splitters import Splitter
from quant_gold.models.targets import TargetBuilder
from quant_gold.settings import Settings
from quant_gold.utils.io import read_json, render_markdown_table, write_dataframe_csv, write_json, write_markdown
from quant_gold.utils.sample_data import generate_sample_standard_frames


def load_dataset_specs(project_root: Path) -> list:
    payload = read_json(project_root / "configs" / "datasets.json")
    return dataset_specs_from_config(payload)


def load_experiment_config(project_root: Path) -> dict:
    return read_json(project_root / "configs" / "experiment.json")


def fetch_remote_standard_frames(settings: Settings, dataset_specs: list) -> list:
    cache = RawCache(settings.data_raw_dir)
    normalizer = Normalizer()
    alpha = AlphaVantageDataSource(cache=cache, api_key=settings.alpha_vantage_api_key)
    fred = FredDataSource(cache=cache, api_key=settings.fred_api_key)

    standard_frames = []
    for dataset_spec in dataset_specs:
        source = alpha if dataset_spec.source == "alpha_vantage" else fred
        raw_payload = source.fetch(dataset_spec)
        standard_frames.append(normalizer.normalize(raw_payload))
    return standard_frames


def build_v01_frames(
    standard_frames: list,
    target_horizon_days: int = 1,
    required_feature_columns: list[str] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    feature_builder = FeatureBuilder()
    target_builder = TargetBuilder()
    feature_frame = feature_builder.build(standard_frames, FeatureSpec())
    model_frame = target_builder.build(
        feature_frame,
        TargetSpec(forecast_horizon_days=target_horizon_days),
        required_feature_columns=required_feature_columns,
    )
    return feature_frame, model_frame


def write_data_dictionary(settings: Settings, standard_frames: list) -> None:
    rows = []
    for standard_frame in standard_frames:
        frame = standard_frame.frame
        rows.append(
            {
                "series_id": standard_frame.dataset_spec.name,
                "source": standard_frame.dataset_spec.source,
                "remote_id": standard_frame.dataset_spec.remote_id,
                "native_frequency": standard_frame.dataset_spec.native_frequency,
                "unit": frame["unit"].iloc[0],
                "last_updated": frame["last_updated"].iloc[0],
                "description": frame["description"].iloc[0],
            }
        )
    data_dictionary = pd.DataFrame(rows).sort_values("series_id").reset_index(drop=True)
    write_dataframe_csv(settings.data_interim_dir / "data_dictionary.csv", data_dictionary)


def generate_eda_outputs(settings: Settings, feature_frame: pd.DataFrame) -> None:
    summary = feature_frame.describe(include="all").transpose()
    missingness = feature_frame.isna().mean().sort_values(ascending=False)
    correlation_candidates = [
        column
        for column in [
            "gold_close",
            "silver_close",
            "usd_proxy",
            "yield_10y",
            "real_yield_proxy",
            "vix_proxy",
            "equity_proxy",
            "oil_close",
        ]
        if column in feature_frame.columns
    ]
    correlation = feature_frame[correlation_candidates].corr() if correlation_candidates else pd.DataFrame()

    write_dataframe_csv(
        settings.data_interim_dir / "eda_summary.csv",
        summary.reset_index().rename(columns={"index": "field"}),
    )
    write_dataframe_csv(
        settings.data_interim_dir / "eda_missingness.csv",
        missingness.rename("missing_fraction").reset_index().rename(columns={"index": "field"}),
    )
    if not correlation.empty:
        write_dataframe_csv(
            settings.data_interim_dir / "eda_correlation.csv",
            correlation.reset_index().rename(columns={"index": "field"}),
        )

    figure, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    feature_frame.plot(x="date", y="gold_close", ax=axes[0], title="Gold close")
    feature_frame.plot(x="date", y="return_1d", ax=axes[1], title="Gold daily return")
    figure.tight_layout()
    figure.savefig(settings.reports_dir / "gold_eda.png", dpi=150)
    plt.close(figure)

    eda_markdown = f"""# v0.1 EDA Report

## Dataset window

- Start: `{feature_frame['date'].min().date()}`
- End: `{feature_frame['date'].max().date()}`
- Rows: `{len(feature_frame)}`

## Missingness snapshot

{render_markdown_table(missingness.head(10))}

## Core correlations

{render_markdown_table(correlation) if not correlation.empty else 'No correlation matrix was generated.'}
"""
    write_markdown(settings.reports_dir / "v01_eda_report.md", eda_markdown)


def generate_model_report(settings: Settings, baseline_results, split_frames) -> None:
    payload = {
        "classification_metrics": baseline_results.classification_metrics,
        "regression_metrics": baseline_results.regression_metrics,
        "feature_columns": baseline_results.feature_columns,
        "split_sizes": {
            "train": len(split_frames.train),
            "validation": len(split_frames.validation),
            "test": len(split_frames.test),
        },
    }
    write_json(settings.reports_dir / "v01_model_report.json", payload)

    report_markdown = f"""# v0.1 Model Report

## Split sizes

- Train: `{len(split_frames.train)}`
- Validation: `{len(split_frames.validation)}`
- Test: `{len(split_frames.test)}`

## Classification metrics

### Train

{render_markdown_table(pd.DataFrame([baseline_results.classification_metrics['train']]), index=False)}

### Validation

{render_markdown_table(pd.DataFrame([baseline_results.classification_metrics['validation']]), index=False)}

### Test

{render_markdown_table(pd.DataFrame([baseline_results.classification_metrics['test']]), index=False)}

### Test naive baseline

{render_markdown_table(pd.DataFrame([baseline_results.classification_metrics['test_naive_direction']]), index=False)}

## Regression metrics

### Train

{render_markdown_table(pd.DataFrame([baseline_results.regression_metrics['train']]), index=False)}

### Validation

{render_markdown_table(pd.DataFrame([baseline_results.regression_metrics['validation']]), index=False)}

### Test

{render_markdown_table(pd.DataFrame([baseline_results.regression_metrics['test']]), index=False)}

## Notes

- Primary task is classification of next-day gold direction.
- Regression output is a diagnostic, not a trading claim.
- Current pipeline uses daily alignment and a conservative lag on exogenous series.
"""
    write_markdown(settings.reports_dir / "v01_model_report.md", report_markdown)


def generate_diagnosis_report(
    settings: Settings,
    feature_frame: pd.DataFrame,
    model_frame: pd.DataFrame,
    baseline_results,
    split_frames,
) -> None:
    feature_missing = feature_frame.isna().mean().sort_values(ascending=False).head(10)
    class_balance = {
        "full": float(model_frame["target_direction_1d"].mean()),
        "train": float(split_frames.train["target_direction_1d"].mean()),
        "validation": float(split_frames.validation["target_direction_1d"].mean()),
        "test": float(split_frames.test["target_direction_1d"].mean()),
    }
    coefficient_series = (
        pd.Series(baseline_results.classification_coefficients)
        .sort_values(key=lambda series: series.abs(), ascending=False)
        .head(10)
    )
    target_corr = (
        model_frame[baseline_results.feature_columns + ["target_return_1d"]]
        .corr(numeric_only=True)["target_return_1d"]
        .drop("target_return_1d")
        .sort_values(key=lambda series: series.abs(), ascending=False)
        .head(10)
    )

    test_accuracy = baseline_results.classification_metrics["test"]["accuracy"]
    naive_accuracy = baseline_results.classification_metrics["test_naive_direction"]["accuracy"]
    summary_line = (
        "当前逻辑回归测试集表现优于朴素基线。"
        if test_accuracy > naive_accuracy
        else "当前逻辑回归测试集表现未超过朴素方向基线，需要先做数据与特征诊断。"
    )

    diagnosis_markdown = f"""# v0.1 真实数据诊断报告

## 1. 样本区间

- 特征样本起点：`{feature_frame["date"].min().date()}`
- 特征样本终点：`{feature_frame["date"].max().date()}`
- 特征样本行数：`{len(feature_frame)}`
- 建模样本起点：`{model_frame["date"].min().date()}`
- 建模样本终点：`{model_frame["date"].max().date()}`
- 建模样本行数：`{len(model_frame)}`

## 2. 标签分布（Class Balance）

- 全样本正类比例：`{class_balance['full']:.4f}`
- 训练集正类比例：`{class_balance['train']:.4f}`
- 验证集正类比例：`{class_balance['validation']:.4f}`
- 测试集正类比例：`{class_balance['test']:.4f}`

## 3. 缺失值最高的字段

{render_markdown_table(feature_missing)}

## 4. 测试集基线比较

- 逻辑回归准确率（Logistic Regression Accuracy）：`{test_accuracy:.4f}`
- 朴素方向基线准确率（Naive Direction Accuracy）：`{naive_accuracy:.4f}`
- 诊断结论：{summary_line}

## 5. 绝对值最大的逻辑回归系数

{render_markdown_table(coefficient_series)}

## 6. 与下一日收益率相关性绝对值最高的特征

{render_markdown_table(target_corr)}

## 7. 当前判断

- 当前工程链路已经可用，问题已从“接口是否打通”转为“特征是否足够有信息量”。
- 如果测试集不优于朴素基线，下一步应该优先检查目标定义、样本切分、特征窗口和缺失处理，而不是直接上更复杂模型。
- 股指代理（Equity Proxy）相关特征缺失较多，说明真实数据起始时间不一致会影响最终可用样本。

## 8. 下一步建议

1. 先做真实数据 EDA 结论整理，解释美元、利率、VIX、股指与黄金的关系是否稳定。
2. 复查 `target_direction_1d` 是否过于噪声化，可增加周频方向或多日收益目标作对照。
3. 复查特征窗口，尤其是 5 日与 20 日窗口是否适合当前日频黄金任务。
4. 在进入 `v0.2` 前，先让至少一个简单基线稳定优于朴素方向基线。
"""
    write_markdown(settings.reports_dir / "v01_diagnosis_report_zh.md", diagnosis_markdown)


def build_horizon_diagnostics(feature_frame: pd.DataFrame, experiment_config: dict) -> tuple[list[dict], str]:
    horizons = experiment_config.get("diagnostic_horizons", [1, 3, 5])
    rows: list[dict] = []
    observations: list[str] = []

    for horizon in horizons:
        model_frame = TargetBuilder().build(
            feature_frame,
            TargetSpec(forecast_horizon_days=horizon),
            required_feature_columns=experiment_config["classification_feature_columns"],
        )
        split_frames = Splitter().split(
            model_frame,
            SplitSpec(
                train_fraction=experiment_config["train_fraction"],
                validation_fraction=experiment_config["validation_fraction"],
            ),
        )
        baseline_results = run_baselines(
            split_frames=split_frames,
            feature_columns=experiment_config["classification_feature_columns"],
        )
        test_accuracy = baseline_results.classification_metrics["test"]["accuracy"]
        naive_accuracy = baseline_results.classification_metrics["test_naive_direction"]["accuracy"]
        advantage = test_accuracy - naive_accuracy
        rows.append(
            {
                "horizon_days": horizon,
                "model_rows": len(model_frame),
                "test_positive_ratio": float(model_frame["target_direction_1d"].mean()),
                "test_accuracy": test_accuracy,
                "test_naive_accuracy": naive_accuracy,
                "accuracy_advantage_vs_naive": advantage,
                "test_rmse": baseline_results.regression_metrics["test"]["rmse"],
            }
        )

    comparison = pd.DataFrame(rows).sort_values("horizon_days").reset_index(drop=True)
    best_row = comparison.sort_values("accuracy_advantage_vs_naive", ascending=False).iloc[0]
    worst_row = comparison.sort_values("accuracy_advantage_vs_naive", ascending=True).iloc[0]

    observations.append(
        
            f"表现最接近或优于朴素基线的期限是 `{int(best_row['horizon_days'])}d`，"
            f"准确率优势为 `{best_row['accuracy_advantage_vs_naive']:.4f}`。"
        
    )
    observations.append(
        
            f"最弱的期限是 `{int(worst_row['horizon_days'])}d`，"
            f"准确率优势为 `{worst_row['accuracy_advantage_vs_naive']:.4f}`。"
        
    )
    if (comparison["accuracy_advantage_vs_naive"] <= 0).all():
        observations.append("当前 1d/3d/5d 目标都没有稳定超过朴素方向基线，应优先回到目标定义和特征质量。")
    else:
        observations.append("至少有一个多日目标开始接近或超过朴素方向基线，说明任务期限可能比 1 日方向更适合当前特征。")

    return rows, "\n".join(f"- {item}" for item in observations)


def generate_horizon_comparison_report(
    settings: Settings,
    horizon_rows: list[dict],
    observations_markdown: str,
) -> None:
    comparison = pd.DataFrame(horizon_rows).sort_values("horizon_days").reset_index(drop=True)
    report_markdown = f"""# v0.1 多预测期限对比报告

## 1. 目的

这份报告用于比较不同预测期限（Forecast Horizon）下，当前特征集对黄金方向任务是否更有信息量。

## 2. 对比表

{render_markdown_table(comparison, index=False)}

字段说明：

- `horizon_days`：目标预测期限
- `model_rows`：可用建模样本量
- `test_positive_ratio`：目标为上涨的比例
- `test_accuracy`：逻辑回归测试集准确率
- `test_naive_accuracy`：朴素方向基线测试集准确率
- `accuracy_advantage_vs_naive`：逻辑回归相对朴素基线的准确率差值
- `test_rmse`：对应回归诊断任务的测试集 RMSE

## 3. 当前观察

{observations_markdown}

## 4. 如何解释

- 如果多日目标优于 1 日目标，通常说明单日方向噪声更大。
- 如果所有期限都弱于朴素基线，问题更可能在特征信息量不足，而不是模型不够复杂。
- 如果某个期限的标签分布明显偏斜，需要警惕分类准确率的误导。

## 5. 下一步建议

1. 优先围绕表现最好的期限继续做 EDA 和特征诊断。
2. 对比 `1d / 3d / 5d` 目标下，美元、利率、VIX 相关特征的重要性是否变化。
3. 只有在简单基线有改善后，再考虑扩展到更复杂模型。
"""
    write_markdown(settings.reports_dir / "v01_horizon_comparison_report_zh.md", report_markdown)
    write_json(settings.reports_dir / "v01_horizon_comparison_report.json", {"rows": horizon_rows})


def build_feature_subset_diagnostics(
    feature_frame: pd.DataFrame,
    experiment_config: dict,
    horizon_days: int = 5,
) -> tuple[list[dict], str]:
    subset_config = experiment_config.get("diagnostic_feature_subsets", {})
    rows: list[dict] = []
    for subset_name, configured_columns in subset_config.items():
        feature_columns = [column for column in configured_columns if column in feature_frame.columns]
        if not feature_columns:
            continue
        model_frame = TargetBuilder().build(
            feature_frame,
            TargetSpec(forecast_horizon_days=horizon_days),
            required_feature_columns=feature_columns,
        )
        split_frames = Splitter().split(
            model_frame,
            SplitSpec(
                train_fraction=experiment_config["train_fraction"],
                validation_fraction=experiment_config["validation_fraction"],
            ),
        )
        baseline_results = run_baselines(split_frames=split_frames, feature_columns=feature_columns)
        rows.append(
            {
                "subset_name": subset_name,
                "feature_count": len(feature_columns),
                "validation_accuracy": baseline_results.classification_metrics["validation"]["accuracy"],
                "test_accuracy": baseline_results.classification_metrics["test"]["accuracy"],
                "test_naive_accuracy": baseline_results.classification_metrics["test_naive_direction"]["accuracy"],
                "accuracy_advantage_vs_naive": baseline_results.classification_metrics["test"]["accuracy"]
                - baseline_results.classification_metrics["test_naive_direction"]["accuracy"],
                "test_precision": baseline_results.classification_metrics["test"]["precision"],
                "test_recall": baseline_results.classification_metrics["test"]["recall"],
                "test_rmse": baseline_results.regression_metrics["test"]["rmse"],
            }
        )

    comparison = pd.DataFrame(rows).sort_values("test_accuracy", ascending=False).reset_index(drop=True)
    best_row = comparison.iloc[0]
    observations = [
        (
            f"`{int(horizon_days)}d` 目标下表现最好的特征子集是 "
            f"`{best_row['subset_name']}`，测试集准确率为 `{best_row['test_accuracy']:.4f}`。"
        ),
        f"它相对朴素方向基线的准确率优势为 `{best_row['accuracy_advantage_vs_naive']:.4f}`。",
    ]
    if best_row["accuracy_advantage_vs_naive"] > 0:
        observations.append("这说明当前更有希望的方向是先收缩特征空间、保留高信噪比特征，而不是直接继续加变量。")
    else:
        observations.append("这说明即便做了特征子集拆分，当前信息量仍不足，需要继续回到目标定义和特征构造。")

    return rows, "\n".join(f"- {item}" for item in observations)


def generate_feature_subset_report(
    settings: Settings,
    subset_rows: list[dict],
    observations_markdown: str,
    horizon_days: int = 5,
) -> None:
    comparison = pd.DataFrame(subset_rows).sort_values("test_accuracy", ascending=False).reset_index(drop=True)
    report_markdown = f"""# v0.1 特征子集对比报告

## 1. 目的

这份报告比较 `{horizon_days}d` 目标下，不同特征子集（Feature Subsets）的表现，帮助判断当前更应该做“加特征”还是“减特征”。

## 2. 对比表

{render_markdown_table(comparison, index=False)}

字段说明：

- `subset_name`：特征子集名称
- `feature_count`：特征数量
- `validation_accuracy`：验证集准确率
- `test_accuracy`：测试集准确率
- `test_naive_accuracy`：朴素方向基线准确率
- `accuracy_advantage_vs_naive`：相对朴素基线的准确率差值
- `test_precision`：测试集精确率（Precision）
- `test_recall`：测试集召回率（Recall）
- `test_rmse`：对应回归诊断任务的测试集 RMSE

## 3. 当前观察

{observations_markdown}

## 4. 解释原则

- 如果较小的特征子集优于全量特征，通常说明部分外生变量在当前任务下更像噪声而不是增量信息。
- 如果价格类特征（Price-derived Features）优于宏观类特征，说明当前预测期限可能更偏短中期价格行为，而不是宏观慢变量驱动。
- 如果宏观特征单独表现仍有一定解释力，说明它们适合做辅助变量，但未必适合直接与所有价格特征混合。

## 5. 下一步建议

1. 先围绕最优特征子集继续做稳定性诊断，而不是立刻扩展到更多特征。
2. 对最优子集做滚动窗口（Rolling Window）与不同样本区间的稳健性检查。
3. 如果最优子集明显优于全量特征，后续建模默认先以该子集为基线。
"""
    write_markdown(settings.reports_dir / "v01_feature_subset_report_zh.md", report_markdown)
    write_json(
        settings.reports_dir / "v01_feature_subset_report.json",
        {"rows": subset_rows, "horizon_days": horizon_days},
    )


def generate_ml_model_comparison_report(
    settings: Settings,
    experiment_config: dict,
    feature_frame: pd.DataFrame,
) -> None:
    ml_config = experiment_config.get("ml_experiment", {})
    target_horizon_days = ml_config.get("target_horizon_days", 5)
    subset_name = ml_config.get("feature_subset", "gold_only")
    subset_map = experiment_config.get("diagnostic_feature_subsets", {})
    feature_columns = [column for column in subset_map.get(subset_name, []) if column in feature_frame.columns]
    if not feature_columns:
        raise ValueError(f"No feature columns found for ML subset: {subset_name}")

    model_frame = TargetBuilder().build(
        feature_frame,
        TargetSpec(forecast_horizon_days=target_horizon_days),
        required_feature_columns=feature_columns,
    )
    split_frames = Splitter().split(
        model_frame,
        SplitSpec(
            train_fraction=experiment_config["train_fraction"],
            validation_fraction=experiment_config["validation_fraction"],
        ),
    )
    candidate_models = ml_config.get("candidate_models", ["logistic_regression"])
    comparison_results = compare_classification_models(
        split_frames=split_frames,
        feature_columns=feature_columns,
        candidate_models=candidate_models,
    )

    rows = []
    for result in comparison_results:
        rows.append(
            {
                "model_name": result.model_name,
                "train_accuracy": result.metrics_by_split["train"]["accuracy"],
                "validation_accuracy": result.metrics_by_split["validation"]["accuracy"],
                "test_accuracy": result.metrics_by_split["test"]["accuracy"],
                "train_precision": result.metrics_by_split["train"]["precision"],
                "validation_precision": result.metrics_by_split["validation"]["precision"],
                "test_precision": result.metrics_by_split["test"]["precision"],
                "train_recall": result.metrics_by_split["train"]["recall"],
                "validation_recall": result.metrics_by_split["validation"]["recall"],
                "test_recall": result.metrics_by_split["test"]["recall"],
            }
        )

    comparison = (
        pd.DataFrame(rows)
        .sort_values(["validation_accuracy", "model_name"], ascending=[False, True])
        .reset_index(drop=True)
    )
    best_row = comparison.iloc[0]
    report_markdown = f"""# v0.1 机器学习模型对比报告

## 1. 当前机器学习实验设置

- 目标期限（Target Horizon）：`{target_horizon_days}d`
- 特征子集（Feature Subset）：`{subset_name}`
- 训练集（Train）样本量：`{len(split_frames.train)}`
- 验证集（Validation）样本量：`{len(split_frames.validation)}`
- 测试集（Test）样本量：`{len(split_frames.test)}`

## 2. 为什么先做训练集 / 验证集 / 测试集

- 训练集：用于拟合模型参数
- 验证集：用于比较模型、调参和筛选方向
- 测试集：只用于最终检验，不参与模型选择

这一步的目标是“先确认模型是否有稳定泛化能力（Generalization）”，而不是直接进入回测。

## 3. 模型对比表

{render_markdown_table(comparison, index=False)}

## 4. 当前观察

- 当前验证集表现最好的模型是 `{best_row['model_name']}`。
- 它的验证集准确率约为 `{best_row['validation_accuracy']:.4f}`，测试集准确率约为 `{best_row['test_accuracy']:.4f}`。
- 如果训练集明显高于验证集和测试集，需要警惕过拟合（Overfitting）。
- 只有当测试集结果稳定后，预测输出才值得进入信号层（Signal Layer）和回测层（Backtesting Layer）。

## 5. 当前阶段与回测的关系

- 机器学习阶段解决的是“能不能预测”
- 回测阶段解决的是“即使能预测，能不能形成可交易规则”

所以当前顺序应当是：

1. 先确定目标定义和特征集
2. 再比较模型
3. 再把最稳定的模型带入信号与回测

## 6. 下一步建议

1. 先围绕验证集最优模型做稳健性检查。
2. 对训练集、验证集、测试集的差异做过拟合诊断。
3. 如果测试集也保持稳定，再进入最小信号生成与回测原型。
"""
    write_markdown(settings.reports_dir / "v01_ml_model_comparison_report_zh.md", report_markdown)
    write_json(
        settings.reports_dir / "v01_ml_model_comparison_report.json",
        {
            "rows": rows,
            "target_horizon_days": target_horizon_days,
            "feature_subset": subset_name,
        },
    )


def generate_ml_optimization_report(settings: Settings, experiment_config: dict, feature_frame: pd.DataFrame):
    ml_config = experiment_config.get("ml_experiment", {})
    target_horizon_days = ml_config.get("target_horizon_days", 5)
    subset_name = ml_config.get("feature_subset", "gold_only")
    subset_map = experiment_config.get("diagnostic_feature_subsets", {})
    feature_columns = [column for column in subset_map.get(subset_name, []) if column in feature_frame.columns]
    if not feature_columns:
        raise ValueError(f"No feature columns found for ML optimization subset: {subset_name}")

    model_frame = TargetBuilder().build(
        feature_frame,
        TargetSpec(forecast_horizon_days=target_horizon_days),
        required_feature_columns=feature_columns,
    )
    split_frames = Splitter().split(
        model_frame,
        SplitSpec(
            train_fraction=experiment_config["train_fraction"],
            validation_fraction=experiment_config["validation_fraction"],
        ),
    )
    optimization = optimize_model_spec(split_frames=split_frames, feature_columns=feature_columns, overfit_penalty=0.6)
    comparison = pd.DataFrame(optimization.rows)
    best = comparison.iloc[0]

    report_markdown = f"""# v0.1 机器学习优化与防过拟合报告

## 1. 优化目标

当前优化不是单纯追求训练集最高准确率，而是同时考虑：

- 验证集准确率（Validation Accuracy）
- 训练集与验证集差距（Generalization Gap）
- 模型复杂度带来的过拟合风险（Overfitting Risk）

评分思路：

```text
objective_score = validation_accuracy - 0.6 * max(train_accuracy - validation_accuracy, 0)
```

## 2. 当前优化设置

- 目标期限（Target Horizon）：`{target_horizon_days}d`
- 特征子集（Feature Subset）：`{subset_name}`
- 过拟合惩罚系数（Overfit Penalty）：`0.6`

## 3. 候选模型排序

{render_markdown_table(comparison.head(12), index=False)}

## 4. 当前选中的最优模型

- 模型名称：`{best['model_name']}`
- 模型参数：`{best['model_params']}`
- 训练集准确率：`{best['train_accuracy']:.4f}`
- 验证集准确率：`{best['validation_accuracy']:.4f}`
- 测试集准确率：`{best['test_accuracy']:.4f}`
- 泛化落差（Generalization Gap）：`{best['generalization_gap']:.4f}`
- 综合评分（Objective Score）：`{best['objective_score']:.4f}`

## 5. 为什么说这是“更适合当前阶段”的模型

- 它不是单纯训练集最强的模型
- 它是在验证集表现和过拟合控制之间更平衡的模型
- 因为我们后面还要进入样本外回测，所以宁可先保守，也不要把复杂度堆得过高

## 6. 下一步

这份优化结果将直接作为当前十年回测原型的默认模型来源。
"""
    write_markdown(settings.reports_dir / "v01_ml_optimization_report_zh.md", report_markdown)
    write_json(
        settings.reports_dir / "v01_ml_optimization_report.json",
        {
            "rows": optimization.rows,
            "best_spec": {
                "model_name": optimization.best_spec.model_name,
                "model_params": optimization.best_spec.model_params,
            },
        },
    )
    return optimization.best_spec


def generate_backtest_report(
    settings: Settings,
    experiment_config: dict,
    feature_frame: pd.DataFrame,
    selected_model_spec,
) -> None:
    backtest_config = experiment_config.get("backtest_experiment", {})
    target_horizon_days = backtest_config.get("target_horizon_days", 5)
    subset_name = backtest_config.get("feature_subset", "gold_only")
    subset_map = experiment_config.get("diagnostic_feature_subsets", {})
    feature_columns = [column for column in subset_map.get(subset_name, []) if column in feature_frame.columns]
    if not feature_columns:
        raise ValueError(f"No feature columns found for backtest subset: {subset_name}")

    model_frame = TargetBuilder().build(
        feature_frame,
        TargetSpec(forecast_horizon_days=target_horizon_days),
        required_feature_columns=feature_columns,
    )
    configured_model_name = backtest_config.get("model_name")
    configured_model_params = backtest_config.get("model_params", {})
    model_name = configured_model_name or selected_model_spec.model_name
    model_params = configured_model_params or selected_model_spec.model_params

    wf_config = WalkForwardConfig(
        model_name=model_name,
        model_params=model_params,
        feature_columns=feature_columns,
        target_horizon_days=target_horizon_days,
        lookback_years=backtest_config.get("lookback_years", 10),
        initial_train_years=backtest_config.get("initial_train_years", 3),
        retrain_frequency_days=backtest_config.get("retrain_frequency_days", 21),
    )
    prediction_frame = generate_walk_forward_predictions(model_frame, wf_config)
    backtest_result = run_long_flat_backtest(
        prediction_frame=prediction_frame,
        transaction_cost_bps=backtest_config.get("transaction_cost_bps", 5),
    )

    write_dataframe_csv(settings.data_processed_dir / "backtest_predictions_10y.csv", backtest_result.daily_frame)
    write_json(settings.reports_dir / "v01_backtest_10y_report.json", backtest_result.metrics)

    figure, ax = plt.subplots(figsize=(12, 6))
    backtest_result.daily_frame.plot(x="date", y="strategy_equity", ax=ax, label="Strategy Equity")
    backtest_result.daily_frame.plot(x="date", y="benchmark_equity", ax=ax, label="Benchmark Equity")
    ax.set_title("10Y Walk-Forward Backtest Equity Curve")
    ax.set_ylabel("Equity")
    figure.tight_layout()
    figure.savefig(settings.reports_dir / "v01_backtest_10y_equity.png", dpi=150)
    plt.close(figure)

    metrics = backtest_result.metrics
    report_markdown = f"""# v0.1 十年回测报告

## 1. 回测设置

- 回测窗口（Lookback Window）：最近 `10` 年
- 目标期限（Target Horizon）：`{target_horizon_days}d`
- 特征子集（Feature Subset）：`{subset_name}`
- 模型（Model）：`{wf_config.model_name}`
- 模型参数（Model Params）：`{wf_config.model_params}`
- 初始训练窗口（Initial Train Window）：`{wf_config.initial_train_years}` 年
- 再训练频率（Retrain Frequency）：每 `21` 个交易日
- 交易成本（Transaction Costs）：`{backtest_config.get("transaction_cost_bps", 5)}` bps
- 信号规则（Signal Rule）：预测为上涨则次日做多，否则空仓（Long / Flat）

## 2. 为什么这版回测仍然是原型

- 这是滚动训练（Walk-forward Training）下的样本外（Out-of-sample）回测，不是整段历史一次性拟合后回看。
- 但它仍然是最小原型，因为：
  - 还没有滑点（Slippage）模型
  - 还没有更细的成交规则
  - 还没有持仓上限和风险预算
  - 还没有完整绩效归因

## 3. 核心指标

| 指标 | 数值 |
| --- | ---: |
| 策略总收益（Strategy Total Return） | {metrics['strategy_total_return']:.4f} |
| 基准总收益（Benchmark Total Return） | {metrics['benchmark_total_return']:.4f} |
| 策略年化收益（Strategy Annualized Return） | {metrics['strategy_annualized_return']:.4f} |
| 基准年化收益（Benchmark Annualized Return） | {metrics['benchmark_annualized_return']:.4f} |
| 策略年化波动（Strategy Annualized Volatility） | {metrics['strategy_annualized_volatility']:.4f} |
| 基准年化波动（Benchmark Annualized Volatility） | {metrics['benchmark_annualized_volatility']:.4f} |
| 策略夏普（Strategy Sharpe） | {metrics['strategy_sharpe']:.4f} |
| 基准夏普（Benchmark Sharpe） | {metrics['benchmark_sharpe']:.4f} |
| 策略最大回撤（Strategy Max Drawdown） | {metrics['strategy_max_drawdown']:.4f} |
| 基准最大回撤（Benchmark Max Drawdown） | {metrics['benchmark_max_drawdown']:.4f} |
| 平均仓位（Average Position） | {metrics['average_position']:.4f} |
| 年化换手（Annualized Turnover） | {metrics['annualized_turnover']:.4f} |

## 4. 解释原则

- 如果策略收益优于基准，但换手或回撤明显更差，需要继续检查交易实现是否值得。
- 如果策略只在训练上看起来好，而样本外回测没有改善，就不能宣称模型有交易价值。
- 当前回测是“机器学习输出 -> 最小信号 -> 最小执行”的第一版，不是最终交易系统。

## 5. 当前结论

- 只有当十年回测、训练/验证/测试结果、以及特征诊断这三者方向一致时，模型才值得继续推进。
- 如果十年回测结果与静态测试集结果冲突，应优先相信滚动样本外（Walk-forward OOS）结果。

## 6. 结果文件

- `data/processed/backtest_predictions_10y.csv`
- `reports/generated/v01_backtest_10y_report.json`
- `reports/generated/v01_backtest_10y_equity.png`

## 7. 下一步建议

1. 先检查这版十年回测是否优于买入持有（Buy and Hold）。
2. 再比较 `logistic_regression` 与 `random_forest` 的十年回测差异。
3. 如果样本外结果仍然稳定，再进入更完整的信号与风险控制层。
"""
    write_markdown(settings.reports_dir / "v01_backtest_10y_report_zh.md", report_markdown)


def run_pipeline(mode: str = "sample", project_root: Path | None = None) -> dict:
    settings = Settings.from_env(project_root=project_root)
    settings.ensure_local_dirs()

    dataset_specs = load_dataset_specs(settings.project_root)
    experiment_config = load_experiment_config(settings.project_root)

    if mode == "sample":
        standard_frames = generate_sample_standard_frames(dataset_specs)
    elif mode == "remote":
        standard_frames = fetch_remote_standard_frames(settings, dataset_specs)
    else:
        raise ValueError(f"Unsupported mode: {mode}")

    feature_frame, model_frame = build_v01_frames(
        standard_frames,
        target_horizon_days=1,
        required_feature_columns=experiment_config["classification_feature_columns"],
    )
    split_frames = Splitter().split(
        model_frame,
        SplitSpec(
            train_fraction=experiment_config["train_fraction"],
            validation_fraction=experiment_config["validation_fraction"],
        ),
    )
    baseline_results = run_baselines(
        split_frames=split_frames,
        feature_columns=experiment_config["classification_feature_columns"],
    )

    write_dataframe_csv(settings.data_interim_dir / "feature_frame.csv", feature_frame)
    write_dataframe_csv(settings.data_processed_dir / "model_frame.csv", model_frame)
    write_data_dictionary(settings, standard_frames)
    generate_eda_outputs(settings, feature_frame)
    generate_model_report(settings, baseline_results, split_frames)
    generate_diagnosis_report(settings, feature_frame, model_frame, baseline_results, split_frames)
    horizon_rows, observations_markdown = build_horizon_diagnostics(feature_frame, experiment_config)
    generate_horizon_comparison_report(settings, horizon_rows, observations_markdown)
    subset_rows, subset_observations_markdown = build_feature_subset_diagnostics(
        feature_frame,
        experiment_config,
        horizon_days=5,
    )
    generate_feature_subset_report(settings, subset_rows, subset_observations_markdown, horizon_days=5)
    generate_ml_model_comparison_report(settings, experiment_config, feature_frame)
    selected_model_spec = generate_ml_optimization_report(settings, experiment_config, feature_frame)
    generate_backtest_report(settings, experiment_config, feature_frame, selected_model_spec)

    return {
        "mode": mode,
        "feature_rows": len(feature_frame),
        "model_rows": len(model_frame),
        "classification_metrics": baseline_results.classification_metrics,
        "regression_metrics": baseline_results.regression_metrics,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the quant gold v0.1 baseline pipeline.")
    parser.add_argument("--mode", choices=("sample", "remote"), default="sample")
    arguments = parser.parse_args()
    result = run_pipeline(mode=arguments.mode)
    print(result)


if __name__ == "__main__":
    main()
