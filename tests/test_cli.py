from paper_figures.cli import main


def test_generate_cli_rejects_missing_data(tmp_path, capsys):
    result = main(
        [
            "generate",
            "training",
            "--data",
            str(tmp_path / "missing.csv"),
            "--output-dir",
            str(tmp_path / "out"),
        ]
    )
    assert result == 2
    assert "Expected an existing CSV" in capsys.readouterr().err


def test_batch_cli_propagates_render_failure(tmp_path):
    source = tmp_path / "src"
    source.mkdir()
    (source / "fig_01_broken.py").write_text("raise RuntimeError('broken')\n", encoding="utf-8")

    result = main(
        [
            "batch",
            "--src-dir",
            str(source),
            "--export-dir",
            str(tmp_path / "export"),
        ]
    )

    assert result == 1
    assert (tmp_path / "export" / "latex_snippets.tex").is_file()


def test_batch_no_run_rejects_empty_export(tmp_path):
    export = tmp_path / "export"
    export.mkdir()
    assert main(["batch", "--no-run", "--export-dir", str(export)]) == 2


def test_setup_accepts_legacy_output_dir_option(tmp_path):
    destination = tmp_path / "legacy"
    assert main(["setup", "--output-dir", str(destination)]) == 0
    assert (destination / "style_config.json").is_file()


def test_invalid_style_config_returns_cli_error(tmp_path, capsys):
    config = tmp_path / "invalid.json"
    config.write_text("{}", encoding="utf-8")
    result = main(
        [
            "check",
            str(tmp_path),
            "--config",
            str(config),
            "--strict",
        ]
    )
    assert result == 2
    assert "invalid style config" in capsys.readouterr().err
