#!/usr/bin/env python3
"""Backward-compatible wrapper for ``paper-figures check``."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from paper_figures.cli import main

raise SystemExit(main(["check", *sys.argv[1:]]))
