"""Deterministic, bounded project discovery."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path

SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", "node_modules", "dist", "build"}
MAX_TEXT_BYTES = 2 * 1024 * 1024


@dataclass
class DiscoveryResult:
    csv_files: list[str] = field(default_factory=list)
    model_files: list[str] = field(default_factory=list)
    log_files: list[str] = field(default_factory=list)
    existing_figure_dirs: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, list[str]]:
        return asdict(self)


def discover(root: Path) -> DiscoveryResult:
    root = root.resolve()
    result = DiscoveryResult()
    for candidate in ("figures", "figs", "images"):
        if (root / candidate).is_dir():
            result.existing_figure_dirs.append(candidate)

    for path in sorted(root.rglob("*")):
        if any(
            part in SKIP_DIRS or part.startswith(".") for part in path.relative_to(root).parts[:-1]
        ):
            continue
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        lower = path.name.lower()
        if path.suffix.lower() == ".csv":
            result.csv_files.append(relative)
        elif path.suffix.lower() == ".py" and path.stat().st_size <= MAX_TEXT_BYTES:
            text = path.read_text(encoding="utf-8", errors="replace")
            if "nn.Module" in text or "torch.nn.Module" in text:
                result.model_files.append(relative)
        elif path.suffix.lower() == ".log" or "metrics" in lower:
            result.log_files.append(relative)
    return result
