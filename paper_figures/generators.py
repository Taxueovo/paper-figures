"""Built-in generators that turn real tabular/spec data into publication figures."""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any


def _pyplot(config: dict[str, Any]):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    font_family = config["font_family"]
    updates: dict[str, Any] = {
        "font.family": font_family,
        "font.size": config["font_size"]["label"],
        "axes.labelsize": config["font_size"]["label"],
        "axes.titlesize": config["font_size"]["title"],
        "xtick.labelsize": config["font_size"]["tick"],
        "ytick.labelsize": config["font_size"]["tick"],
        "legend.fontsize": config["font_size"]["legend"],
        "lines.linewidth": config["line_width"],
        "lines.markersize": config["marker_size"],
        "axes.spines.top": config["spine_top"],
        "axes.spines.right": config["spine_right"],
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.05,
    }
    if font_family == "serif" and config.get("font_serif"):
        updates["font.serif"] = config["font_serif"]
    if font_family == "sans-serif" and config.get("font_sans"):
        updates["font.sans-serif"] = config["font_sans"]
    plt.rcParams.update(updates)
    return plt


def _read_csv(path: Path):
    import pandas as pd

    if not path.is_file() or path.suffix.lower() != ".csv":
        raise ValueError(f"Expected an existing CSV file: {path}")
    frame = pd.read_csv(path)
    if frame.empty:
        raise ValueError(f"CSV contains no rows: {path}")
    if frame.columns.duplicated().any():
        raise ValueError("CSV column names must be unique")
    return frame


def _numeric_columns(frame) -> list[str]:
    return [str(column) for column in frame.select_dtypes(include="number").columns]


def _require_columns(frame, columns: Sequence[str]) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ValueError(f"CSV is missing columns: {', '.join(missing)}")


def _require_numeric(frame, columns: Sequence[str]) -> None:
    import numpy as np

    _require_columns(frame, columns)
    non_numeric = [column for column in columns if column not in _numeric_columns(frame)]
    if non_numeric:
        raise ValueError(f"Columns must be numeric: {', '.join(non_numeric)}")
    if not np.isfinite(frame[list(columns)].to_numpy(dtype=float)).all():
        raise ValueError(
            f"Numeric columns contain missing or infinite values: {', '.join(columns)}"
        )


def _figure_size(
    config: dict[str, Any], width: str, ratio: float | None = None
) -> tuple[float, float]:
    figure_width = float(config["fig_width"][width])
    return figure_width, figure_width * float(ratio or config["fig_height_ratio"])


def save_triplet(figure, output_dir: Path, name: str, config: dict[str, Any]) -> dict[str, Path]:
    import re

    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", name):
        raise ValueError("name may contain only letters, numbers, dots, underscores, and hyphens")
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {extension: output_dir / f"{name}.{extension}" for extension in ("pdf", "svg", "png")}
    temporary = {
        extension: path.with_name(f".{path.name}.tmp") for extension, path in outputs.items()
    }
    try:
        figure.savefig(temporary["pdf"], format="pdf")
        figure.savefig(temporary["svg"], format="svg")
        figure.savefig(temporary["png"], format="png", dpi=config["dpi"])
        for extension, path in outputs.items():
            temporary[extension].replace(path)
    finally:
        for path in temporary.values():
            path.unlink(missing_ok=True)
    return outputs


def training_curves(
    data: Path,
    output_dir: Path,
    name: str,
    config: dict[str, Any],
    *,
    x: str | None = None,
    series: Sequence[str] | None = None,
) -> dict[str, Path]:
    frame = _read_csv(data)
    numeric = _numeric_columns(frame)
    x_column = x or ("epoch" if "epoch" in frame.columns else numeric[0] if numeric else None)
    if not x_column:
        raise ValueError("Training data needs at least one numeric x-axis column")
    selected = list(series or [column for column in numeric if column != x_column])
    if not selected:
        raise ValueError("Training data needs at least one numeric series column")
    _require_numeric(frame, [x_column, *selected])
    plt = _pyplot(config)
    figure, axis = plt.subplots(figsize=_figure_size(config, "single"))
    styles = ["-", "--", "-.", ":"]
    markers = ["o", "s", "^", "D", "v"]
    for index, column in enumerate(selected):
        axis.plot(
            frame[x_column],
            frame[column],
            styles[index % len(styles)],
            marker=markers[index % len(markers)],
            markevery=max(1, len(frame) // 12),
            label=column.replace("_", " ").title(),
        )
    axis.set_xlabel(x_column.replace("_", " ").title())
    axis.set_ylabel("Value")
    axis.grid(bool(config.get("grid")))
    if config.get("grid"):
        axis.grid(alpha=0.25)
    axis.legend(frameon=False)
    figure.tight_layout()
    outputs = save_triplet(figure, output_dir, name, config)
    plt.close(figure)
    return outputs


def scatter_error(
    data: Path,
    output_dir: Path,
    name: str,
    config: dict[str, Any],
    *,
    truth: str | None = None,
    prediction: str | None = None,
) -> dict[str, Path]:
    import numpy as np

    frame = _read_csv(data)
    numeric = _numeric_columns(frame)
    truth_column = truth or (
        "y_true" if "y_true" in frame.columns else numeric[0] if numeric else None
    )
    prediction_column = prediction or (
        "y_pred" if "y_pred" in frame.columns else numeric[1] if len(numeric) > 1 else None
    )
    if not truth_column or not prediction_column or truth_column == prediction_column:
        raise ValueError("Scatter data needs two distinct numeric truth and prediction columns")
    _require_numeric(frame, [truth_column, prediction_column])
    values = frame[[truth_column, prediction_column]]
    if len(values) < 2:
        raise ValueError("Scatter data needs at least two complete rows")
    y_true = values[truth_column].to_numpy(dtype=float)
    y_pred = values[prediction_column].to_numpy(dtype=float)
    residual = y_pred - y_true
    mae = float(np.mean(np.abs(residual)))
    denominator = float(np.sum((y_true - np.mean(y_true)) ** 2))
    r_squared = 1.0 - float(np.sum(residual**2)) / denominator if denominator else float("nan")
    plt = _pyplot(config)
    figure, (scatter_axis, error_axis) = plt.subplots(
        1, 2, figsize=_figure_size(config, "double", 0.45)
    )
    scatter_axis.scatter(y_true, y_pred, s=14, alpha=0.55, color="#2456D1", edgecolors="none")
    low, high = float(min(y_true.min(), y_pred.min())), float(max(y_true.max(), y_pred.max()))
    scatter_axis.plot(
        [low, high], [low, high], "--", color="#68778A", linewidth=1, label="Identity"
    )
    scatter_axis.set(
        xlabel=truth_column.replace("_", " ").title(),
        ylabel=prediction_column.replace("_", " ").title(),
    )
    score = (
        f"MAE = {mae:.3g}" if np.isnan(r_squared) else f"$R^2$ = {r_squared:.3f}\nMAE = {mae:.3g}"
    )
    scatter_axis.text(0.04, 0.96, score, transform=scatter_axis.transAxes, va="top")
    error_axis.hist(
        residual,
        bins=min(30, max(8, int(len(residual) ** 0.5))),
        color="#2456D1",
        alpha=0.8,
        edgecolor="white",
    )
    error_axis.axvline(
        float(np.mean(residual)), color="#C93A35", linestyle="--", label="Mean error"
    )
    error_axis.set(xlabel="Prediction error", ylabel="Count")
    error_axis.legend(frameon=False)
    figure.tight_layout()
    outputs = save_triplet(figure, output_dir, name, config)
    plt.close(figure)
    return outputs


def bar_chart(
    data: Path,
    output_dir: Path,
    name: str,
    config: dict[str, Any],
    *,
    category: str | None = None,
    series: Sequence[str] | None = None,
) -> dict[str, Path]:
    import numpy as np

    frame = _read_csv(data)
    numeric = _numeric_columns(frame)
    category_column = category or next(
        (str(column) for column in frame.columns if str(column) not in numeric),
        str(frame.columns[0]),
    )
    selected = list(series or [column for column in numeric if column != category_column])
    if not selected:
        raise ValueError("Bar data needs at least one numeric value column")
    _require_columns(frame, [category_column, *selected])
    _require_numeric(frame, selected)
    if frame[category_column].isna().any():
        raise ValueError(f"Category column contains missing values: {category_column}")
    plt = _pyplot(config)
    figure, axis = plt.subplots(
        figsize=_figure_size(config, "double", 0.5 if len(frame) > 6 else 0.42)
    )
    positions = np.arange(len(frame))
    width = 0.8 / len(selected)
    colors = ["#2456D1", "#DD8452", "#2F855A", "#8172B3", "#C93A35"]
    for index, column in enumerate(selected):
        offset = (index - (len(selected) - 1) / 2) * width
        axis.bar(
            positions + offset,
            frame[column],
            width,
            label=column.replace("_", " ").title(),
            color=colors[index % len(colors)],
        )
    axis.set_xticks(
        positions,
        frame[category_column].astype(str),
        rotation=25 if len(frame) > 6 else 0,
        ha="right" if len(frame) > 6 else "center",
    )
    axis.set_xlabel(category_column.replace("_", " ").title())
    axis.set_ylabel("Value")
    axis.legend(
        frameon=False,
        loc="lower center",
        bbox_to_anchor=(0.5, 1.01),
        ncol=min(3, len(selected)),
    )
    figure.tight_layout()
    outputs = save_triplet(figure, output_dir, name, config)
    plt.close(figure)
    return outputs


def sensitivity(
    data: Path,
    output_dir: Path,
    name: str,
    config: dict[str, Any],
    *,
    x: str | None = None,
    y: str | None = None,
    value: str | None = None,
) -> dict[str, Path]:
    frame = _read_csv(data)
    numeric = _numeric_columns(frame)
    x_column = x or (numeric[0] if numeric else None)
    value_column = value or (numeric[-1] if len(numeric) > 1 else None)
    if not x_column or not value_column or x_column == value_column:
        raise ValueError("Sensitivity data needs distinct parameter and value columns")
    _require_numeric(frame, [x_column, value_column] + ([y] if y else []))
    plt = _pyplot(config)
    figure, axis = plt.subplots(figsize=_figure_size(config, "single", 0.8 if y else None))
    if y:
        if frame.duplicated([y, x_column]).any():
            raise ValueError("Sensitivity heatmap contains duplicate x/y coordinate pairs")
        pivot = frame.pivot(index=y, columns=x_column, values=value_column)
        if pivot.isna().any().any():
            raise ValueError("Sensitivity heatmap must provide a complete rectangular x/y grid")
        image = axis.imshow(pivot.to_numpy(), cmap="viridis", aspect="auto")
        axis.set_xticks(range(len(pivot.columns)), [str(item) for item in pivot.columns])
        axis.set_yticks(range(len(pivot.index)), [str(item) for item in pivot.index])
        axis.set(xlabel=x_column.replace("_", " ").title(), ylabel=y.replace("_", " ").title())
        figure.colorbar(image, ax=axis, label=value_column.replace("_", " ").title())
    else:
        ordered = frame.sort_values(x_column)
        axis.plot(ordered[x_column], ordered[value_column], "-o", color="#2456D1")
        axis.set(
            xlabel=x_column.replace("_", " ").title(), ylabel=value_column.replace("_", " ").title()
        )
        axis.grid(True, alpha=0.25)
    figure.tight_layout()
    outputs = save_triplet(figure, output_dir, name, config)
    plt.close(figure)
    return outputs


def architecture(
    data: Path, output_dir: Path, name: str, config: dict[str, Any]
) -> dict[str, Path]:
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

    with data.open(encoding="utf-8") as handle:
        spec = json.load(handle)
    nodes = spec.get("nodes") if isinstance(spec, dict) else None
    edges = spec.get("edges", []) if isinstance(spec, dict) else []
    if not isinstance(nodes, list) or not nodes:
        raise ValueError("Architecture JSON must contain a non-empty nodes list")
    if not all(isinstance(node, dict) for node in nodes):
        raise ValueError("Every architecture node must be an object")
    if not isinstance(edges, list):
        raise ValueError("Architecture edges must be a list")
    identifiers = [node.get("id") for node in nodes]
    if len(identifiers) != len(nodes) or len(set(identifiers)) != len(nodes):
        raise ValueError("Every architecture node needs a unique id")
    positions: dict[str, tuple[float, float]] = {}
    for index, node in enumerate(nodes):
        positions[node["id"]] = (float(node.get("x", index * 2.2)), float(node.get("y", 0)))
    import math

    if any(not math.isfinite(value) for position in positions.values() for value in position):
        raise ValueError("Architecture node coordinates must be finite numbers")
    if any(
        not isinstance(edge, list)
        or len(edge) != 2
        or edge[0] not in positions
        or edge[1] not in positions
        for edge in edges
    ):
        raise ValueError("Every edge must be [source, target] and reference known node ids")
    plt = _pyplot(config)
    figure, axis = plt.subplots(figsize=_figure_size(config, "double", 0.42))
    palette = {"input": "#DCEAFE", "module": "#E5E1FF", "fusion": "#D9F4E8", "output": "#FFE0BA"}
    for source, target in edges:
        sx, sy = positions[source]
        tx, ty = positions[target]
        axis.add_patch(
            FancyArrowPatch(
                (sx + 0.75, sy),
                (tx - 0.75, ty),
                arrowstyle="-|>",
                mutation_scale=12,
                linewidth=1.3,
                color="#607086",
                connectionstyle="arc3,rad=0.05",
            )
        )
    for node in nodes:
        x_position, y_position = positions[node["id"]]
        color = palette.get(str(node.get("group", "module")), "#E8EFFC")
        axis.add_patch(
            FancyBboxPatch(
                (x_position - 0.75, y_position - 0.35),
                1.5,
                0.7,
                boxstyle="round,pad=0.08,rounding_size=0.12",
                facecolor=color,
                edgecolor="#344054",
                linewidth=1.1,
            )
        )
        axis.text(
            x_position,
            y_position,
            str(node.get("label", node["id"])),
            ha="center",
            va="center",
            weight="bold",
        )
    xs, ys = zip(*positions.values(), strict=True)
    axis.set_xlim(min(xs) - 1.2, max(xs) + 1.2)
    axis.set_ylim(min(ys) - 1.0, max(ys) + 1.0)
    axis.set_aspect("equal", adjustable="box")
    axis.axis("off")
    figure.tight_layout()
    outputs = save_triplet(figure, output_dir, name, config)
    plt.close(figure)
    return outputs
