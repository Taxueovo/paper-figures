"""Publication-figure tooling with deterministic output validation."""

from .config import JOURNAL_PRESETS, load_style_config, style_for
from .rendering import RenderResult, render_script

__all__ = ["JOURNAL_PRESETS", "RenderResult", "load_style_config", "render_script", "style_for"]
__version__ = "1.0.0"
