from paper_figures.discovery import discover


def test_discovery_is_bounded_and_skips_hidden_directories(tmp_path):
    (tmp_path / "metrics.csv").write_text("epoch,loss\n1,0.5\n", encoding="utf-8")
    (tmp_path / "model.py").write_text("class Net(nn.Module): pass\n", encoding="utf-8")
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv" / "hidden.csv").write_text("secret\n", encoding="utf-8")
    (tmp_path / "figures").mkdir()

    result = discover(tmp_path)

    assert result.csv_files == ["metrics.csv"]
    assert result.model_files == ["model.py"]
    assert result.existing_figure_dirs == ["figures"]
