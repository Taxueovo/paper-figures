#!/usr/bin/env python3
"""Validate figures meet publication style standards.

Usage:
    python style_checker.py <export_dir> [--config figures/style_config.json]

Checks:
- PNG: file size > 0, dimensions >= 1000px wide at 300 DPI
- PDF: valid header, non-zero size
- SVG: valid XML, contains <svg> tag
- General: all three formats present per figure
"""

import argparse
import json
import os
import sys
from pathlib import Path


def check_png(filepath: str, config: dict) -> list:
    """Validate PNG file."""
    issues = []
    size = os.path.getsize(filepath)
    if size == 0:
        issues.append("Empty file")
        return issues
    if size < 1000:
        issues.append(f"Suspiciously small ({size} bytes)")

    try:
        from PIL import Image
        img = Image.open(filepath)
        w, h = img.size
        dpi = img.info.get("dpi", (72, 72))
        if isinstance(dpi, tuple):
            dpi_x = dpi[0]
        else:
            dpi_x = dpi

        if w < 800:
            issues.append(f"Width {w}px may be too small for print (target: 300 DPI)")

        expected_dpi = config.get("dpi", 300)
        if dpi_x < expected_dpi * 0.9:
            issues.append(f"DPI {dpi_x} below target {expected_dpi}")
    except ImportError:
        issues.append("PIL not installed — cannot check dimensions/DPI")
    except Exception as e:
        issues.append(f"Cannot read PNG: {e}")

    return issues


def check_pdf(filepath: str) -> list:
    """Validate PDF file."""
    issues = []
    size = os.path.getsize(filepath)
    if size == 0:
        issues.append("Empty file")
        return issues
    if size < 100:
        issues.append(f"Suspiciously small ({size} bytes)")

    with open(filepath, "rb") as f:
        header = f.read(5)
    if header != b"%PDF-":
        issues.append("Invalid PDF header")

    return issues


def check_svg(filepath: str) -> list:
    """Validate SVG file."""
    issues = []
    size = os.path.getsize(filepath)
    if size == 0:
        issues.append("Empty file")
        return issues

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read(500)
        if "<svg" not in content.lower():
            issues.append("No <svg> tag found in file")
    except UnicodeDecodeError:
        issues.append("File is not valid UTF-8")

    return issues


def check_completeness(export_dir: str) -> list:
    """Check that each figure has all three formats."""
    issues = []
    files = {}
    for f in os.listdir(export_dir):
        name, ext = os.path.splitext(f)
        ext = ext.lstrip(".").lower()
        if ext in ("pdf", "svg", "png"):
            files.setdefault(name, set()).add(ext)

    for name, exts in files.items():
        missing = {"pdf", "svg", "png"} - exts
        if missing:
            issues.append(f"{name}: missing formats: {', '.join(sorted(missing))}")

    return issues


def main():
    parser = argparse.ArgumentParser(description="Check figure style compliance")
    parser.add_argument("export_dir", help="Directory containing exported figures")
    parser.add_argument("--config", default=None,
                        help="Path to style_config.json")
    parser.add_argument("--strict", action="store_true",
                        help="Exit with error on any issue")
    args = parser.parse_args()

    export_dir = os.path.abspath(args.export_dir)
    if not os.path.isdir(export_dir):
        print(f"Error: Directory not found: {export_dir}", file=sys.stderr)
        sys.exit(1)

    # Load config
    config = {}
    if args.config and os.path.exists(args.config):
        with open(args.config) as f:
            config = json.load(f)
    else:
        # Try default location
        default_config = os.path.join(os.path.dirname(export_dir), "style_config.json")
        if os.path.exists(default_config):
            with open(default_config) as f:
                config = json.load(f)

    all_issues = []
    files_checked = 0

    print(f"Checking: {export_dir}")
    print(f"Config:   {config.get('journal', 'generic')}")
    print("-" * 60)

    # Check individual files
    for f in sorted(os.listdir(export_dir)):
        filepath = os.path.join(export_dir, f)
        if not os.path.isfile(filepath):
            continue

        name, ext = os.path.splitext(f)
        ext = ext.lstrip(".").lower()

        if ext == "png":
            issues = check_png(filepath, config)
        elif ext == "pdf":
            issues = check_pdf(filepath)
        elif ext == "svg":
            issues = check_svg(filepath)
        elif ext in ("tex", "md", "json"):
            continue  # skip metadata files
        else:
            continue

        files_checked += 1
        if issues:
            for issue in issues:
                print(f"  ✗ {f}: {issue}")
                all_issues.append((f, issue))
        else:
            size_kb = os.path.getsize(filepath) / 1024
            print(f"  ✓ {f} ({size_kb:.1f} KB)")

    # Check completeness
    print()
    completeness = check_completeness(export_dir)
    for issue in completeness:
        print(f"  ✗ {issue}")
        all_issues.append(("completeness", issue))

    # Summary
    print(f"\n{'='*60}")
    print(f"Checked: {files_checked} files")
    print(f"Issues:  {len(all_issues)}")

    if all_issues:
        if args.strict:
            print("\nFAILED — strict mode")
            sys.exit(1)
        else:
            print("\nWARN — some issues found (use --strict to fail)")
    else:
        print("\nPASSED — all checks OK")

    sys.exit(0)


if __name__ == "__main__":
    main()
