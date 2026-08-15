# Workflow: Batch Custom Figures

1. Ensure every trusted source is named `fig_*.py` and writes the exact stem expected from its filename.
2. Run `paper-figures batch --src-dir figures/src --export-dir figures/export --config figures/style_config.json`.
3. Stop on any non-zero exit. Fix the failed source; do not reuse stale exports.
4. Run strict validation and inspect every PNG.
5. Review generated LaTeX captions; placeholders are intentionally never presented as final prose.
