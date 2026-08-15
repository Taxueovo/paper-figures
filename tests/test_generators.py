import json

import pandas as pd
import pytest

from paper_figures.config import style_for
from paper_figures.generators import (
    architecture,
    bar_chart,
    scatter_error,
    sensitivity,
    training_curves,
)
from paper_figures.validation import validate_triplet


@pytest.mark.parametrize(
    ("name", "frame", "generator"),
    [
        ("training", pd.DataFrame({"epoch": [1, 2, 3], "loss": [0.9, 0.5, 0.3]}), training_curves),
        ("scatter", pd.DataFrame({"y_true": [1, 2, 3], "y_pred": [1.1, 1.9, 3.2]}), scatter_error),
        ("bar", pd.DataFrame({"method": ["A", "B"], "score": [0.8, 0.9]}), bar_chart),
        (
            "sensitivity",
            pd.DataFrame({"rate": [0.1, 0.2, 0.3], "score": [0.7, 0.9, 0.8]}),
            sensitivity,
        ),
    ],
)
def test_csv_generators_produce_valid_triplets(tmp_path, name, frame, generator):
    data = tmp_path / f"{name}.csv"
    frame.to_csv(data, index=False)
    output = tmp_path / "export"
    generator(data, output, name, style_for("generic"))
    assert validate_triplet(output, name, style_for("generic")) == []


def test_architecture_generator_produces_valid_triplet(tmp_path):
    data = tmp_path / "architecture.json"
    data.write_text(
        json.dumps(
            {
                "nodes": [
                    {"id": "input", "label": "Input", "group": "input", "x": 0},
                    {"id": "model", "label": "Model", "group": "module", "x": 2.5},
                ],
                "edges": [["input", "model"]],
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "export"
    architecture(data, output, "architecture", style_for("generic"))
    assert validate_triplet(output, "architecture", style_for("generic")) == []


def test_sensitivity_rejects_duplicate_heatmap_coordinates(tmp_path):
    data = tmp_path / "duplicates.csv"
    pd.DataFrame({"alpha": [0.1, 0.1], "beta": [1, 1], "score": [0.8, 0.9]}).to_csv(
        data, index=False
    )
    with pytest.raises(ValueError, match="duplicate"):
        sensitivity(
            data,
            tmp_path / "export",
            "heatmap",
            style_for("generic"),
            x="alpha",
            y="beta",
            value="score",
        )
