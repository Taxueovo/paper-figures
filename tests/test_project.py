import pytest

from paper_figures.project import setup_project


def test_setup_refuses_to_overwrite_without_force(tmp_path):
    project = tmp_path / "figures"
    created = setup_project(project, "ieee")
    assert len(created) == 3
    assert (project / "src").is_dir()
    assert '"journal": "ieee"' in (project / "style_config.json").read_text(encoding="utf-8")

    with pytest.raises(FileExistsError):
        setup_project(project, "nature")

    setup_project(project, "nature", force=True)
    assert '"journal": "nature"' in (project / "style_config.json").read_text(encoding="utf-8")


def test_collision_check_does_not_create_directories(tmp_path):
    project = tmp_path / "figures"
    project.mkdir()
    (project / "README.md").write_text("keep me", encoding="utf-8")
    with pytest.raises(FileExistsError):
        setup_project(project, "generic")
    assert not (project / "src").exists()
    assert not (project / "export").exists()
