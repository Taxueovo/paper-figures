"""Safe project scaffolding."""

from __future__ import annotations

from pathlib import Path

from .config import style_for
from .io_utils import atomic_write_json, atomic_write_text

PROJECT_README = """# Paper Figures

Generated with `paper-figures`.

- `src/` contains the reproducible Python source for each figure.
- `export/` contains PDF, SVG, and 300-DPI PNG outputs.
- `style_config.json` records the journal-specific rendering contract.

Run `paper-figures batch --src-dir src --export-dir export` from this directory.
"""


def setup_project(output_dir: Path, journal: str, *, force: bool = False) -> list[Path]:
    output_dir = output_dir.resolve()
    config = style_for(journal)
    targets = {
        output_dir / "style_config.json": None,
        output_dir / "figure_plan.json": {"figures": []},
        output_dir / "README.md": PROJECT_README,
    }
    collisions = [path for path in targets if path.exists() and not force]
    if collisions:
        names = ", ".join(path.name for path in collisions)
        raise FileExistsError(
            f"Refusing to overwrite existing files: {names}; use --force to replace them"
        )
    (output_dir / "src").mkdir(parents=True, exist_ok=True)
    (output_dir / "export").mkdir(parents=True, exist_ok=True)
    atomic_write_json(output_dir / "style_config.json", config)
    atomic_write_json(output_dir / "figure_plan.json", {"figures": []})
    atomic_write_text(output_dir / "README.md", PROJECT_README)
    return list(targets)
