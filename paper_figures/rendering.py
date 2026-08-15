"""Execute a figure source and enforce its exact output contract."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .validation import ValidationIssue, expected_triplet, validate_triplet


@dataclass
class RenderResult:
    script: Path
    stem: str
    returncode: int
    stdout: str
    stderr: str
    outputs: dict[str, Path]
    issues: list[ValidationIssue]

    @property
    def success(self) -> bool:
        return self.returncode == 0 and not self.issues


def output_stem(script: Path) -> str:
    match = re.fullmatch(r"fig_(?:\d+_)?(.+)", script.stem)
    return match.group(1) if match else script.stem


def _fingerprint(path: Path) -> tuple[int, int] | None:
    if not path.is_file():
        return None
    stat = path.stat()
    return stat.st_size, stat.st_mtime_ns


def render_script(
    script: Path,
    output_dir: Path,
    config: dict[str, Any],
    *,
    timeout: int = 120,
    stem: str | None = None,
) -> RenderResult:
    script = script.resolve()
    output_dir = output_dir.resolve()
    if not script.is_file() or script.suffix != ".py":
        raise ValueError(f"Figure source must be an existing Python file: {script}")
    if not 1 <= timeout <= 3600:
        raise ValueError("timeout must be between 1 and 3600 seconds")
    output_dir.mkdir(parents=True, exist_ok=True)
    selected_stem = stem or output_stem(script)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", selected_stem):
        raise ValueError(
            "output stem may contain only letters, numbers, dots, underscores, and hyphens"
        )
    outputs = expected_triplet(output_dir, selected_stem)
    before = {extension: _fingerprint(path) for extension, path in outputs.items()}
    env = os.environ.copy()
    env.update(
        {"MPLBACKEND": "Agg", "PAPER_FIGURES_OUTPUT_DIR": str(output_dir), "PYTHONHASHSEED": "0"}
    )
    try:
        completed = subprocess.run(
            [sys.executable, str(script)],
            cwd=script.parent,
            env=env,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        returncode, stdout, stderr = completed.returncode, completed.stdout, completed.stderr
    except subprocess.TimeoutExpired as exc:
        returncode, stdout, stderr = 124, exc.stdout or "", f"Timed out after {timeout}s"

    issues: list[ValidationIssue] = []
    if returncode == 0:
        for extension, path in outputs.items():
            if _fingerprint(path) == before[extension]:
                issues.append(
                    ValidationIssue(path, "expected output was not created or updated by this run")
                )
        issues.extend(validate_triplet(output_dir, selected_stem, config))
    return RenderResult(script, selected_stem, returncode, stdout, stderr, outputs, issues)
