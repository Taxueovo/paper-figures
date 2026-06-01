---
name: paper-figures
description: >-
  Generates publication-quality figures for academic papers. Supports architecture diagrams,
  training curves, sensitivity/ablation analysis, scatter plots, and error distributions.
  Outputs PDF + SVG + PNG. Auto-detects data sources (CSV, model code, training logs).
  Trigger on: "generate paper figures", "论文插图", "画图", "figure for paper",
  "学术图表", "plot results", "architecture diagram".
---

# paper-figures — Academic Paper Figure Generation Skill

## Global Execution Rules

1. **Serial pipeline**: Execute Steps 1→6 in order. Do not skip steps.
2. **Style first**: Step 2 style config MUST be set before any code generation in Step 4.
3. **Three-format output**: Every figure produces PDF + SVG + PNG (300 DPI). No exceptions.
4. **Code is the source of truth**: Figures are generated from Python/matplotlib code saved to `figures/src/`. Never hand-draw bitmaps.
5. **Data-aware**: Always read actual data files. Never fabricate numbers.
6. **Language**: Respond in the user's input language (Chinese or English).

## Scripts Table

| Script | Purpose | Path |
|--------|---------|------|
| `setup_project` | Create figure directory structure in project | `${SKILL_DIR}/scripts/setup_project.py` |
| `render_figure` | Execute matplotlib code safely, export 3 formats | `${SKILL_DIR}/scripts/render_figure.py` |
| `batch_export` | Export all figures to `figures/export/` | `${SKILL_DIR}/scripts/batch_export.py` |
| `style_checker` | Validate figures meet publication standards | `${SKILL_DIR}/scripts/style_checker.py` |

## Template Index

| Template | File | Use When |
|----------|------|----------|
| Architecture diagram | `templates/architecture.json` | Drawing neural network or module diagrams |
| Training curves | `templates/training_curves.json` | Loss, metric, LR curves over epochs |
| Sensitivity/ablation | `templates/sensitivity.json` | Parameter sweeps, heatmaps, ablation bars |
| Scatter + error | `templates/scatter_error.json` | Prediction vs truth, error histograms |
| Bar chart | `templates/bar_chart.json` | Method comparison, ablation study |

## Workflows Table

| Workflow | Trigger | File |
|----------|---------|------|
| `from-csv` | "Generate figure from this CSV" | `workflows/from-csv.md` |
| `from-model` | "Generate figure from my model" | `workflows/from-model.md` |
| `batch-all` | "Generate all paper figures" | `workflows/batch-all.md` |

---

## Pipeline

### Step 1: Project Discovery

**Gate**: None. Auto-runs on skill activation.

1. Scan the working directory for:
   - Python files with model definitions (classes inheriting `nn.Module`)
   - CSV files with numerical data (sensitivity results, metrics, etc.)
   - Training log files (`*.log`, `epoch_metrics.csv`, `runs/` directory)
   - Existing figure directories (`figures/`, `figs/`, `images/`)
2. Read any Python `Config` dataclass or config dict to extract hyperparameters.
3. Read CSV headers to understand available data columns.
4. **Output**: Print a summary of discovered data sources and recommended figures.

Recommended figure types by data source:

| Data Source | Recommended Figures |
|-------------|-------------------|
| Model code (nn.Module) | Architecture diagram |
| Training log CSV | Loss curves, metric curves, LR schedule |
| Sensitivity CSV | Parameter sweep line/heatmap |
| Test predictions CSV | Scatter plot, error histogram, calibration |
| Ablation results | Bar chart comparison |

**Checkpoint [non-blocking]**: Show recommendations, auto-proceed to Step 2.

---

### Step 2: Style Configuration

**Gate**: Step 1 complete.

1. Ask the user for journal target, OR auto-detect from existing paper files (`.tex`, `.docx`).
2. Load style config from `references/style-guide.md` based on journal.
3. Generate `figures/style_config.json` with:

```json
{
  "journal": "ieee",
  "font_family": "serif",
  "font_serif": ["Times New Roman"],
  "font_sans": ["Arial"],
  "font_size": {
    "label": 10,
    "tick": 9,
    "legend": 9,
    "title": 11
  },
  "fig_width": {
    "single": 3.5,
    "double": 7.16
  },
  "fig_height_ratio": 0.75,
  "line_width": 1.5,
  "marker_size": 6,
  "dpi": 300,
  "palette": "default",
  "grid": false,
  "spine_top": false,
  "spine_right": false
}
```

4. Apply style globally via `matplotlib.rcParams` in generated code.

**Checkpoint [blocking]**: Show style preview (sample axis with configured fonts/colors). User confirms.

---

### Step 3: Figure Planning

**Gate**: Step 2 style confirmed.

1. Based on Step 1 discoveries, present a numbered list of figures to generate.
2. For each figure, specify:
   - Figure ID (e.g., `fig1`, `fig2`)
   - Type (architecture / curves / sensitivity / scatter / bar)
   - Data source file(s)
   - Dimensions (single-column / double-column)
   - Caption draft
3. User confirms or modifies the list.
4. **Output**: `figures/figure_plan.json`

**Checkpoint [blocking]**: User reviews and confirms figure list.

---

### Step 4: Code Generation + Rendering

**Gate**: Step 3 plan confirmed. Style config exists.

For each figure in the plan:

#### 4a. Code Generation

1. Load the relevant template from `templates/*.json` for the figure type.
2. Read the reference guide for the figure type from `references/figure-types.md`.
3. Read the actual data source (CSV, Python model code, etc.).
4. Generate matplotlib/Python code that:
   - Reads the actual data file
   - Applies style from `figures/style_config.json`
   - Creates the figure with proper labels, legends, annotations
   - Saves to three formats: PDF, SVG, PNG
5. Save code to `figures/src/fig_XX_<name>.py`

#### 4b. Rendering

1. Run `python ${SKILL_DIR}/scripts/render_figure.py figures/src/fig_XX_<name>.py`
2. The script:
   - Executes the matplotlib code in a sandboxed subprocess
   - Captures stdout/stderr
   - Verifies three output files were created
   - Returns success/failure status
3. On failure: read error, fix code, re-render (max 3 attempts).

#### 4c. Architecture Diagrams (special case)

For neural network architecture diagrams:
- Read `references/architecture-diagram.md` for drawing conventions
- Use matplotlib with `FancyBboxPatch` for modules, `FancyArrowPatch` for connections
- Annotate tensor dimensions at connection points
- Color-code by module type (backbone=blue, attention=orange, fusion=green, head=red)

**Checkpoint [non-blocking]**: Show rendered PNG preview after each figure. Continue to next.

---

### Step 5: Quality Check

**Gate**: All figures rendered.

1. Run `python ${SKILL_DIR}/scripts/style_checker.py figures/export/`
2. The script checks per figure:
   - Font sizes match `style_config.json`
   - Line widths ≥ configured minimum
   - DPI = 300 for PNG
   - PDF is valid (non-zero page count)
   - SVG is well-formed XML
   - Aspect ratio within journal limits
   - Color contrast ratio ≥ 4.5:1 for text on background
3. Agent visually reviews each PNG:
   - Labels are readable and not overlapping
   - Legend is present where needed
   - Axes are properly labeled with units
   - Data is accurately represented
4. **Output**: Quality report — pass/fail per figure with issues list.

**Checkpoint [blocking if issues]**: Show failed figures, fix and re-render.

---

### Step 6: Export + Documentation

**Gate**: All figures pass quality check.

1. Run `python ${SKILL_DIR}/scripts/batch_export.py`
2. Generate `figures/export/README.md`:
   - Figure list with filenames, types, captions
   - Source data mapping (which CSV/code generated which figure)
   - Style config used
3. Generate `figures/export/latex_snippets.tex`:
   - Ready-to-paste `\begin{figure}...\end{figure}` blocks for each figure
   - Proper `\label{fig:...}` and `\caption{...}`
4. Print summary: total figures, formats, file sizes.

**Done.**

---

## Quick Commands

- **Single figure from CSV**: Invoke `workflows/from-csv.md` directly
- **All figures at once**: Invoke `workflows/batch-all.md`
- **From trained model**: Invoke `workflows/from-model.md`
