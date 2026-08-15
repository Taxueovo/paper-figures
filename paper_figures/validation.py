"""Strict validation for PDF, SVG, and PNG publication assets."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ValidationIssue:
    path: Path
    message: str


def validate_pdf(path: Path) -> list[ValidationIssue]:
    from pypdf import PdfReader

    data = path.read_bytes()
    issues: list[ValidationIssue] = []
    if not data.startswith(b"%PDF-"):
        issues.append(ValidationIssue(path, "invalid PDF header"))
    if b"%%EOF" not in data[-1024:]:
        issues.append(ValidationIssue(path, "missing PDF end marker"))
    try:
        reader = PdfReader(path, strict=True)
        if reader.is_encrypted:
            issues.append(ValidationIssue(path, "PDF must not be encrypted"))
        elif len(reader.pages) == 0:
            issues.append(ValidationIssue(path, "PDF contains no pages"))
    except Exception as exc:
        issues.append(ValidationIssue(path, f"PDF cannot be parsed: {exc}"))
    return issues


def validate_svg(path: Path) -> list[ValidationIssue]:
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, UnicodeError) as exc:
        return [ValidationIssue(path, f"invalid SVG XML: {exc}")]
    if root.tag.rsplit("}", 1)[-1].lower() != "svg":
        return [ValidationIssue(path, "root element is not svg")]
    if not (root.get("viewBox") or (root.get("width") and root.get("height"))):
        return [ValidationIssue(path, "SVG has no viewBox or explicit dimensions")]
    return []


def validate_png(path: Path, config: dict[str, Any]) -> list[ValidationIssue]:
    from PIL import Image

    issues: list[ValidationIssue] = []
    try:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            width, height = image.size
            dpi_value = image.info.get("dpi", (0, 0))
    except Exception as exc:
        return [ValidationIssue(path, f"invalid PNG: {exc}")]
    if width <= 0 or height <= 0:
        issues.append(ValidationIssue(path, "PNG dimensions must be positive"))
    expected_dpi = int(config.get("dpi", 300))
    dpi_x = float(dpi_value[0] if isinstance(dpi_value, tuple) else dpi_value or 0)
    if not dpi_x:
        issues.append(ValidationIssue(path, "PNG has no DPI metadata"))
    elif dpi_x < expected_dpi * 0.9:
        issues.append(ValidationIssue(path, f"DPI {dpi_x:.1f} is below target {expected_dpi}"))
    minimum_width = int(float(config.get("fig_width", {}).get("single", 3.0)) * expected_dpi * 0.85)
    if width < minimum_width:
        issues.append(
            ValidationIssue(path, f"width {width}px is below expected minimum {minimum_width}px")
        )
    return issues


def validate_file(path: Path, config: dict[str, Any]) -> list[ValidationIssue]:
    if not path.is_file() or path.stat().st_size == 0:
        return [ValidationIssue(path, "file is missing or empty")]
    validators = {".pdf": validate_pdf, ".svg": validate_svg}
    if path.suffix.lower() == ".png":
        return validate_png(path, config)
    validator = validators.get(path.suffix.lower())
    return validator(path) if validator else []


def expected_triplet(output_dir: Path, stem: str) -> dict[str, Path]:
    return {extension: output_dir / f"{stem}.{extension}" for extension in ("pdf", "svg", "png")}


def validate_triplet(output_dir: Path, stem: str, config: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for path in expected_triplet(output_dir, stem).values():
        issues.extend(validate_file(path, config))
    return issues


def validate_directory(
    output_dir: Path, config: dict[str, Any]
) -> tuple[int, list[ValidationIssue]]:
    stems = {
        path.stem
        for path in output_dir.iterdir()
        if path.is_file() and path.suffix.lower() in {".pdf", ".svg", ".png"}
    }
    if not stems:
        return 0, [ValidationIssue(output_dir, "no PDF, SVG, or PNG figure exports found")]
    issues: list[ValidationIssue] = []
    for stem in sorted(stems):
        issues.extend(validate_triplet(output_dir, stem, config))
    return len(stems) * 3, issues
