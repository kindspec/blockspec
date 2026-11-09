# SPDX-License-Identifier: Apache-2.0 OR MIT
"""`blockspec check`, through its real entry point."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

GOOD = "# Title\n\nA paragraph.\n"
BAD = "<div>raw</div>\n"
REFERENCE = str(Path(__file__).resolve().parent.parent / "reference")


def run(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "PYTHONPATH": REFERENCE, "PYTHONDONTWRITEBYTECODE": "1"}
    return subprocess.run(
        [sys.executable, "-m", "blockspec", "check", *args],
        capture_output=True,
        text=True,
        cwd=cwd,
        env=env,
    )


def test_a_good_document_passes(tmp_path):
    (tmp_path / "a.md").write_text(GOOD)
    done = run(".", cwd=tmp_path)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "1 file(s) checked, 0 refused" in done.stdout


def test_a_refused_document_names_its_code_and_fails(tmp_path):
    (tmp_path / "a.md").write_text(BAD)
    done = run(".", cwd=tmp_path)
    assert done.returncode == 1
    assert "a.md" in done.stdout
    assert "[raw-html]" in done.stdout
    assert "1 file(s) checked, 1 refused" in done.stdout


def test_one_refusal_among_good_documents_fails_the_run(tmp_path):
    (tmp_path / "a.md").write_text(GOOD)
    (tmp_path / "b.md").write_text(BAD)
    assert run(".", cwd=tmp_path).returncode == 1


def test_github_format_annotates_the_file(tmp_path):
    (tmp_path / "a,b.md").write_text(BAD)
    done = run("--format", "github", ".", cwd=tmp_path)
    assert done.returncode == 1
    line = next(x for x in done.stdout.splitlines() if x.startswith("::error"))
    assert "a%2Cb.md" in line
    assert "title=blockspec [raw-html]::" in line


def test_a_missing_path_is_no_verdict(tmp_path):
    done = run("nope.md", cwd=tmp_path)
    assert done.returncode == 2
    assert "no such file" in done.stderr


def test_a_directory_with_no_documents_is_no_verdict(tmp_path):
    (tmp_path / "a.txt").write_text(GOOD)
    done = run(".", cwd=tmp_path)
    assert done.returncode == 2
    assert "no documents" in done.stderr


def test_a_named_file_is_read_whatever_its_suffix(tmp_path):
    (tmp_path / "a.txt").write_text(BAD)
    assert run("a.txt", cwd=tmp_path).returncode == 1


def test_a_file_that_is_not_utf8_is_refused(tmp_path):
    (tmp_path / "a.md").write_bytes(b"caf\xe9\n")
    done = run(".", cwd=tmp_path)
    assert done.returncode == 1
    assert "not UTF-8" in done.stdout


def test_notes_directories_and_git_are_not_documents(tmp_path):
    (tmp_path / "a.md").write_text(GOOD)
    for skipped in ("a.md.notes", ".git"):
        (tmp_path / skipped).mkdir()
        (tmp_path / skipped / "r.md").write_text(BAD)
    done = run(".", cwd=tmp_path)
    assert done.returncode == 0, done.stdout
    assert "1 file(s) checked" in done.stdout
