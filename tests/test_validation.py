from PIL import Image
from pypdf import PdfWriter

from paper_figures.config import style_for
from paper_figures.validation import validate_directory, validate_triplet


def _write_valid_triplet(directory, stem="result"):
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=50)
    with (directory / f"{stem}.pdf").open("wb") as handle:
        writer.write(handle)
    (directory / f"{stem}.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 50"/>',
        encoding="utf-8",
    )
    Image.new("RGB", (1200, 700), "white").save(directory / f"{stem}.png", dpi=(300, 300))


def test_valid_triplet_passes(tmp_path):
    _write_valid_triplet(tmp_path)
    assert validate_triplet(tmp_path, "result", style_for("generic")) == []
    assert validate_directory(tmp_path, style_for("generic")) == (3, [])


def test_missing_and_empty_exports_fail(tmp_path):
    issues = validate_triplet(tmp_path, "missing", style_for("generic"))
    assert len(issues) == 3
    count, directory_issues = validate_directory(tmp_path, style_for("generic"))
    assert count == 0
    assert "no PDF" in directory_issues[0].message
