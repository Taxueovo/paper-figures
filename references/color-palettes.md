# Accessible Color Palettes for Academic Papers

## Selection Rules

1. **Colorblind-safe**: Use palettes distinguishable by deuteranopia/protanopia
2. **Print-friendly**: Must work in grayscale (B&W printing)
3. **Consistent**: Use the same palette across all paper figures
4. **Maximum 7 colors**: Beyond 7, use markers + line styles to differentiate

## Recommended Palettes

### Default (Colorblind-safe, print-friendly)
```python
PALETTE_DEFAULT = {
    'blue':    '#4C72B0',
    'orange':  '#DD8452',
    'green':   '#55A868',
    'red':     '#C44E52',
    'purple':  '#8172B3',
    'brown':   '#937860',
    'pink':    '#DA8BC3',
    'gray':    '#8C8C8C',
    'cyan':    '#8C564B',
}
```
Source: matplotlib `tab10` (modified for print)

### Wong (Nature Methods recommended)
```python
PALETTE_WONG = {
    'black':   '#000000',
    'orange':  '#E69F00',
    'skyblue': '#56B4E9',
    'green':   '#009E73',
    'yellow':  '#F0E442',
    'blue':    '#0072B2',
    'vermilion': '#D55E00',
    'purple':  '#CC79A7',
}
```
Source: Wong, B. (2011) Nature Methods 8, 441

### Tol (Paul Tol's bright)
```python
PALETTE_TOL_BRIGHT = {
    'blue':    '#4477AA',
    'cyan':    '#66CCEE',
    'green':   '#228833',
    'yellow':  '#CCBB44',
    'red':     '#EE6677',
    'purple':  '#AA3377',
    'grey':    '#BBBBBB',
}
```

### Sequential (for heatmaps / continuous data)
```python
COLORMAP_SEQUENTIAL = 'viridis'     # perceptually uniform, print-safe
COLORMAP_DIVERGING = 'RdBu_r'       # for diverging from a center value
COLORMAP_CATEGORICAL = 'tab10'       # for categorical coloring
```

## Color Assignment by Role

| Role | Default Color | Purpose |
|------|--------------|---------|
| Training data | blue (`#4C72B0`) | Train curves, train points |
| Validation data | orange (`#DD8452`) | Val curves, val points |
| Test data | green (`#55A868`) | Test results |
| Baseline/Reference | gray (`#8C8C8C`) | Reference lines, baselines |
| Proposed method | red (`#C44E52`) | Highlighting the best/ours |
| Attention/Important | purple (`#8172B3`) | Attention maps, highlights |

## Grayscale Conversion

When generating figures, verify they remain distinguishable in grayscale:

```python
def rgb_to_grayscale(hex_color):
    """Convert hex color to grayscale luminance."""
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return 0.299 * r + 0.587 * g + 0.114 * b
```

Grayscale luminance targets for distinct lines:
- Line 1: 0–60 (dark)
- Line 2: 80–140 (medium-dark)
- Line 3: 150–200 (medium-light)
- Line 4: 210–255 (light)

## Usage in Generated Code

```python
from matplotlib.colors import to_rgba
import numpy as np

# Apply palette
colors = ['#4C72B0', '#DD8452', '#55A868', '#C44E52', '#8172B3']

# For bar charts with alpha
bar_colors = [to_rgba(c, alpha=0.85) for c in colors]

# For scatter with transparency
scatter_colors = [to_rgba(c, alpha=0.4) for c in colors]

# For heatmap
import matplotlib.pyplot as plt
cmap = plt.get_cmap('viridis')
```
