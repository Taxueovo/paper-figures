# Neural Network Architecture Diagram Guide

## Overview

Architecture diagrams visualize the structure of a neural network model. This guide covers drawing conventions for matplotlib-based architecture figures suitable for academic papers.

## Drawing Primitives

### Module Blocks

```python
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

def draw_block(ax, x, y, w, h, label, color, fontsize=8, sublabel=None):
    """Draw a rounded rectangle module block."""
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.05",
        facecolor=color, edgecolor='black',
        linewidth=0.8, alpha=0.85
    )
    ax.add_patch(box)
    ax.text(x + w/2, y + h/2 + (0.03 if sublabel else 0), label,
            ha='center', va='center', fontsize=fontsize, fontweight='bold')
    if sublabel:
        ax.text(x + w/2, y + h/2 - 0.06, sublabel,
                ha='center', va='center', fontsize=fontsize-1, fontstyle='italic')
```

### Data Flow Arrows

```python
def draw_arrow(ax, x1, y1, x2, y2, label=None, color='#7F7F7F'):
    """Draw an arrow with optional dimension label."""
    arrow = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle='->', mutation_scale=12,
        linewidth=1.0, color=color,
        connectionstyle='arc3,rad=0'
    )
    ax.add_patch(arrow)
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx, my+0.03, label, ha='center', va='bottom',
                fontsize=7, fontstyle='italic', color='#555555')
```

### Branch/Split

```python
def draw_branch(ax, x, y, outputs, labels=None, color='#7F7F7F'):
    """Draw a branching point from (x,y) to multiple outputs."""
    for i, (ox, oy) in enumerate(outputs):
        draw_arrow(ax, x, y, ox, oy,
                   label=labels[i] if labels else None, color=color)
```

## Color Scheme

| Module Type | Background Color | Border Color | Text Color |
|-------------|-----------------|--------------|------------|
| Backbone (CNN/Transformer) | `#4C72B0` (blue) | `#2E5090` | white |
| Attention Module | `#DD8452` (orange) | `#B86A3C` | white |
| FFT/Frequency Module | `#55A868` (green) | `#3D8A52` | white |
| Fusion Layer | `#8172B3` (purple) | `#635899` | white |
| Output Head | `#C44E52` (red) | `#A03A3E` | white |
| Input/Preprocessing | `#8C8C8C` (gray) | `#666666` | white |
| Loss Function | `#DA8BC3` (pink) | `#B86FA0` | black |

## Tensor Dimension Annotations

- Place dimension labels at arrow midpoints
- Use italic, smaller font (fontsize - 2)
- Format: `(B, C, H, W)` or `(B, N, D)` — batch dimension optional
- Use gray color (`#555555`) to avoid visual clutter

## Layout Algorithm

### Horizontal Layout (preferred for wide figures)
1. Place input on the left, output on the right
2. Space modules evenly: `x_gap = (total_width - n_modules * block_width) / (n_modules + 1)`
3. Vertically center all blocks at `y = fig_height / 2`
4. For multi-branch: split vertically, merge at fusion point

### Vertical Layout (for tall figures)
1. Place input at top, output at bottom
2. Space modules evenly in y
3. Horizontally center all blocks

### Multi-branch Layout
```
                    ┌─────────────┐
         ┌─────────│  Branch A    │─────────┐
         │         └─────────────┘          │
┌────────┤                                  ├────────┐
│ Input  │                                  │ Fusion │──→ Output
└────────┤                                  ├────────┘
         │         ┌─────────────┐          │
         └─────────│  Branch B    │─────────┘
                    └─────────────┘
```

## Example: FiberAngleNet Architecture

```python
fig, ax = plt.subplots(figsize=(7.16, 2.5))
ax.set_xlim(0, 10)
ax.set_ylim(0, 3)
ax.axis('off')

# Input
draw_block(ax, 0.2, 1.0, 1.0, 1.0, 'Input', '#8C8C8C', sublabel='(B, 3, 224, 224)')

# ConvNeXt Backbone (stages 1-2)
draw_block(ax, 1.8, 1.0, 1.5, 1.0, 'ConvNeXt', '#4C72B0',
           sublabel='Stages 1-2')

# Gabor Attention
draw_block(ax, 3.8, 1.5, 1.2, 0.8, 'Gabor\nAttention', '#DD8452',
           sublabel='(B, 384, 28, 28)')

# ConvNeXt (stages 3-4)
draw_block(ax, 5.5, 1.0, 1.5, 1.0, 'ConvNeXt', '#4C72B0',
           sublabel='Stages 3-4')

# FFT Branch
draw_block(ax, 3.8, 0.0, 1.2, 0.7, 'FFT\nOrientation', '#55A868',
           sublabel='(B, 512)')

# Fusion
draw_block(ax, 7.5, 0.8, 1.0, 1.2, 'Fusion', '#8172B3',
           sublabel='(B, 1280)')

# Output
draw_block(ax, 9.0, 1.0, 0.8, 1.0, 'Head', '#C44E52',
           sublabel='angle, σ')

# Arrows
draw_arrow(ax, 1.2, 1.5, 1.8, 1.5)
draw_arrow(ax, 3.3, 1.5, 3.8, 1.75)
draw_arrow(ax, 3.3, 1.5, 3.8, 0.35, label='(B, 3, 224, 224)')
draw_arrow(ax, 5.0, 1.75, 5.5, 1.5)
draw_arrow(ax, 5.0, 0.35, 7.5, 1.0)
draw_arrow(ax, 7.0, 1.5, 7.5, 1.5)
draw_arrow(ax, 8.5, 1.4, 9.0, 1.5)
```

## Checklist

- [ ] All modules labeled with names and tensor dimensions
- [ ] Color-coded by module type
- [ ] Arrows show data flow direction
- [ ] Figure fits single-column (3.5") or double-column (7.16") width
- [ ] Text is readable at 300 DPI
- [ ] No overlapping elements
- [ ] Consistent with other figures in the paper
