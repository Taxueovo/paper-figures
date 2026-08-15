"""Command-line interface and backward-compatible entry points."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from .batch import inspect_exports, render_all, write_export_docs
from .config import JOURNAL_PRESETS, load_style_config, style_for
from .discovery import discover
from .generators import architecture, bar_chart, scatter_error, sensitivity, training_curves
from .project import setup_project
from .rendering import render_script
from .validation import validate_directory


def _config_for(output_dir: Path, explicit: str | None) -> dict:
    candidate = Path(explicit).resolve() if explicit else output_dir.parent / "style_config.json"
    return load_style_config(candidate) if candidate.is_file() else style_for("generic")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="paper-figures", description="Reliable publication-figure tooling"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    setup = commands.add_parser("setup", help="create a figure project safely")
    setup.add_argument("destination", nargs="?", default="figures")
    setup.add_argument("--output-dir", dest="output_dir_option")
    setup.add_argument("--journal", choices=sorted(JOURNAL_PRESETS), default="generic")
    setup.add_argument("--force", action="store_true")
    setup.add_argument("--scan-only", action="store_true")
    render = commands.add_parser("render", help="render one figure and verify exact outputs")
    render.add_argument("script")
    render.add_argument("--output-dir")
    render.add_argument("--config")
    render.add_argument("--output-stem")
    render.add_argument("--timeout", type=int, default=120)
    generate = commands.add_parser(
        "generate", help="generate a figure directly from real CSV or JSON data"
    )
    generate.add_argument(
        "figure_type", choices=["architecture", "bar", "scatter", "sensitivity", "training"]
    )
    generate.add_argument("--data", required=True)
    generate.add_argument("--output-dir", default="figures/export")
    generate.add_argument("--name")
    generate.add_argument("--config")
    generate.add_argument("--x")
    generate.add_argument("--y")
    generate.add_argument("--value")
    generate.add_argument("--truth")
    generate.add_argument("--prediction")
    generate.add_argument("--category")
    generate.add_argument("--series", nargs="+")
    batch = commands.add_parser("batch", help="render every fig_*.py source")
    batch.add_argument("--src-dir", default="figures/src")
    batch.add_argument("--export-dir", default="figures/export")
    batch.add_argument("--config")
    batch.add_argument("--timeout", type=int, default=120)
    batch.add_argument("--no-run", action="store_true")
    check = commands.add_parser("check", help="validate an export directory")
    check.add_argument("export_dir")
    check.add_argument("--config")
    check.add_argument("--strict", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "setup":
        if args.scan_only:
            print(json.dumps(discover(Path.cwd()).to_dict(), indent=2))
            return 0
        try:
            destination = args.output_dir_option or args.destination
            created = setup_project(Path(destination), args.journal, force=args.force)
        except (FileExistsError, ValueError) as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 2
        print("Created:\n" + "\n".join(f"  {path}" for path in created))
        return 0

    output_dir = Path(
        getattr(args, "output_dir", None) or getattr(args, "export_dir", ".")
    ).resolve()
    try:
        config = _config_for(output_dir, getattr(args, "config", None))
    except (OSError, ValueError) as exc:
        print(f"Error: invalid style config: {exc}", file=sys.stderr)
        return 2
    if args.command == "generate":
        data = Path(args.data).resolve()
        name = args.name or f"{args.figure_type}_figure"
        generators = {
            "architecture": lambda: architecture(data, output_dir, name, config),
            "bar": lambda: bar_chart(
                data, output_dir, name, config, category=args.category, series=args.series
            ),
            "scatter": lambda: scatter_error(
                data, output_dir, name, config, truth=args.truth, prediction=args.prediction
            ),
            "sensitivity": lambda: sensitivity(
                data, output_dir, name, config, x=args.x, y=args.y, value=args.value
            ),
            "training": lambda: training_curves(
                data, output_dir, name, config, x=args.x, series=args.series
            ),
        }
        try:
            outputs = generators[args.figure_type]()
        except (OSError, ValueError, KeyError, TypeError) as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 2
        print("Generated:\n" + "\n".join(f"  {path}" for path in outputs.values()))
        return 0
    if args.command == "render":
        script = Path(args.script).resolve()
        if args.output_dir is None:
            output_dir = script.parent.parent / "export"
        try:
            result = render_script(
                script, output_dir, config, timeout=args.timeout, stem=args.output_stem
            )
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 2
        if result.stdout:
            print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
        if result.stderr:
            print(result.stderr, file=sys.stderr, end="" if result.stderr.endswith("\n") else "\n")
        for issue in result.issues:
            print(f"ERROR {issue.path.name}: {issue.message}", file=sys.stderr)
        print(f"{'PASS' if result.success else 'FAIL'}: {result.stem}")
        return 0 if result.success else 1

    if args.command == "batch":
        src_dir, export_dir = Path(args.src_dir).resolve(), Path(args.export_dir).resolve()
        results = (
            inspect_exports(export_dir, config)
            if args.no_run
            else render_all(src_dir, export_dir, config, args.timeout)
        )
        if not results:
            location = export_dir if args.no_run else src_dir
            expected = "figure exports" if args.no_run else "fig_*.py files"
            print(f"Error: no {expected} found in {location}", file=sys.stderr)
            return 2
        export_dir.mkdir(parents=True, exist_ok=True)
        write_export_docs(export_dir, results, config)
        for result in results:
            print(f"{'PASS' if result.success else 'FAIL'} {result.script.name}")
        return 0 if all(result.success for result in results) else 1

    export_dir = Path(args.export_dir).resolve()
    if not export_dir.is_dir():
        print(f"Error: directory not found: {export_dir}", file=sys.stderr)
        return 2
    count, issues = validate_directory(export_dir, config)
    for issue in issues:
        print(f"ERROR {issue.path.name}: {issue.message}")
    print(f"Checked {count} expected files; {len(issues)} issue(s)")
    return 1 if issues and args.strict else 0


def entrypoint() -> None:
    raise SystemExit(main())
