# SPDX-License-Identifier: Apache-2.0 OR MIT
"""`tests/edit-cases/` against `blockspec.edit`.

The cases pin the reference's editing API (`docs/editing-api.md`); their
format is in `tests/edit-cases/README.md`. The runner reads only the case
files, never a case definition in code.
"""

import json
import os

import pytest
from blockspec import Refusal, edit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CASES = os.path.join(ROOT, "tests", "edit-cases")

#: The floor. Fewer cases than this is a tree that shrank, and fails rather
#: than passing on what is left. Raise it when cases are added.
MIN_CASES = 113


def _read(case, name):
    with open(os.path.join(CASES, case, name), "rb") as handle:
        return handle.read().decode("utf-8")


def _cases():
    out = {}
    for dirpath, _dirs, files in os.walk(CASES):
        if "expect.json" in files:
            case = os.path.relpath(dirpath, CASES).replace(os.sep, "/")
            with open(os.path.join(dirpath, "expect.json"), encoding="utf-8") as handle:
                out[case] = json.load(handle)
    return dict(sorted(out.items()))


CASE_LIST = _cases()


def _run(case, expect):
    """The text returned, or the refusal's code."""
    text = _read(case, "input.md")
    op = expect["op"]
    try:
        if op == "replace":
            return edit.replace_block(text, expect["node"], _read(case, "source.md")), None
        if op == "insert":
            where = {k: expect[k] for k in ("before", "after") if k in expect}
            return edit.insert_block(text, _read(case, "source.md"), **where), None
        if op == "delete":
            return edit.delete_block(text, expect["node"]), None
    except Refusal as refusal:
        return None, refusal.code
    raise AssertionError(f"{case}: unknown op {op!r}")


def test_the_tree_holds_cases():
    assert len(CASE_LIST) >= MIN_CASES, f"{len(CASE_LIST)} cases under {CASES}"


def test_every_api_reason_has_a_case():
    covered = {expect.get("refusal") for expect in CASE_LIST.values()}
    assert set(edit.REASONS) <= covered, sorted(set(edit.REASONS) - covered)


@pytest.mark.parametrize("case", list(CASE_LIST))
def test_case(case):
    expect = CASE_LIST[case]
    assert ("result" in expect) != ("refusal" in expect), "give exactly one of result, refusal"
    out, code = _run(case, expect)
    if "refusal" in expect:
        assert code == expect["refusal"], f"expected refusal {expect['refusal']!r}, got {code!r}"
        assert expect.get("controls"), "a refusal case lists its controls"
        for control in expect["controls"]:
            assert "result" in CASE_LIST.get(control, {}), (
                f"control {control!r} is no accepting case"
            )
    else:
        assert code is None, f"expected the edit to be made, got refusal {code!r}"
        assert out == _read(case, expect["result"])
