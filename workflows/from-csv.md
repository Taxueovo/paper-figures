# Workflow: Generate Figure from CSV

## Trigger
User says: "Generate a figure from this CSV" / "用这个CSV画图" / provides a CSV file path

## Steps

### 1. Read and Analyze CSV
1. Read the CSV file specified by the user.
2. Parse column names, data types, and value ranges.
3. Determine the best figure type:
   - Single parameter column + metric columns → **1D sensitivity line plot**
   - Two parameter columns + metric column → **2D heatmap**
   - Epoch column + loss/metric columns → **training curves**
   - True/predicted columns → **scatter plot**
   - Category + value columns → **bar chart**

### 2. Select Template
Based on the analysis, load the corresponding template:
- `templates/sensitivity.json` for parameter sweeps
- `templates/training_curves.json` for epoch-based data
- `templates/scatter_error.json` for prediction data
- `templates/bar_chart.json` for comparison data

### 3. Generate Code
1. Read `references/style-guide.md` for the active style config.
2. Read the template's `code_template` field.
3. Generate a complete Python script that:
   - Loads the CSV with pandas
   - Applies the template's plotting logic
   - Uses actual column names from the CSV
   - Adds proper labels, legends, and annotations
   - Saves to PDF + SVG + PNG
4. Save to `figures/src/fig_XX_<descriptive_name>.py`

### 4. Render and Verify
1. Run: `python ${SKILL_DIR}/scripts/render_figure.py figures/src/fig_XX_<name>.py`
2. Check output files exist and are valid.
3. Show the PNG preview to the user.

### 5. Iterate
If the user wants changes:
- Modify the source script
- Re-render
- Repeat until satisfied

## Example

```
User: "用 alpha_sensitivity.csv 画一个参数敏感性图"

1. Read alpha_sensitivity.csv → columns: alpha, best_epoch, val_mae, val_rmse, val_ece, test_mae, test_rmse, test_ece, test_std
2. Single parameter (alpha) + multiple metrics → 1D sensitivity line plot
3. Generate fig_alpha_sensitivity.py with dual y-axis (MAE + ECE)
4. Render → figures/export/alpha_sensitivity.{pdf,svg,png}
5. Show preview
```
