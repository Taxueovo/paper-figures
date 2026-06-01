# Publication Style Guide

## Journal Presets

### IEEE (IEEE Transactions, CVPR, ICCV, ECCV)
```json
{
  "font_family": "serif",
  "font_serif": ["Times New Roman"],
  "font_size": {"label": 10, "tick": 9, "legend": 9, "title": 11},
  "fig_width": {"single": 3.5, "double": 7.16},
  "fig_height_ratio": 0.75,
  "line_width": 1.5,
  "marker_size": 6,
  "dpi": 300,
  "format": ["pdf", "svg", "png"]
}
```

### Nature / Science
```json
{
  "font_family": "sans-serif",
  "font_sans": ["Arial", "Helvetica"],
  "font_size": {"label": 9, "tick": 8, "legend": 8, "title": 10},
  "fig_width": {"single": 3.5, "double": 7.0},
  "fig_height_ratio": 0.8,
  "line_width": 1.2,
  "marker_size": 5,
  "dpi": 300,
  "format": ["pdf", "svg", "png"]
}
```

### Elsevier (Pattern Recognition, Neurocomputing, etc.)
```json
{
  "font_family": "serif",
  "font_serif": ["Times New Roman", "Georgia"],
  "font_size": {"label": 10, "tick": 9, "legend": 9, "title": 11},
  "fig_width": {"single": 3.54, "double": 7.28},
  "fig_height_ratio": 0.75,
  "line_width": 1.5,
  "marker_size": 6,
  "dpi": 300,
  "format": ["pdf", "svg", "png"]
}
```

### ACM (SIGGRAPH, MM, etc.)
```json
{
  "font_family": "serif",
  "font_serif": ["Times New Roman", "Libertine"],
  "font_size": {"label": 9, "tick": 8, "legend": 8, "title": 10},
  "fig_width": {"single": 3.3, "double": 6.75},
  "fig_height_ratio": 0.75,
  "line_width": 1.3,
  "marker_size": 5,
  "dpi": 300,
  "format": ["pdf", "svg", "png"]
}
```

### Generic / Default
```json
{
  "font_family": "serif",
  "font_serif": ["DejaVu Serif", "Times New Roman"],
  "font_size": {"label": 11, "tick": 10, "legend": 10, "title": 12},
  "fig_width": {"single": 4.0, "double": 7.5},
  "fig_height_ratio": 0.75,
  "line_width": 1.5,
  "marker_size": 6,
  "dpi": 300,
  "format": ["pdf", "svg", "png"]
}
```

## Matplotlib rcParams Template

Every generated figure script should begin with:

```python
import matplotlib
matplotlib.use('Agg')  # non-interactive backend
import matplotlib.pyplot as plt
import json, os

# Load style config
with open(os.path.join(os.path.dirname(__file__), '..', 'style_config.json')) as f:
    style = json.load(f)

plt.rcParams.update({
    'font.family': style['font_family'],
    'font.size': style['font_size']['label'],
    'axes.labelsize': style['font_size']['label'],
    'axes.titlesize': style['font_size']['title'],
    'xtick.labelsize': style['font_size']['tick'],
    'ytick.labelsize': style['font_size']['tick'],
    'legend.fontsize': style['font_size']['legend'],
    'lines.linewidth': style['line_width'],
    'lines.markersize': style['marker_size'],
    'figure.dpi': style['dpi'],
    'savefig.dpi': style['dpi'],
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.05,
    'axes.grid': style.get('grid', False),
    'axes.spines.top': style.get('spine_top', False),
    'axes.spines.right': style.get('spine_right', False),
})

# Add serif/sans font if specified
if 'font_serif' in style:
    plt.rcParams['font.serif'] = style['font_serif']
if 'font_sans' in style:
    plt.rcParams['font.sans-serif'] = style['font_sans']
```

## Layout Rules

### Single-column figure
- Width: `style['fig_width']['single']` (typically 3.5 inches / 89 mm)
- Height: `width * style['fig_height_ratio']`
- Use for: focused results, single plots

### Double-column (full-width) figure
- Width: `style['fig_width']['double']` (typically 7.16 inches / 182 mm)
- Height: `width * style['fig_height_ratio']`
- Use for: multi-panel figures, architecture diagrams, wide comparisons

### Subplot grid
- Use `gridspec` for precise control
- Consistent spacing: `wspace=0.3, hspace=0.3`
- Label subplots with `(a)`, `(b)`, etc. — use `fig.text()` at fixed coordinates

## Typography Rules

- **Axis labels**: Always include units in parentheses, e.g., `Temperature (°C)`, `MAE (degrees)`
- **Legend**: Place inside plot area when possible (upper-right or lower-left); avoid overlapping data
- **Tick marks**: Point inward (`tick_params(direction='in')`)
- **Scientific notation**: Use `ScalarFormatter` with `useMathText=True`

## Line and Marker Styles

For distinguishing multiple lines:

| Series | Color | Marker | Line Style |
|--------|-------|--------|------------|
| Train | C0 (blue) | `o` | solid `-` |
| Validation | C1 (orange) | `s` | dashed `--` |
| Test | C2 (green) | `^` | dash-dot `-.` |
| Baseline | C3 (red) | `D` | dotted `:` |

Use `palette` from `references/color-palettes.md` for accessible alternatives.

## Export Settings

```python
# PDF — vector, for LaTeX inclusion
fig.savefig('output.pdf', format='pdf', bbox_inches='tight', pad_inches=0.05)

# SVG — editable in Inkscape/Illustrator
fig.savefig('output.svg', format='svg', bbox_inches='tight', pad_inches=0.05)

# PNG — for Word/preview, 300 DPI
fig.savefig('output.png', format='png', dpi=300, bbox_inches='tight', pad_inches=0.05)
```
