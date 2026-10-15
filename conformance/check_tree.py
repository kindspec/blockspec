# SPDX-License-Identifier: MIT
"""Check that blockspec's case tree can fail, with no implementation at all.

    python3 conformance/check_tree.py [root]

Standard library only. It needs no implementation and no kindkit, and it
checks the tree, not a format reader:

  1. The tree holds at least run_cases.MIN_CASES cases.
  2. Every case passes when an implementation returns exactly what the case
     expects. A case nothing could pass is as useless as one nothing could fail.
  3. No trivial implementation passes a case it should not. "Accept, with an
     empty document" fails every accepting case and every refusal. "Refuse
     with code X" fails every accepting case and every refusal whose code is
     not X. So every accepting case asserts some structure, and every refusal
     case asserts one refusal, not merely "refused".
  4. Each element a case asserts is compared. One element at a time is
     dropped, altered, or added in the expected answer, and a line number or
     path index is given as a float or a bool; each altered answer must fail.
     A field the runner stopped comparing, or compared as a subset, shows up
     here.
  5. Every refusal names at least one control, each control is an accepting
     case in this tree, and every refusal code in case-body.schema.json has a
     refusal case.
  6. Each accepting case's blocks partition its input (0002): line ranges in
     order, inside the file, not overlapping, starting and ending on a
     non-blank line, and covering every non-blank line outside the
     frontmatter, which opens on line 1 with a non-blank line 2 and is
     delimited by `---` lines, the closing one perhaps followed by spaces or
     tabs.

Exit codes follow kindkit's: 0 every check passed, 1 at least one failed, 2 no
verdict (the tree is missing or empty).
"""

from __future__ import annotations

import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from run_cases import CASES, MIN_CASES, compare  # noqa: E402

CONTAINERS = ("list", "block_quote")


def load_tree(root: str) -> dict[str, dict]:
    if not os.path.isdir(root):
        raise SystemExit(_no_verdict(f"case root is not a directory: {root!r}"))
    cases = {}
    for dirpath, _dirs, names in sorted(os.walk(root)):
        if "expect.json" not in names:
            continue
        cid = os.path.relpath(dirpath, root).replace(os.sep, "/")
        with open(os.path.join(dirpath, "expect.json"), encoding="utf-8") as handle:
            expect = json.load(handle)
        with open(os.path.join(dirpath, "input.md"), encoding="utf-8", newline="") as handle:
            text = handle.read()
        cases[cid] = {"expect": expect, "input": text}
    if not cases:
        raise SystemExit(_no_verdict(f"no cases under {root!r}"))
    return cases


def _no_verdict(message: str) -> int:
    print(f"HARD FAILURE: {message}", file=sys.stderr)
    return 2


def answer(expect: dict) -> dict:
    """What a correct implementation returns for this case."""
    if not expect["accept"]:
        return {"accept": False, "refusal": expect["refusal"]}
    return {
        "accept": True,
        "frontmatter": copy.deepcopy(expect.get("frontmatter")),
        "blocks": copy.deepcopy(expect["blocks"]),
        "leaves": copy.deepcopy(expect["leaves"]),
        "names": copy.deepcopy(expect["names"]),
        "resolve": copy.deepcopy(expect.get("resolve", {})),
    }


def alterations(expect: dict):
    """Yield (label, answer) pairs, each differing from the right answer once."""
    right = answer(expect)
    if not expect["accept"]:
        return
    span = right["frontmatter"]
    for label, change in (
        ("frontmatter dropped" if span else "frontmatter added", None if span else [1, 1]),
        ("frontmatter end", [span[0], span[1] + 1] if span else None),
    ):
        if label == "frontmatter end" and not span:
            continue
        alt = copy.deepcopy(right)
        alt["frontmatter"] = change
        yield label, alt
    for i, block in enumerate(right["blocks"]):
        for label, change in (
            ("dropped", None),
            ("type", {**block, "type": "paragraph" if block["type"] != "paragraph" else "heading"}),
            ("start", {**block, "lines": [block["lines"][0] + 1, block["lines"][1]]}),
            ("end", {**block, "lines": [block["lines"][0], block["lines"][1] + 1]}),
        ):
            alt = copy.deepcopy(right)
            if change is None:
                del alt["blocks"][i]
            else:
                alt["blocks"][i] = change
            yield f"block {i} {label}", alt
    for i, leaf in enumerate(right["leaves"]):
        content = leaf["content"]
        changed = content + [["x"]] if isinstance(content, list) else content + "x"
        for label, change in (
            ("dropped", None),
            ("content", {**leaf, "content": changed}),
            ("node", {**leaf, "node": leaf["node"] + [0]}),
            ("type", {**leaf, "type": "paragraph" if leaf["type"] != "paragraph" else "heading"}),
        ):
            alt = copy.deepcopy(right)
            if change is None:
                del alt["leaves"][i]
            else:
                alt["leaves"][i] = change
            yield f"leaf {i} {label}", alt
    alt = copy.deepcopy(right)
    alt["blocks"].append({"type": "paragraph", "lines": [9999, 9999]})
    yield "blocks: one extra", alt
    alt = copy.deepcopy(right)
    alt["leaves"].append({"node": [9999], "type": "paragraph", "content": "extra"})
    yield "leaves: one extra", alt
    if right["blocks"]:
        alt = copy.deepcopy(right)
        alt["blocks"][0]["lines"] = [float(n) for n in alt["blocks"][0]["lines"]]
        yield "block 0 lines as floats", alt
    if right["leaves"]:
        alt = copy.deepcopy(right)
        alt["leaves"][0]["node"] = [float(n) for n in alt["leaves"][0]["node"]]
        yield "leaf 0 node as floats", alt
    if right["blocks"] and right["blocks"][0]["lines"][0] == 1:
        alt = copy.deepcopy(right)
        alt["blocks"][0]["lines"][0] = True
        yield "block 0 first line as a bool", alt
    alt = copy.deepcopy(right)
    alt["names"]["zz-not-declared"] = {"node": [0], "type": "paragraph"}
    yield "names: one extra", alt
    for field in ("names", "resolve"):
        for name in right[field]:
            alt = copy.deepcopy(right)
            del alt[field][name]
            yield f"{field} {name!r} dropped", alt
            alt = copy.deepcopy(right)
            alt[field][name] = (
                "#REF!(" + name + ")"
                if not isinstance(right[field][name], str)
                else {"node": [0], "type": "paragraph"}
            )
            yield f"{field} {name!r} retargeted", alt


def partition_problems(expect: dict, text: str):
    lines = text.split("\n")
    if text.endswith("\n"):
        lines.pop()
    covered = set()
    previous_end = 0
    span = expect.get("frontmatter")
    if span:
        if span[0] != 1 or not span[0] < span[1] <= len(lines):
            yield f"frontmatter {span} does not open on line 1 inside the file"
        elif lines[0] != "---" or lines[span[1] - 1].rstrip(" \t") != "---":
            yield f"frontmatter {span} is not delimited by `---` lines"
        elif not lines[1].strip():
            yield f"frontmatter {span} has a blank line 2, which makes line 1 a thematic break"
        covered.update(range(span[0], span[1] + 1))
        previous_end = span[1]
    for i, block in enumerate(expect["blocks"]):
        start, end = block["lines"]
        if not (previous_end < start <= end <= len(lines)):
            yield f"block {i} lines {block['lines']} out of order or outside the file"
            continue
        if not lines[start - 1].strip() or not lines[end - 1].strip():
            yield f"block {i} lines {block['lines']} start or end on a blank line"
        covered.update(range(start, end + 1))
        previous_end = end
    for number, line in enumerate(lines, 1):
        if line.strip() and number not in covered:
            yield f"line {number} is non-blank and in no block"
    for leaf in expect["leaves"]:
        top = leaf["node"][0]
        if top >= len(expect["blocks"]):
            yield f"leaf {leaf['node']} is under no block"
        elif len(leaf["node"]) == 1 and expect["blocks"][top]["type"] != leaf["type"]:
            yield f"leaf {leaf['node']} is a {leaf['type']}, block {top} a different type"
        elif len(leaf["node"]) > 1 and expect["blocks"][top]["type"] not in CONTAINERS:
            yield f"leaf {leaf['node']} is under block {top}, which is not a container"


def refusal_codes(root: str) -> list[str]:
    with open(os.path.join(root, "case-body.schema.json"), encoding="utf-8") as handle:
        schema = json.load(handle)
    for branch in schema["allOf"]:
        refusal = branch["then"]["properties"].get("refusal")
        if refusal:
            return refusal["enum"]
    raise SystemExit(_no_verdict("case-body.schema.json lists no refusal codes"))


def check(root: str) -> list[str]:
    cases = load_tree(root)
    codes = refusal_codes(root)
    problems = []
    if len(cases) < MIN_CASES:
        problems.append(f"tree: {len(cases)} cases, below the floor of {MIN_CASES}")

    trivial = {"accept-empty": {"accept": True, "blocks": [], "leaves": [], "names": {}}}
    trivial["refuse-without-a-code"] = {"accept": False, "refusal": None}
    for code in codes:
        trivial[f"refuse-{code}"] = {"accept": False, "refusal": code}

    seen_codes = set()
    for cid, case in cases.items():
        expect = case["expect"]
        misses = list(compare(expect, answer(expect)))
        if misses:
            problems.append(f"{cid}: fails its own right answer: {misses[0]}")
        for label, got in trivial.items():
            should_pass = not expect["accept"] and label == f"refuse-{expect['refusal']}"
            passed = not list(compare(expect, got))
            if passed != should_pass:
                verb = "passes" if passed else "fails"
                problems.append(f"{cid}: the trivial implementation {label!r} {verb} it")
        for label, got in alterations(expect):
            if not list(compare(expect, got)):
                problems.append(f"{cid}: an answer with {label} still passes")
        if expect["accept"]:
            for problem in partition_problems(expect, case["input"]):
                problems.append(f"{cid}: {problem}")
        else:
            seen_codes.add(expect["refusal"])
            for control in expect["controls"]:
                other = cases.get(control)
                if other is None:
                    problems.append(f"{cid}: control {control!r} is not a case in this tree")
                elif not other["expect"]["accept"]:
                    problems.append(f"{cid}: control {control!r} does not accept")
    for code in codes:
        if code not in seen_codes:
            problems.append(f"refusal code {code!r} has no refusal case")
    accepting = sum(1 for case in cases.values() if case["expect"]["accept"])
    print(f"{len(cases)} cases: {accepting} accept, {len(cases) - accepting} refuse")
    return problems


def main(argv: list[str]) -> int:
    root = argv[0] if argv else CASES
    problems = check(root)
    for problem in problems:
        print(f"  FAIL {problem}")
    print(f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
