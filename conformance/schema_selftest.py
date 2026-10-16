# SPDX-License-Identifier: MIT
"""Check that case-body.schema.json accepts an `anchor` body and rejects
broken ones, with kindkit's own validator.

    python3 conformance/schema_selftest.py <kindkit checkout>

The bodies are synthetic and written to a temporary tree; none is a
conformance case, and none says anything about how an anchor resolves. Each
broken body breaks one rule of the schema's `anchor` branch, and each is
validated in a tree of its own, so every rule is seen to reject on its own.
Exit 0 when the good body validates and every broken one is rejected; 1
otherwise; 2 when the validator cannot be run.
"""

from __future__ import annotations

import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA = os.path.join(HERE, "cases", "case-body.schema.json")

LEAF = {"node": [0], "type": "paragraph"}
RECORD = "doc.md.notes/01J9Z3M8Q4X7V2K6T0R5N1B8CD.md"

GOOD = {
    "kind": "anchor",
    "object_format": "sha256",
    "merge": {"doc.md": "clean"},
    "records": {
        RECORD: {"status": "EDITED", "leaf": LEAF, "span": [0, 3], "suggestion": None},
        "doc.md.notes/01J9Z3M8Q4X7V2K6T0R5N1B8CE.md": {
            "status": "RESOLVED",
            "leaf": LEAF,
            "span": [1, 2],
            "suggestion": {"gate": "apply", "written": "written/doc.md"},
        },
        "doc.md.notes/01J9Z3M8Q4X7V2K6T0R5N1B8CF.md": {
            "status": "DETACHED",
            "leaf": LEAF,
            "span": None,
            "suggestion": {"gate": "stale", "reason": None},
        },
        "doc.md.notes/01J9Z3M8Q4X7V2K6T0R5N1B8CG.md": {
            "status": "REFUSED(near-copy)",
            "leaf": None,
            "span": None,
            "suggestion": {"gate": "stale", "reason": None},
        },
        "doc.md.notes/01J9Z3M8Q4X7V2K6T0R5N1B8CJ.md": {
            "status": "EDITED",
            "leaf": LEAF,
            "span": [0, 1],
            "suggestion": {"gate": "stale", "reason": "unmappable-offset"},
        },
        "doc.md.notes/01J9Z3M8Q4X7V2K6T0R5N1B8CH.md": {
            "status": "#REF!(reply-to)",
            "leaf": None,
            "span": None,
            "suggestion": None,
        },
    },
    "transclusions": {
        "dir/ref.md": [
            {
                "leaf": LEAF,
                "status": "RESOLVED",
                "unit": {"document": "doc.md", "target": {"region": [LEAF]}},
            },
            {"leaf": LEAF, "status": "REFUSED(pinned-orphaned)", "unit": None},
            {"leaf": LEAF, "status": "#REF!(gone)", "unit": None},
        ],
        "empty.md": [],
    },
    "controls": ["anchor/x/y"],
}


def _broken():
    """(label, body), each with one rule broken."""

    def edit(change):
        body = copy.deepcopy(GOOD)
        change(body)
        return body

    def record(field, value, path=RECORD):
        return edit(lambda b: b["records"][path].__setitem__(field, value))

    def entry(field, value, at=0):
        return edit(lambda b: b["transclusions"]["dir/ref.md"][at].__setitem__(field, value))

    yield "an unknown kind", edit(lambda b: b.__setitem__("kind", "anchors"))
    yield (
        "no records and no transclusions",
        edit(lambda b: (b.pop("records"), b.pop("transclusions"))),
    )
    yield "an accept field", edit(lambda b: b.__setitem__("accept", True))
    yield "an unknown field", edit(lambda b: b.__setitem__("extra", 1))
    yield "an unknown object format", edit(lambda b: b.__setitem__("object_format", "md5"))
    yield "an unknown merge outcome", edit(lambda b: b.__setitem__("merge", {"doc.md": "ok"}))
    yield (
        "a merge path with a .. segment",
        edit(lambda b: b.__setitem__("merge", {"../doc.md": "clean"})),
    )
    yield (
        "a record outside a notes directory",
        edit(lambda b: b["records"].__setitem__("doc.md", b["records"].pop(RECORD))),
    )
    yield "an unknown record status", record("status", "FOUND")
    yield "an unknown refusal reason", record("status", "REFUSED(name-rebound)")
    yield "a missing record field", edit(lambda b: b["records"][RECORD].pop("span"))
    yield "an extra record field", record("message", "x")
    yield "EDITED with no leaf", record("leaf", None)
    yield "EDITED with no span", record("span", None)
    yield "a leaf of a type that bears no text", record("leaf", {"node": [0], "type": "html_block"})
    yield "a span of one offset", record("span", [0])
    yield "a negative offset", record("span", [-1, 3])
    yield "a float offset", record("span", [0, 3.5])
    path = "doc.md.notes/01J9Z3M8Q4X7V2K6T0R5N1B8CF.md"
    yield "DETACHED with a span", record("span", [0, 1], path)
    path = "doc.md.notes/01J9Z3M8Q4X7V2K6T0R5N1B8CG.md"
    yield "REFUSED with a leaf", record("leaf", LEAF, path)
    yield (
        "unmappable-offset on a refused anchor",
        record("suggestion", {"gate": "stale", "reason": "unmappable-offset"}, path),
    )
    yield (
        "an unknown stale reason",
        record("suggestion", {"gate": "stale", "reason": "status-not-open"}, path),
    )
    yield (
        "a stale gate with a written file",
        record("suggestion", {"gate": "stale", "reason": None, "written": "w.md"}, path),
    )
    yield "an apply gate with no written file", record("suggestion", {"gate": "apply"}, path)
    yield (
        "an apply gate on a refused anchor",
        record("suggestion", {"gate": "apply", "written": "written/doc.md"}, path),
    )
    yield "an unknown gate", record("suggestion", {"gate": "maybe", "reason": None}, path)
    path = "doc.md.notes/01J9Z3M8Q4X7V2K6T0R5N1B8CH.md"
    yield "a reply with a suggestion", record("suggestion", {"gate": "stale", "reason": None}, path)
    yield "a transclusion with an unknown reason", entry("status", "REFUSED(span-ambiguous)")
    yield (
        "a transclusion leaf of a type that bears no text",
        entry("leaf", {"node": [0], "type": "list"}),
    )
    yield (
        "a transclusion leaf that is not a paragraph",
        entry("leaf", {"node": [0], "type": "heading"}),
    )
    reply = "doc.md.notes/01J9Z3M8Q4X7V2K6T0R5N1B8CH.md"
    yield "a span of three offsets", record("span", [0, 1, 2])
    yield "an empty node path", record("leaf", {"node": [], "type": "paragraph"})
    yield "a reply with a leaf", record("leaf", LEAF, reply)
    yield "a record status of #REF!(name)", record("status", "#REF!(name)", reply)
    yield "an empty records object", edit(lambda b: b.__setitem__("records", {}))
    yield "an empty merge object", edit(lambda b: b.__setitem__("merge", {}))
    yield (
        "a unit document with a .. segment",
        entry("unit", {"document": "a/../doc.md", "target": LEAF}),
    )
    yield "a control that is not a case id", edit(lambda b: b.__setitem__("controls", ["Case"]))
    yield "a resolved transclusion with no unit", entry("unit", None)
    yield (
        "a refused transclusion with a unit",
        entry("unit", {"document": "doc.md", "target": LEAF}, 1),
    )
    yield "a unit with no target", entry("unit", {"document": "doc.md"})
    yield (
        "a unit with an absolute document path",
        entry("unit", {"document": "/doc.md", "target": LEAF}),
    )
    yield (
        "a missing transclusion field",
        edit(lambda b: b["transclusions"]["dir/ref.md"][0].pop("unit")),
    )
    yield "empty controls", edit(lambda b: b.__setitem__("controls", []))


def _validate(validator: str, body: dict, workdir: str) -> int:
    root = tempfile.mkdtemp(dir=workdir)
    shutil.copy(SCHEMA, root)
    case = os.path.join(root, "anchor", "synthetic")
    os.makedirs(case)
    with open(os.path.join(case, "expect.json"), "w", encoding="utf-8") as handle:
        json.dump(body, handle)
    with open(os.path.join(case, "WHY.md"), "w", encoding="utf-8") as handle:
        handle.write("A synthetic body for the schema's self-test.\n")
    done = subprocess.run([sys.executable, validator, root], capture_output=True, text=True)
    return done.returncode


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: schema_selftest.py <kindkit checkout>", file=sys.stderr)
        return 2
    validator = os.path.join(argv[0], "tools", "validate_case_tree.py")
    if not os.path.isfile(validator):
        print(f"HARD FAILURE: no validator at {validator!r}", file=sys.stderr)
        return 2
    workdir = tempfile.mkdtemp(prefix="blockspec-schema-")
    problems = []
    try:
        code = _validate(validator, GOOD, workdir)
        if code != 0:
            print(f"HARD FAILURE: the good body did not validate (exit {code})", file=sys.stderr)
            return 2
        print("  accepted  the good body")
        for label, body in _broken():
            code = _validate(validator, body, workdir)
            verdict = "rejected" if code == 1 else f"exit {code}"
            print(f"  {verdict:<9} {label}")
            if code != 1:
                problems.append(label)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    print(f"{len(problems)} broken body(ies) not rejected")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
