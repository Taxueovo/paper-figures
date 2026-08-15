from paper_figures.config import style_for
from paper_figures.rendering import render_script

WRITER = r"""
import os
from pathlib import Path
from PIL import Image
from pypdf import PdfWriter

output = Path(os.environ["PAPER_FIGURES_OUTPUT_DIR"])
output.mkdir(parents=True, exist_ok=True)
writer = PdfWriter()
writer.add_blank_page(width=100, height=50)
with (output / "demo.pdf").open("wb") as handle:
    writer.write(handle)
(output / "demo.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 50"/>')
Image.new("RGB", (1200, 700), "white").save(output / "demo.png", dpi=(300, 300))
"""


def test_render_accepts_only_exact_outputs_from_current_run(tmp_path):
    script = tmp_path / "fig_01_demo.py"
    script.write_text(WRITER, encoding="utf-8")
    result = render_script(script, tmp_path / "export", style_for("generic"))
    assert result.success
    assert result.stem == "demo"


def test_stale_outputs_do_not_create_a_false_success(tmp_path):
    script = tmp_path / "fig_01_demo.py"
    script.write_text(WRITER, encoding="utf-8")
    export = tmp_path / "export"
    assert render_script(script, export, style_for("generic")).success
    script.write_text("pass\n", encoding="utf-8")

    result = render_script(script, export, style_for("generic"))

    assert not result.success
    assert len([issue for issue in result.issues if "not created or updated" in issue.message]) == 3
