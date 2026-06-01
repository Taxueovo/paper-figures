# Figure Type Specifications

## 1. Architecture Diagrams

### Purpose
Visualize neural network architecture, module connections, and data flow.

### Matplotlib Approach (recommended for most papers)
- Use `FancyBboxPatch` for module blocks
- Use `FancyArrowPatch` with `ConnectionStyle` for data flow arrows
- Annotate tensor shapes at connection midpoints
- Color-code by module type

### Drawing Convention
- **Flow direction**: Left to right (horizontal) for wide figures; top to bottom for tall figures
- **Backbone modules**: Blue tones (`#4C72B0`, `#55A868`)
- **Attention modules**: Orange/amber (`#DD8452`, `#C44E52`)
- **Fusion layers**: Green (`#55A868`)
- **Output heads**: Red/purple (`#C44E52`, `#8172B3`)
- **Data arrows**: Gray (`#7F7F7F`), width proportional to importance
- **Tensor annotations**: Small font, italic, at arrow midpoints

### Block Size Convention
- Main blocks: 1.5 × 0.8 inches (relative to figure)
- Sub-blocks: 1.0 × 0.5 inches
- Minimum gap: 0.2 inches between blocks

### Multi-branch Architecture
For models with parallel branches (e.g., CNN + FFT):
- Draw branches splitting from a common input
- Use different background tint for each branch
- Merge with a clearly labeled fusion block
- Show dimension changes at branch/split points

### Template
See `templates/architecture.json`

---

## 2. Training Curves

### Purpose
Show convergence behavior, overfitting detection, and hyperparameter schedules.

### Plot Types
- **Loss curves**: train + val on same axes, dual y-axis if scales differ
- **Metric curves**: MAE, RMSE, accuracy, R² over epochs
- **Learning rate schedule**: overlay as semi-transparent fill or secondary y-axis
- **Gradient norms**: useful for appendix or supplementary

### Data Format
CSV with columns: `epoch, train_loss, val_loss, train_mae, val_mae, lr`

### Annotations
- Mark best epoch with vertical dashed line + annotation
- Mark early stopping point if applicable
- If overfitting is visible, annotate the divergence point
- Show final values as text annotation near the curve endpoint

### Multi-run Overlay
When comparing multiple training runs (e.g., different alpha values):
- Use different colors per run
- Add a legend with the hyperparameter value
- Consider small multiples (subplot grid) if >4 runs

### Template
See `templates/training_curves.json`

---

## 3. Sensitivity / Ablation Analysis

### Purpose
Show model sensitivity to hyperparameters and contribution of each component.

### 1D Sensitivity (single parameter sweep)
- **Line plot** with markers at each tested value
- X-axis: parameter value (log scale if range spans order of magnitude)
- Y-axis: metric (MAE, RMSE, etc.)
- Mark optimal value with a star or vertical line
- Show confidence interval if multiple runs per value

### 2D Sensitivity (two-parameter sweep)
- **Heatmap** with labeled cells
- X-axis: parameter 1, Y-axis: parameter 2
- Color: metric value (use perceptually uniform colormap: `viridis`, `plasma`)
- Annotate each cell with the exact value
- Mark optimal combination with a border or marker

### Ablation Study
- **Grouped bar chart**: groups = ablation conditions, bars = metrics
- Include "Full model" as baseline
- Sort by performance (best to worst)
- Show percentage drop from baseline as annotation

### Data Format
CSV with parameter columns + metric columns (e.g., `alpha_sensitivity.csv`, `fft_sensitivity.csv`)

### Template
See `templates/sensitivity.json`

---

## 4. Scatter Plot + Error Distribution

### Purpose
Evaluate prediction quality and uncertainty calibration.

### Predicted vs True Scatter
- X-axis: true values, Y-axis: predicted values
- Identity line (y=x) as dashed gray reference
- R² and MAE as text annotation in corner
- Point color: optional third variable (e.g., uncertainty)
- Point transparency: 0.3–0.5 for dense regions

### Error Distribution Histogram
- X-axis: absolute error (degrees)
- Y-axis: count or density
- Overlay KDE curve
- Mark mean and median with vertical lines
- Show percentile annotations (50th, 90th, 95th)

### Uncertainty Calibration Plot
- Bin predictions by predicted std
- Per bin: plot mean predicted std vs mean actual error
- Perfect calibration = diagonal line
- ECE score as annotation

### Combined Figure (2×1 subplot)
Top: scatter plot, Bottom: error histogram. Shared x-axis concept, separate y-axes.

### Data Format
Arrays: `true_angles`, `pred_angles`, `pred_stds` (optional)

### Template
See `templates/scatter_error.json`

---

## 5. Bar Chart (Comparison / Ablation)

### Purpose
Compare methods or model variants side by side.

### Single-metric comparison
- Horizontal bars (preferred when method names are long)
- Sort by performance
- Show value labels at bar ends
- Highlight best with a distinct color

### Multi-metric comparison
- Grouped vertical bars
- One group per method, bars per metric
- Consistent color mapping across groups
- Legend outside the plot area

### Error Bars
- Show std or confidence interval as error bars
- If multiple runs, show individual points as scatter overlay

### Template
See `templates/bar_chart.json`
