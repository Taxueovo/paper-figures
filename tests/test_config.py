import json

import pytest

from paper_figures.config import load_style_config, style_for


def test_presets_are_independent():
    first = style_for("generic")
    first["font_size"]["title"] = 99
    assert style_for("generic")["font_size"]["title"] != 99


def test_invalid_style_is_rejected(tmp_path):
    path = tmp_path / "style.json"
    path.write_text(json.dumps({"journal": "broken"}), encoding="utf-8")
    with pytest.raises(ValueError, match="missing"):
        load_style_config(path)
