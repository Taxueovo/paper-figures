# paper-figures
(兄弟我是真不会画图了，没办法了搞了个这个，你们要是也不会就拿去用吧）
Publication-quality figure generation for academic papers. A Claude Code skill that automatically generates publication-ready figures from your research data.

## Features

- **5 figure types**: Architecture diagrams, training curves, sensitivity/ablation analysis, scatter + error plots, bar charts
- **Journal presets**: IEEE, Nature/Science, Elsevier, ACM — auto-configured fonts, sizes, and layouts
- **Triple output**: Every figure exports PDF (for LaTeX) + SVG (editable) + PNG (300 DPI preview)
- **Data-aware**: Reads CSV files, training logs, and Python model code directly
- **Quality checks**: Automated style validation (font sizes, DPI, contrast ratios)

## Quick Start

### As a Claude Code Skill

This project is designed to be used as a [Claude Code skill](https://docs.anthropic.com/en/docs/claude-code). Place it in your skills directory and trigger with:

```
"generate paper figures"
"论文插图"
"画图"
```

### Standalone Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Set up a figure project
python scripts/setup_project.py /path/to/your/project

# Render a figure
python scripts/render_figure.py figures/src/fig_01_example.py

# Batch export all figures
python scripts/batch_export.py figures/src/ figures/export/

# Style check
python scripts/style_checker.py figures/export/
```

## Project Structure

```
paper-figures/
├── SKILL.md                  # Skill definition and pipeline
├── requirements.txt          # Python dependencies
├── scripts/
│   ├── setup_project.py      # Initialize figure directory structure
│   ├── render_figure.py      # Execute matplotlib code, export 3 formats
│   ├── batch_export.py       # Batch export all figures
│   └── style_checker.py      # Validate publication standards
├── templates/
│   ├── architecture.json     # Neural network architecture diagrams
│   ├── training_curves.json  # Loss/metric curves over epochs
│   ├── sensitivity.json      # Parameter sweeps, heatmaps, ablation
│   ├── scatter_error.json    # Prediction vs truth, error histograms
│   └── bar_chart.json        # Method comparison charts
├── references/
│   ├── style-guide.md        # Journal-specific style presets
│   ├── figure-types.md       # Detailed specs per figure type
│   ├── color-palettes.md     # Accessible color palettes
│   └── architecture-diagram.md # Architecture drawing conventions
└── workflows/
    ├── from-csv.md           # Generate figure from CSV data
    ├── from-model.md         # Generate figure from model code
    └── batch-all.md          # Generate all paper figures at once
```

## Supported Journal Styles

| Journal | Font | Single Width | Double Width |
|---------|------|-------------|-------------|
| IEEE (CVPR, ICCV, ECCV) | Times New Roman | 3.5" | 7.16" |
| Nature / Science | Arial | 3.5" | 7.0" |
| Elsevier | Times New Roman | 3.54" | 7.28" |
| ACM (SIGGRAPH, MM) | Times New Roman | 3.3" | 6.75" |

## Dependencies

- matplotlib >= 3.7.0
- seaborn >= 0.12.0
- numpy >= 1.24.0
- pandas >= 1.5.0
- scipy >= 1.10.0
- Pillow >= 9.0.0

## License

MIT
