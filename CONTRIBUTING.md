# Contributing

Thanks for helping improve Paper Figures.

1. Open an issue for substantial behavioral changes.
2. Create a focused branch and add tests for user-visible behavior.
3. Run `ruff format --check paper_figures tests scripts`, `ruff check paper_figures tests scripts`, `pytest`, and `python scripts/release_audit.py`.
4. Keep examples synthetic and non-sensitive. Never add private research datasets, credentials, personal paths, or generated export directories.
5. Submit a pull request explaining the problem, behavior change, and verification performed.

By contributing, you agree that your work is licensed under the repository's MIT License.
