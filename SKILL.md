---
name: paper-figures
description: >-
  Generate reproducible academic figures from real CSV or JSON data. Supports training curves,
  prediction/error plots, comparisons, sensitivity maps, and architecture diagrams, with
  PDF + SVG + 300-DPI PNG output. Trigger on: paper figure, 论文插图, 学术图表, plot results.
---

# Paper Figures Skill

## Non-negotiable rules

1. Read actual user-provided data. Never fabricate, interpolate, or silently replace values.
2. Confirm column meanings and units when they cannot be inferred safely.
3. Keep source data outside this skill repository; never copy private datasets into it.
4. Produce and validate PDF, SVG, and PNG for each requested figure.
5. Treat `paper-figures render` as execution of trusted Python code, not as a sandbox.
6. Show the user the PNG result for visual review before declaring the figure finished.

## Workflow

1. Discover inputs with `paper-figures setup --scan-only` or inspect only paths the user supplied.
2. Create a project with `paper-figures setup figures --journal <preset>` if needed.
3. Agree on figure type, columns, units, output name, and journal style.
4. Prefer the built-in `generate` command for CSV/JSON inputs:

   ```bash
   paper-figures generate <type> --data <path> --output-dir figures/export --config figures/style_config.json
   ```

5. Use a custom `fig_*.py` source only when the built-in generator cannot express the requested plot. It must read the real source and respect `PAPER_FIGURES_OUTPUT_DIR`.
6. Run `paper-figures check figures/export --config figures/style_config.json --strict`.
7. Visually inspect the PNG for clipping, overlap, misleading scales, wrong labels, and color accessibility.

## Supported built-ins

| Type | Required data | Key options |
| :--- | :--- | :--- |
| `training` | numeric x and series columns | `--x`, `--series` |
| `scatter` | two numeric columns | `--truth`, `--prediction` |
| `bar` | category and numeric series | `--category`, `--series` |
| `sensitivity` | numeric x/value; optional numeric y | `--x`, `--y`, `--value` |
| `architecture` | JSON nodes and edges | explicit node positions/groups |

Presets: `generic`, `ieee`, `nature`, `elsevier`, `acm`.

For input examples, read only the matching file under `templates/`. For domain-specific layout guidance, read the matching reference under `references/`.
