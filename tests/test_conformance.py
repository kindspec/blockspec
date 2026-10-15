# SPDX-License-Identifier: Apache-2.0 OR MIT
"""The conformance tree against the reference, through the runner CI uses.

The tree is the deliverable; running it under pytest is a convenience.
`just conform` runs the same command directly.
"""

import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNNER = os.path.join(ROOT, "conformance", "run_cases.py")
CASES = os.path.join(ROOT, "conformance", "cases")
IMPL = os.path.join(ROOT, "reference", "blockspec", "document.py")

sys.path.insert(0, os.path.join(ROOT, "conformance"))
from run_cases import MIN_CASES  # noqa: E402


def _run(*args):
    return subprocess.run([sys.executable, RUNNER, *args], cwd=ROOT, capture_output=True, text=True)


def _case_dirs():
    return {
        os.path.relpath(dirpath, CASES).replace(os.sep, "/")
        for dirpath, _dirs, files in os.walk(CASES)
        if "expect.json" in files
    }


def test_the_reference_passes_every_case_in_the_tree(tmp_path):
    """Exit 0 alone is not the claim: the report must say the whole tree ran,
    from this tree, and nothing failed."""
    report = tmp_path / "report.json"
    r = _run("--impl", IMPL, "--report-json", str(report))
    assert r.returncode == 0, r.stdout + r.stderr
    got = json.loads(report.read_text(encoding="utf-8"))
    assert got["root"] == CASES
    assert set(got["cases"]) == _case_dirs()
    assert len(got["cases"]) >= MIN_CASES
    assert got["failures"] == []


def test_the_runner_with_no_implementation_is_no_verdict():
    r = _run()
    assert r.returncode == 2, r.stdout + r.stderr
