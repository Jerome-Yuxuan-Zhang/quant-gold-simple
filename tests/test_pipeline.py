import shutil
import tempfile
from pathlib import Path

from quant_gold.pipelines.v01_pipeline import run_pipeline


def test_sample_pipeline_runs_end_to_end() -> None:
    source_root = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir) / "repo"
        shutil.copytree(source_root, temp_root)
        result = run_pipeline(mode="sample", project_root=temp_root)
        assert result["mode"] == "sample"
        assert result["feature_rows"] > 100
        assert "test" in result["classification_metrics"]
