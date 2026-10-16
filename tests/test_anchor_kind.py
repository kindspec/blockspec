# SPDX-License-Identifier: Apache-2.0 OR MIT
"""The `anchor` case kind's machinery: the runner and `check_tree.py`.

Every case here is synthetic and written to a temporary tree. None is a
conformance case, and the outcomes they expect say nothing about how an
anchor resolves: the implementation under test is a fake that checks what
the runner handed it and echoes an answer. What is tested is that the runner
builds the repository the README describes, and that a wrong answer fails.
"""

import copy
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNNER = os.path.join(ROOT, "conformance", "run_cases.py")

sys.path.insert(0, os.path.join(ROOT, "conformance"))
import anchor_cases  # noqa: E402
import check_tree  # noqa: E402

RECORD = "doc.md.notes/01J9Z3M8Q4X7V2K6T0R5N1B8CD.md"
OUTCOME = {
    "status": "EDITED",
    "leaf": {"node": [0], "type": "paragraph"},
    "span": [0, 2],
    "suggestion": {"gate": "apply", "written": "written/doc.md"},
}
REFUSED = {"status": "REFUSED(near-copy)", "leaf": None, "span": None, "suggestion": None}
UNIT = {"document": "doc.md", "target": {"node": [0], "type": "paragraph"}}
TRANSCLUSIONS = [{"leaf": {"node": [1], "type": "paragraph"}, "status": "RESOLVED", "unit": UNIT}]

# The fake implementation. It raises unless the repository is the one the
# test describes in the file ANCHOR_CHECK names, and then reports the answer
# that file holds: a stand-in for an implementation that got it right.
FAKE = r"""
import hashlib, json, os

def conform(text, queries):
    return {"accept": True, "blocks": [], "leaves": [], "names": {}}

def _id(fmt, text):
    data = text.encode("utf-8")
    return getattr(hashlib, fmt)(b"blob %d\0" % len(data) + data).hexdigest()

def resolve(repo, queries):
    with open(os.environ["ANCHOR_CHECK"], encoding="utf-8") as handle:
        check = json.load(handle)
    assert repo["object_format"] == check["object_format"], repo["object_format"]
    assert repo["tree"] == check["tree"], repo["tree"]
    for oid, text in repo["blobs"].items():
        assert oid == _id(repo["object_format"], text), oid
    assert sorted(repo["blobs"].values()) == sorted(check["blobs"]), repo["blobs"]
    assert queries == check["queries"], queries
    return check["answer"]
"""


def _id(fmt, text):
    data = text.encode("utf-8")
    return getattr(hashlib, fmt)(b"blob %d\0" % len(data) + data).hexdigest()


def _write(root, files):
    for path, text in files.items():
        full = os.path.join(root, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8", newline="") as handle:
            handle.write(text if isinstance(text, str) else json.dumps(text))


def _run(tmp_path, expect, files, check, fake=FAKE):
    root = tmp_path / "cases"
    _write(str(root / "anchor" / "one"), {"expect.json": expect, "WHY.md": "Synthetic.\n", **files})
    impl = tmp_path / "fake_impl.py"
    impl.write_text(fake, encoding="utf-8")
    checked = tmp_path / "check.json"
    checked.write_text(json.dumps(check), encoding="utf-8")
    report = tmp_path / "report.json"
    done = subprocess.run(
        [sys.executable, RUNNER, "--impl", str(impl), str(root), "--min-cases", "1"]
        + ["--report-json", str(report)],
        capture_output=True,
        text=True,
        env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", ANCHOR_CHECK=str(checked)),
    )
    failures = json.loads(report.read_text())["failures"] if report.exists() else None
    return done.returncode, failures, done.stdout + done.stderr


def _basic(fmt="sha1"):
    """A case, its files, and what the repository built from them must be."""
    base, doc, written = "Old text.\n", "New text.\n", "Ne text.\n"
    record = '---\nanchor: {"base": "{{blob:blobs/doc.md}}"}\n---\n'
    expect = {"kind": "anchor", "records": {RECORD: copy.deepcopy(OUTCOME)}}
    if fmt != "sha1":
        expect["object_format"] = fmt
    files = {
        "tree/doc.md": doc,
        f"tree/{RECORD}": record,
        "blobs/doc.md": base,
        "written/doc.md": written,
        "gone/doc.md": "Never committed.\n",
    }
    record = record.replace("{{blob:blobs/doc.md}}", _id(fmt, base))
    answer = {**OUTCOME, "suggestion": {"gate": "apply", "written": written}}
    check = {
        "object_format": fmt,
        "tree": {"doc.md": doc, RECORD: record},
        "blobs": [doc, record, base],
        "queries": {"records": [RECORD], "transclusions": []},
        "answer": {"records": {RECORD: answer}},
    }
    return expect, files, check


def test_the_runner_hands_over_the_repository_the_case_describes(tmp_path):
    code, failures, out = _run(tmp_path, *_basic())
    assert code == 0, out
    assert failures == []


def test_a_sha256_case_is_hashed_in_a_sha256_repository(tmp_path):
    expect, files, check = _basic("sha256")
    assert len(check["tree"][RECORD].split('"')[3]) == 64
    code, _, out = _run(tmp_path, expect, files, check)
    assert code == 0, out


def test_each_field_of_a_record_is_compared(tmp_path):
    for field, value in (
        ("status", "RESOLVED"),
        ("leaf", {"node": [1], "type": "paragraph"}),
        ("leaf", None),
        ("span", [0, 3]),
        ("span", [0.0, 2.0]),
        ("span", [False, 2]),
        ("leaf", {"node": [False], "type": "paragraph"}),
        ("suggestion", {"gate": "apply", "written": "New text.\n"}),
        ("suggestion", {"gate": "stale", "reason": None}),
        ("suggestion", None),
    ):
        expect, files, check = _basic()
        check["answer"]["records"][RECORD][field] = value
        code, failures, out = _run(tmp_path, expect, files, check)
        assert code == 1, (field, value, out)
        assert failures and all(field in f["message"] for f in failures), failures


def test_a_stale_reason_is_compared(tmp_path):
    expect, files, check = _basic()
    expect["records"][RECORD]["suggestion"] = {"gate": "stale", "reason": "unmappable-offset"}
    for reason, code in (("unmappable-offset", 0), (None, 1)):
        check["answer"]["records"][RECORD]["suggestion"] = {"gate": "stale", "reason": reason}
        assert _run(tmp_path, expect, files, check)[0] == code, reason


def test_a_record_with_no_outcome_fails(tmp_path):
    expect, files, check = _basic()
    check["answer"] = {"records": {}}
    code, failures, _ = _run(tmp_path, expect, files, check)
    assert code == 1
    assert [f["message"] for f in failures] == [f"record {RECORD!r}: no outcome reported"]


def test_an_implementation_without_resolve_fails_the_case(tmp_path):
    fake = FAKE.replace("def resolve(", "def not_resolve(")
    code, failures, _ = _run(tmp_path, *_basic(), fake=fake)
    assert code == 1
    assert [f["message"] for f in failures] == [
        "the implementation defines no resolve(repo, queries)"
    ]


def test_a_placeholder_naming_no_file_is_a_malformed_case(tmp_path):
    expect, files, check = _basic()
    files[f"tree/{RECORD}"] = files[f"tree/{RECORD}"].replace("blobs/doc.md", "blobs/none.md")
    code, failures, _ = _run(tmp_path, expect, files, check)
    assert code == 1
    assert [f["message"] for f in failures] == [
        f"the case is malformed: tree/{RECORD}: {{{{blob:blobs/none.md}}}} names no file "
        "in the case directory"
    ]


def _merge_case(sides, outcome, merged):
    expect, files, check = _basic()
    del files["tree/doc.md"]
    for side, text in zip(anchor_cases.SIDES, sides, strict=True):
        files[f"merge/{side}/doc.md"] = text
    expect["merge"] = {"doc.md": outcome}
    check["tree"]["doc.md"] = merged
    check["blobs"] = sorted({*check["blobs"][1:], *sides, merged})
    return expect, files, check


def test_a_clean_merge_is_the_current_file(tmp_path):
    sides = ("a\nb\nc\nd\ne\n", "A\nb\nc\nd\ne\n", "a\nb\nc\nd\nE\n")
    code, _, out = _run(tmp_path, *_merge_case(sides, "clean", "A\nb\nc\nd\nE\n"))
    assert code == 0, out


CONFLICT = ("a\nb\nc\n", "a\nB1\nc\n", "a\nB2\nc\n")
CONFLICTED = "a\n<<<<<<< HEAD\nB1\n=======\nB2\n>>>>>>> b1\nc\n"


def test_a_conflicted_merge_keeps_its_markers(tmp_path):
    code, _, out = _run(tmp_path, *_merge_case(CONFLICT, "conflict", CONFLICTED))
    assert code == 0, out


def test_a_merge_outcome_other_than_the_stated_one_fails(tmp_path):
    code, failures, _ = _run(tmp_path, *_merge_case(CONFLICT, "clean", CONFLICTED))
    assert code == 1
    assert [f["message"] for f in failures] == [
        "merge 'doc.md': expected clean, stock git reported conflict"
    ]


def _with_transclusions():
    expect, files, check = _basic()
    expect["transclusions"] = {"ref.md": copy.deepcopy(TRANSCLUSIONS)}
    files["tree/ref.md"] = "Text.\n"
    check["tree"]["ref.md"] = "Text.\n"
    check["blobs"].append("Text.\n")
    check["queries"]["transclusions"] = ["ref.md"]
    check["answer"]["transclusions"] = {"ref.md": copy.deepcopy(TRANSCLUSIONS)}
    return expect, files, check


def test_each_field_of_a_transclusion_is_compared(tmp_path):
    code, _, out = _run(tmp_path, *_with_transclusions())
    assert code == 0, out
    entry = TRANSCLUSIONS[0]
    for change in (
        None,
        [],
        [entry, entry],
        [{**entry, "status": "#REF!(x)"}],
        [{**entry, "unit": None}],
        [{**entry, "leaf": {"node": [1.0], "type": "paragraph"}}],
        [{**entry, "unit": {**UNIT, "target": {"node": [True], "type": "paragraph"}}}],
    ):
        expect, files, check = _with_transclusions()
        check["answer"]["transclusions"] = {} if change is None else {"ref.md": change}
        code, _, out = _run(tmp_path, expect, files, check)
        assert code == 1, (change, out)


def _tree(tmp_path, cases):
    root = tmp_path / "tree"
    with open(os.path.join(ROOT, "conformance", "cases", "case-body.schema.json")) as handle:
        _write(str(root), {"case-body.schema.json": handle.read()})
    for cid, (expect, files) in cases.items():
        _write(str(root / cid), {"expect.json": expect, "WHY.md": "Synthetic.\n", **files})
    return [p for p in check_tree.check(str(root)) if p.startswith("anchor/")]


def _parse_control():
    return {
        "kind": "parse",
        "accept": True,
        "blocks": [{"type": "paragraph", "lines": [1, 1]}],
        "leaves": [{"node": [0], "type": "paragraph", "content": "a"}],
        "names": {},
    }, {"input.md": "a\n"}


def test_check_tree_passes_a_well_formed_anchor_case(tmp_path):
    expect, files, _ = _basic()
    assert _tree(tmp_path, {"anchor/one": (expect, files)}) == []
    expect, files, _ = _with_transclusions()
    assert _tree(tmp_path / "t", {"anchor/one": (expect, files)}) == []


def test_check_tree_reports_what_a_case_gets_wrong_about_its_files(tmp_path):
    expect, files, _ = _basic()
    del files["written/doc.md"]
    files["tree/x.md"] = "{{blob:gone/none.md}}"
    files["blobs/self.md"] = "{{blob:blobs/doc.md}}"
    files["tree/y.md"] = "{{blob:blobs/self.md}}"
    other = "other.md.notes/01J9Z3M8Q4X7V2K6T0R5N1B8CE.md"
    expect["records"][other] = REFUSED
    expect["controls"] = ["anchor/two"]
    expect["merge"] = {"m.md": "clean"}
    files["tree/m.md"] = "here already\n"
    files["merge/base/m.md"] = "base\n"
    two = _basic()[:2]
    problems = _tree(tmp_path, {"anchor/one": (expect, files), "anchor/two": two})
    assert sorted(problems) == sorted(
        f"anchor/one: {p}"
        for p in (
            "tree/x.md: {{blob:gone/none.md}} names no file in the case directory",
            "tree/y.md: {{blob:blobs/self.md}} names a file that holds a placeholder itself",
            "merge 'm.md': no merge/ours/m.md",
            "merge 'm.md': no merge/theirs/m.md",
            "merge 'm.md': tree/m.md exists too, and the merge would replace it",
            f"{other!r}: no tree/{other}, and no merge makes it",
            f"record {RECORD!r}: written file 'written/doc.md' is missing",
        )
    )


def test_check_tree_requires_a_control_for_a_refusal(tmp_path):
    expect, files, _ = _basic()
    expect["records"][RECORD] = REFUSED
    del files["written/doc.md"]
    assert _tree(tmp_path, {"anchor/one": (expect, files)}) == [
        "anchor/one: expects a REFUSED outcome and names no control"
    ]
    for at, (controls, problem) in enumerate(
        (
            (["anchor/one"], "names itself as its control"),
            (["anchor/none"], "control 'anchor/none' is not a case in this tree"),
            (["x/control"], "control 'x/control' is not an anchor case"),
        )
    ):
        expect["controls"] = controls
        cases = {"anchor/one": (expect, files), "x/control": _parse_control()}
        assert _tree(tmp_path / str(at), cases) == [f"anchor/one: {problem}"]
    expect["controls"] = ["anchor/two"]
    cases = {"anchor/one": (expect, files), "anchor/two": _basic()[:2]}
    assert _tree(tmp_path / "ok", cases) == []


def test_check_tree_finds_a_comparison_that_was_dropped(tmp_path, monkeypatch):
    """If the runner stopped comparing a field, an alteration of it would
    pass, and check_tree must say so."""
    monkeypatch.setattr(anchor_cases, "TRANSCLUSION_FIELDS", ("leaf", "status"))
    expect, files, _ = _with_transclusions()
    assert _tree(tmp_path, {"anchor/one": (expect, files)}) == [
        "anchor/one: an answer with transclusions in 'ref.md' entry 0 unit still passes",
        "anchor/one: an answer with transclusions in 'ref.md' entry 0 unit as floats still passes",
        "anchor/one: an answer with transclusions in 'ref.md' entry 0 unit as bools still passes",
    ]


def test_check_tree_finds_a_case_that_an_empty_answer_passes(tmp_path, monkeypatch):
    """A runner that let a missing outcome through would let an
    implementation that reports nothing pass, and check_tree must say so."""
    compare = anchor_cases.compare

    def lenient(expect, got, files):
        if got == {"records": {}, "transclusions": {}}:
            return iter(())
        return compare(expect, got, files)

    monkeypatch.setattr(anchor_cases, "compare", lenient)
    expect, files, _ = _basic()
    problems = _tree(tmp_path, {"anchor/one": (expect, files)})
    assert "anchor/one: an implementation that reports nothing passes it" in problems, problems


def test_check_tree_reports_an_unreadable_file_with_a_readable_files_bytes(tmp_path):
    """Ids are content-addressed: a file outside tree/, blobs/ and merge/ that
    has a readable file's bytes names a readable blob, whatever its place."""
    expect, files, _ = _basic()
    files["gone/doc.md"] = files["blobs/doc.md"]
    files[f"tree/{RECORD}"] = files[f"tree/{RECORD}"].replace("blobs/doc.md", "gone/doc.md")
    assert _tree(tmp_path, {"anchor/one": (expect, files)}) == [
        "anchor/one: gone/doc.md: meant to be unreadable, but a readable file has the same "
        "bytes, so its blob id names a readable blob"
    ]
    files["gone/doc.md"] = "Never committed.\n"
    assert _tree(tmp_path / "ok", {"anchor/one": (expect, files)}) == []


def test_check_tree_alters_an_index_into_a_bool(tmp_path, monkeypatch):
    """If the runner took True for 1, a bool alteration would pass."""
    monkeypatch.setattr(anchor_cases, "not_integers", lambda value: iter(()))
    expect, files, _ = _basic()
    problems = _tree(tmp_path, {"anchor/one": (expect, files)})
    assert any("as bools still passes" in p for p in problems), problems
