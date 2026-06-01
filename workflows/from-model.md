# Workflow: Generate Figure from Trained Model

## Trigger
User says: "Generate figures from my model" / "从模型生成图" / mentions model checkpoint or training code

## Steps

### 1. Discover Model and Data
1. Find Python files with `nn.Module` subclasses in the project.
2. Read the model architecture code to understand:
   - Module structure and connections
   - Input/output shapes
   - Special modules (attention, custom layers, etc.)
3. Find training data:
   - CSV files with metrics
   - Log files
   - Model checkpoints (`.pth`, `.pt`)
4. Find test/validation data paths from config.

### 2. Determine Figure Set
Based on what's available, recommend figures:

| Available Data | Recommended Figures |
|---------------|-------------------|
| Model code only | Architecture diagram |
| Model code + training logs | Architecture + training curves |
| Model code + test predictions | Architecture + scatter + error histogram |
| All of the above | Full figure set |

### 3. Architecture Diagram
1. Read `references/architecture-diagram.md` for conventions.
2. Read the model's `__init__` and `forward` methods.
3. Identify module blocks, connections, and data flow.
4. Generate matplotlib code using `FancyBboxPatch` and `FancyArrowPatch`.
5. Color-code by module type using `templates/architecture.json` color scheme.
6. Annotate tensor dimensions at connection points.

### 4. Training Curves (if training logs available)
1. Read the metrics CSV/log file.
2. Use `templates/training_curves.json` template.
3. Plot train + val loss and metrics over epochs.
4. Mark best epoch, early stopping point.

### 5. Results Plots (if test predictions available)
1. Read prediction data (true angles, predicted angles, uncertainties).
2. Use `templates/scatter_error.json` template.
3. Generate scatter plot + error distribution.
4. Annotate R², MAE, ECE.

### 6. Render All
1. Run each figure script through `scripts/render_figure.py`.
2. Run `scripts/batch_export.py` to consolidate.
3. Show all previews to user.

## Example

```
User: "从 DinoConv.py 生成模型架构图"

1. Read DinoConv.py → find FiberAngleNet(nn.Module) with ConvNeXt backbone, GaborAttention, FFTOrientationModule, fusion head
2. Recommend: architecture diagram + (if logs exist) training curves
3. Generate fig_architecture.py with:
   - ConvNeXt stages 1-2 (blue) → GaborAttention (orange) → ConvNeXt stages 3-4 (blue)
   - FFT branch (green) from input
   - Fusion (purple) → Output head (red)
   - Tensor dimensions at each connection
4. Render → figures/export/architecture.{pdf,svg,png}
```
