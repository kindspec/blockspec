# SPDX-License-Identifier: Apache-2.0 OR MIT
"""The `merge` case kind's runner.

The cases here are synthetic, and the implementation is a fake that records
what it was handed. What is tested is that the runner really merges with git,
and that a wrong outcome, wrong bytes or a wrong reading each fail.
"""

import os
import sys
from types import SimpleNamespace

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "conformance"))
import check_tree  # noqa: E402
import run_cases  # noqa: E402

BASE, OURS, THEIRS, MERGED = (
    "One.\n\nTwo.\n\nThree.\n",
    "Won.\n\nTwo.\n\nThree.\n",
    "One.\n\nTwo.\n\nTree.\n",
    "Won.\n\nTwo.\n\nTree.\n",
)
READING = {
    "accept": True,
    "blocks": [{"type": "paragraph", "lines": [1, 1]}],
    "leaves": [{"node": [0], "type": "paragraph", "content": "Won."}],
    "names": {},
}


def case(merge="clean", merged=MERGED, ours=OURS):
    files = {"base": BASE, "ours": ours, "theirs": THEIRS}
    if merged is not None:
        files["merged"] = merged
    return SimpleNamespace(files=files, expect={"kind": "merge", "merge": merge, **READING})


def run(c, reading=READING):
    seen = []

    def conform(text, queries):
        seen.append(text)
        return reading

    return list(run_cases.merge_handler(conform)(c)), seen


def test_the_right_answer_passes_and_the_merged_text_is_read():
    problems, seen = run(case())
    assert problems == []
    assert seen == [MERGED]


def test_the_merge_really_runs(monkeypatch):
    import kindkit.gitmerge

    monkeypatch.setattr(kindkit.gitmerge, "merge", lambda *a, **k: ("clean", "something else\n"))
    problems, seen = run(case())
    assert problems and "merged.md" in problems[0]
    assert seen == []


def test_the_wrong_outcome_fails():
    problems, seen = run(case(merge="conflict", merged=None))
    assert problems and "expected stock git to report conflict" in problems[0]
    assert seen == []


def test_a_conflict_the_case_expected_reaches_the_reader_with_markers():
    conflicted = "One.\n\nTwo.\n\nDifferent.\n"
    c = case(merge="conflict", merged=None, ours=conflicted)
    c.files["theirs"] = "One.\n\nTwo.\n\nOther.\n"
    _problems, seen = run(c, {"accept": False, "refusal": "conflict-marker"})
    assert len(seen) == 1
    assert "<<<<<<<" in seen[0]


def test_wrong_merged_bytes_fail():
    problems, _seen = run(case(merged="Won.\n\nTwo.\n\nTrey.\n"))
    assert problems and "merged.md" in problems[0]


def test_a_clean_merge_with_no_merged_file_fails():
    problems, _seen = run(case(merged=None))
    assert problems and "no merged.md" in problems[0]


def test_a_wrong_reading_fails():
    wrong = {**READING, "leaves": [{"node": [0], "type": "paragraph", "content": "Other."}]}
    problems, _seen = run(case(), wrong)
    assert problems and "leaves" in problems[0]


def test_a_missing_version_fails():
    c = case()
    del c.files["ours"]
    problems, _seen = run(c)
    assert problems and "no ours.md" in problems[0]


def test_the_tree_check_requires_each_file():
    full = {"base.md", "ours.md", "theirs.md", "merged.md", "WHY.md"}
    expect = {"merge": "clean"}
    assert list(check_tree.merge_file_problems({"expect": expect, "names": full})) == []
    for name in ("base.md", "ours.md", "theirs.md", "merged.md", "WHY.md"):
        got = list(check_tree.merge_file_problems({"expect": expect, "names": full - {name}}))
        assert got, name
