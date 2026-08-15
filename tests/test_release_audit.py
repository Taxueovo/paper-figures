from pathlib import Path

from paper_figures.release_audit import audit_paths


def test_release_audit_detects_secret_and_private_path(tmp_path):
    secret = tmp_path / "config.txt"
    credential = "this-is-a-real" + "-looking-secret-value"
    private_path = "/" + "Users/alice/private/data.csv"
    secret.write_text(
        f"api_token = '{credential}'\n{private_path}\n",
        encoding="utf-8",
    )
    findings = audit_paths([secret], base=tmp_path)
    assert len(findings) == 2


def test_release_audit_accepts_normal_source(tmp_path):
    source = tmp_path / "module.py"
    source.write_text("def answer():\n    return 42\n", encoding="utf-8")
    assert audit_paths([source], base=Path(tmp_path)) == []
