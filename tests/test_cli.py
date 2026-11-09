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
    assert "1 file(s) checked, 0 refused, 0 unreadable" in done.stdout


def test_a_refused_document_names_its_code_and_fails(tmp_path):
    (tmp_path / "a.md").write_text(BAD)
    done = run(".", cwd=tmp_path)
    assert done.returncode == 1
    assert "a.md" in done.stdout
    assert "[raw-html]" in done.stdout
    assert "1 file(s) checked, 1 refused, 0 unreadable" in done.stdout


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


def test_git_is_not_read(tmp_path):
    (tmp_path / "a.md").write_text(GOOD)
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "r.md").write_text(BAD)
    done = run(".", cwd=tmp_path)
    assert done.returncode == 0, done.stdout
    assert "1 file(s) checked" in done.stdout


def test_a_record_in_a_notes_directory_is_read(tmp_path):
    (tmp_path / "a.md").write_text(GOOD)
    (tmp_path / "a.md.notes").mkdir()
    (tmp_path / "a.md.notes" / "r.md").write_text(BAD)
    assert run(".", cwd=tmp_path).returncode == 1


def test_a_file_named_twice_is_counted_once(tmp_path):
    (tmp_path / "d").mkdir()
    (tmp_path / "d" / "a.md").write_text(GOOD)
    assert "1 file(s) checked" in run("d", "d/a.md", cwd=tmp_path).stdout


def test_a_dangling_link_in_a_directory_is_no_verdict(tmp_path):
    (tmp_path / "a.md").write_text(GOOD)
    (tmp_path / "b.md").symlink_to(tmp_path / "gone.md")
    done = run(".", cwd=tmp_path)
    assert done.returncode == 2, done.stdout + done.stderr
    assert "1 file(s) checked, 0 refused, 1 unreadable" in done.stdout


def test_a_refusal_outranks_an_unreadable_file(tmp_path):
    (tmp_path / "a.md").write_text(BAD)
    (tmp_path / "b.md").symlink_to(tmp_path / "gone.md")
    assert run(".", cwd=tmp_path).returncode == 1


def test_a_fifo_is_not_read(tmp_path):
    os.mkfifo(tmp_path / "a.md")
    done = run(".", cwd=tmp_path)
    assert done.returncode == 2


def test_nesting_too_deep_for_the_reader_is_no_verdict(tmp_path):
    (tmp_path / "a.md").write_text("> " * 5000 + "x\n")
    (tmp_path / "b.md").write_text(GOOD)
    done = run(".", cwd=tmp_path)
    assert done.returncode == 2, done.stdout + done.stderr
    assert "1 file(s) checked" in done.stdout


def test_a_name_the_terminal_cannot_print_does_not_crash(tmp_path):
    name = os.fsencode(tmp_path) + b"/caf\xe9.md"
    with open(name, "wb") as handle:
        handle.write(BAD.encode())
    done = subprocess.run(
        [sys.executable, "-m", "blockspec", "check", "."],
        capture_output=True,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": REFERENCE, "PYTHONIOENCODING": "utf-8"},
    )
    assert done.returncode == 1, done.stderr
    assert b"Traceback" not in done.stderr


def test_a_record_may_link_to_a_name_in_its_document(tmp_path):
    (tmp_path / "a.md").write_text(GOOD)
    (tmp_path / "a.md.notes").mkdir()
    (tmp_path / "a.md.notes" / "r.md").write_text("See [x](#title-only-there).\n")
    assert run(".", cwd=tmp_path).returncode == 0


def test_a_document_link_to_a_missing_name_is_refused(tmp_path):
    (tmp_path / "a.md").write_text("See [x](#gone).\n")
    done = run(".", cwd=tmp_path)
    assert done.returncode == 1
    assert "[dangling-link]" in done.stdout


def test_a_notes_directory_with_no_document_is_not_a_record(tmp_path):
    (tmp_path / "release.notes").mkdir()
    (tmp_path / "release.notes" / "r.md").write_text("See [x](#gone).\n")
    assert run(".", cwd=tmp_path).returncode == 1


def test_a_record_is_a_record_from_inside_its_directory(tmp_path):
    (tmp_path / "a.md").write_text(GOOD)
    notes = tmp_path / "a.md.notes"
    notes.mkdir()
    (notes / "r.md").write_text("See [x](#gone).\n")
    assert run(".", cwd=notes).returncode == 0
