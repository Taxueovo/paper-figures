# Workflow: Batch Generate All Paper Figures

## Trigger
User says: "Generate all paper figures" / "生成所有图表" / "一键生成论文插图"

## Steps

### 1. Full Project Scan
1. Run `python ${SKILL_DIR}/scripts/setup_project.py --scan-only` to discover all data sources.
2. Read all CSV files in the project.
3. Read all Python model files.
4. Check for existing figure directories.

### 2. Plan All Figures
Based on scan results, create a comprehensive figure plan:

```json
{
  "figures": [
    {
      "id": "fig1",
      "name": "architecture",
      "type": "architecture",
      "source": "DinoConv.py",
      "width": "double",
      "caption": "FiberAngleNet architecture overview"
    },
    {
      "id": "fig2",
      "name": "alpha_sensitivity",
      "type": "sensitivity_1d",
      "source": "alpha_sensitivity.csv",
      "width": "single",
      "caption": "Sensitivity to loss weight α"
    },
    ...
  ]
}
```

Save to `figures/figure_plan.json`.

### 3. Generate All Code
For each figure in the plan:
1. Load the appropriate template.
2. Read the data source.
3. Generate Python code.
4. Save to `figures/src/fig_XX_<name>.py`.

### 4. Batch Render
Run: `python ${SKILL_DIR}/scripts/batch_export.py`

This will:
- Execute all figure scripts
- Export PDF + SVG + PNG for each
- Generate LaTeX snippets
- Generate README.md

### 5. Quality Check
Run: `python ${SKILL_DIR}/scripts/style_checker.py figures/export/`

Review all figures visually (read PNGs).

### 6. Report
Print summary:
- Total figures generated
- Formats per figure
- Any quality issues
- LaTeX snippet file location

## Example

```
User: "一键生成所有论文插图"

Scan results:
  - alpha_sensitivity.csv (6 rows, columns: alpha, val_mae, ...)
  - fft_sensitivity.csv (9 rows, columns: r1, r2, val_mae, ...)
  - DinoConv.py (FiberAngleNet model)

Generated:
  fig1_architecture.{pdf,svg,png} — Model architecture diagram
  fig2_alpha_sensitivity.{pdf,svg,png} — Loss weight sensitivity
  fig3_fft_sensitivity.{pdf,svg,png} — FFT parameter heatmap

Total: 3 figures × 3 formats = 9 files
LaTeX snippets: figures/export/latex_snippets.tex
```
