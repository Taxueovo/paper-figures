"""Journal style presets and validated configuration loading."""

from __future__ import annotations

from copy import deepcopy
from math import isfinite
from pathlib import Path
from typing import Any

from .io_utils import load_json_object

_BASE: dict[str, Any] = {
    "line_width": 1.5,
    "marker_size": 6,
    "dpi": 300,
    "grid": False,
    "spine_top": False,
    "spine_right": False,
}

JOURNAL_PRESETS: dict[str, dict[str, Any]] = {
    "generic": {
        **_BASE,
        "font_family": "serif",
        "font_serif": ["DejaVu Serif", "Times New Roman"],
        "font_size": {"label": 11, "tick": 10, "legend": 10, "title": 12},
        "fig_width": {"single": 4.0, "double": 7.5},
        "fig_height_ratio": 0.75,
    },
    "ieee": {
        **_BASE,
        "font_family": "serif",
        "font_serif": ["Times New Roman", "DejaVu Serif"],
        "font_size": {"label": 10, "tick": 9, "legend": 9, "title": 11},
        "fig_width": {"single": 3.5, "double": 7.16},
        "fig_height_ratio": 0.75,
    },
    "nature": {
        **_BASE,
        "font_family": "sans-serif",
        "font_sans": ["Arial", "Helvetica", "DejaVu Sans"],
        "font_size": {"label": 9, "tick": 8, "legend": 8, "title": 10},
        "fig_width": {"single": 3.5, "double": 7.0},
        "fig_height_ratio": 0.8,
        "line_width": 1.2,
        "marker_size": 5,
    },
    "elsevier": {
        **_BASE,
        "font_family": "serif",
        "font_serif": ["Times New Roman", "Georgia", "DejaVu Serif"],
        "font_size": {"label": 10, "tick": 9, "legend": 9, "title": 11},
        "fig_width": {"single": 3.54, "double": 7.28},
        "fig_height_ratio": 0.75,
    },
    "acm": {
        **_BASE,
        "font_family": "serif",
        "font_serif": ["Times New Roman", "Libertine", "DejaVu Serif"],
        "font_size": {"label": 9, "tick": 8, "legend": 8, "title": 10},
        "fig_width": {"single": 3.3, "double": 6.75},
        "fig_height_ratio": 0.75,
        "line_width": 1.3,
        "marker_size": 5,
    },
}


def validate_style(config: dict[str, Any]) -> dict[str, Any]:
    required = {
        "journal",
        "font_family",
        "font_size",
        "fig_width",
        "fig_height_ratio",
        "dpi",
        "line_width",
        "marker_size",
        "grid",
        "spine_top",
        "spine_right",
    }
    missing = sorted(required - config.keys())
    if missing:
        raise ValueError(f"Style config is missing: {', '.join(missing)}")
    if not isinstance(config["dpi"], int) or not 72 <= config["dpi"] <= 1200:
        raise ValueError("dpi must be an integer between 72 and 1200")
    if not isinstance(config["journal"], str) or not config["journal"].strip():
        raise ValueError("journal must be a non-empty string")
    if config["font_family"] not in {"serif", "sans-serif", "monospace"}:
        raise ValueError("font_family must be serif, sans-serif, or monospace")
    widths = config["fig_width"]
    if not isinstance(widths, dict) or any(
        not _positive_finite(widths.get(k)) for k in ("single", "double")
    ):
        raise ValueError("fig_width must define positive single and double widths")
    sizes = config["font_size"]
    if not isinstance(sizes, dict) or any(
        not _positive_finite(sizes.get(k)) for k in ("label", "tick", "legend", "title")
    ):
        raise ValueError("font_size must define positive label, tick, legend, and title sizes")
    for key in ("fig_height_ratio", "line_width", "marker_size"):
        if not _positive_finite(config[key]):
            raise ValueError(f"{key} must be a positive number")
    for key in ("grid", "spine_top", "spine_right"):
        if not isinstance(config[key], bool):
            raise ValueError(f"{key} must be true or false")
    return config


def _positive_finite(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and isfinite(value)
        and value > 0
    )


def style_for(journal: str) -> dict[str, Any]:
    if journal not in JOURNAL_PRESETS:
        raise ValueError(f"Unknown journal preset: {journal}")
    config = deepcopy(JOURNAL_PRESETS[journal])
    config["journal"] = journal
    return validate_style(config)


def load_style_config(path: Path) -> dict[str, Any]:
    return validate_style(load_json_object(path))
