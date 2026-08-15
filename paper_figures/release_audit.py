"""Fail a release when tracked content contains high-confidence private material."""

from __future__ import annotations

import argparse
import re
import subprocess
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

MAX_SCAN_BYTES = 5 * 1024 * 1024
MAX_HISTORY_COMMITS = 500
FORBIDDEN_NAMES = {
    ".env",
    "credentials.json",
    "id_dsa",
    "id_ed25519",
    "id_rsa",
    "secrets.json",
}
FORBIDDEN_SUFFIXES = {".key", ".p12", ".pfx", ".pem", ".sqlite", ".sqlite3"}
PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----"),
    "GitHub token": re.compile(r"(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,})"),
    "cloud access key": re.compile(r"(?:AKIA|ASIA)[0-9A-Z]{16}"),
    "API credential": re.compile(
        r"(?i)(?:api[_-]?key|api[_-]?token|client[_-]?secret|password)\s*[:=]\s*['\"][^'\"]{16,}['\"]"
    ),
    "private absolute path": re.compile(
        r"(?:/Users/[^/\s]+/|/home/[^/\s]+/|[A-Z]:\\Users\\[^\\\s]+\\)"
    ),
}


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    kind: str


def _is_forbidden_path(path: Path) -> bool:
    return path.name in FORBIDDEN_NAMES or path.suffix.lower() in FORBIDDEN_SUFFIXES


def audit_paths(paths: Iterable[Path], *, base: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in paths:
        relative = path.relative_to(base).as_posix()
        if path.is_symlink():
            findings.append(Finding(relative, 0, "symbolic link requires manual review"))
            continue
        if _is_forbidden_path(path):
            findings.append(Finding(relative, 0, "sensitive filename"))
            continue
        if not path.is_file() or path.stat().st_size > MAX_SCAN_BYTES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            for kind, pattern in PATTERNS.items():
                if pattern.search(line):
                    findings.append(Finding(relative, line_number, kind))
    return findings


def audit_history(root: Path) -> list[Finding]:
    revisions = subprocess.run(
        ["git", "rev-list", "--all"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    if len(revisions) > MAX_HISTORY_COMMITS:
        return [
            Finding("<git-history>", 0, f"history exceeds {MAX_HISTORY_COMMITS}-commit audit limit")
        ]
    findings: list[Finding] = []
    seen_blobs: set[str] = set()
    for revision in revisions:
        listing = subprocess.run(
            ["git", "ls-tree", "-r", "-z", revision],
            cwd=root,
            check=True,
            capture_output=True,
        ).stdout
        for entry in listing.split(b"\0"):
            if not entry:
                continue
            metadata, raw_path = entry.split(b"\t", 1)
            mode, kind, object_id = metadata.decode().split()
            path = Path(raw_path.decode())
            if path.name == Path(__file__).name:
                continue
            if _is_forbidden_path(path):
                findings.append(
                    Finding(f"{revision[:8]}:{path.as_posix()}", 0, "sensitive filename")
                )
            if kind != "blob" or object_id in seen_blobs or mode == "120000":
                continue
            seen_blobs.add(object_id)
            data = subprocess.run(
                ["git", "cat-file", "blob", object_id],
                cwd=root,
                check=True,
                capture_output=True,
            ).stdout
            if len(data) > MAX_SCAN_BYTES:
                continue
            try:
                text = data.decode("utf-8")
            except UnicodeDecodeError:
                continue
            for line_number, line in enumerate(text.splitlines(), start=1):
                for label, pattern in PATTERNS.items():
                    if pattern.search(line):
                        findings.append(
                            Finding(f"{revision[:8]}:{path.as_posix()}", line_number, label)
                        )
    return findings


def tracked_paths(root: Path) -> list[Path]:
    completed = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    return [root / item.decode() for item in completed.stdout.split(b"\0") if item]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--history", action="store_true", help="also scan reachable Git history")
    args = parser.parse_args()
    root = args.root.resolve()
    paths = [path for path in tracked_paths(root) if path.name != Path(__file__).name]
    findings = audit_paths(paths, base=root)
    if args.history:
        findings.extend(audit_history(root))
    for finding in findings:
        location = f":{finding.line}" if finding.line else ""
        print(f"{finding.kind}: {finding.path}{location}")
    if findings:
        print(f"Release audit failed with {len(findings)} finding(s).")
        return 1
    print(f"Release audit passed: {len(paths)} tracked files checked.")
    return 0
