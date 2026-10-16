# SPDX-License-Identifier: MIT
"""The `anchor` case kind: how a case states what SPEC.md section 11 resolves.

`cases/README.md`, *The kind `anchor`*, defines the case shape. This module
reads a case directory into the repository an implementation is handed,
compares what the implementation returns with the case, and lists what a
case directory gets wrong about its own files. `run_cases.py` drives it with
git and kindkit; `check_tree.py` uses the parts that need neither.

Standard library only at import time. Git is needed to hash blobs and to run
a case's merge, and kindkit's `gitmerge` to merge; both are reached only by
`Repository`, which `check_tree.py` never builds.
"""

from __future__ import annotations

import copy
import os
import re
import shutil
import subprocess
import tempfile
from collections.abc import Callable, Iterator, Mapping

#: `{{blob:PATH}}`: the object id of the file at PATH, relative to the case
#: directory. Written by the case author where a record's `base` or a pin's
#: `blob` goes, so a case holds content and never a hash.
PLACEHOLDER = re.compile(r"\{\{blob:([^{}]*)\}\}")

TREE = "tree/"
BLOBS = "blobs/"
MERGE = "merge/"
SIDES = ("base", "ours", "theirs")
OBJECT_FORMATS = ("sha1", "sha256")

#: Record statuses that put the anchor on a current leaf, and those that also
#: place its span there (SPEC.md section 11.6).
ON_A_LEAF = ("RESOLVED", "MOVED", "EDITED", "DETACHED")
WITH_A_SPAN = ("RESOLVED", "MOVED", "EDITED")

RECORD_FIELDS = ("status", "leaf", "span", "suggestion")
TRANSCLUSION_FIELDS = ("leaf", "status", "unit")


def read_case_files(case_dir: str) -> dict[str, str]:
    """Every file under the case directory but `expect.json`, by its path
    relative to the directory with `/` separators, read as exact bytes."""
    files = {}
    for dirpath, dirnames, names in os.walk(case_dir):
        dirnames.sort()
        for name in sorted(names):
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, case_dir).replace(os.sep, "/")
            if rel == "expect.json":
                continue
            with open(path, encoding="utf-8", newline="") as handle:
                files[rel] = handle.read()
    return files


def _placeholders(text: str) -> list[str]:
    return PLACEHOLDER.findall(text)


def _documents(expect: Mapping) -> list[str]:
    return [*expect.get("records", {}), *expect.get("transclusions", {})]


def fixture_problems(expect: Mapping, files: Mapping[str, str]) -> Iterator[str]:
    """What the case directory gets wrong about its own files. None of these
    needs git or an implementation, so `check_tree.py` reports them too."""
    for path, text in files.items():
        for target in _placeholders(text):
            if target not in files:
                yield f"{path}: {{{{blob:{target}}}}} names no file in the case directory"
            elif _placeholders(files[target]):
                yield f"{path}: {{{{blob:{target}}}}} names a file that holds a placeholder itself"
    merged = expect.get("merge", {})
    for path in merged:
        for side in SIDES:
            if f"{MERGE}{side}/{path}" not in files:
                yield f"merge {path!r}: no {MERGE}{side}/{path}"
        if f"{TREE}{path}" in files:
            yield f"merge {path!r}: {TREE}{path} exists too, and the merge would replace it"
    for path in _documents(expect):
        if f"{TREE}{path}" not in files and path not in merged:
            yield f"{path!r}: no {TREE}{path}, and no merge makes it"
    for path, outcome in expect.get("records", {}).items():
        suggestion = outcome.get("suggestion")
        if suggestion and suggestion.get("gate") == "apply":
            if suggestion.get("written") not in files:
                yield f"record {path!r}: written file {suggestion.get('written')!r} is missing"


def substitute(files: Mapping[str, str], blob_id: Callable[[str], str]) -> dict[str, str]:
    """Each file with every placeholder replaced by the object id of the file
    it names, hashed as its bytes stand."""
    return {
        path: PLACEHOLDER.sub(lambda m: blob_id(files[m.group(1)]), text)
        for path, text in files.items()
    }


def _stock_env(nowhere: str) -> dict[str, str]:
    """Git with no configuration from this machine, as kindkit's gitmerge
    runs it: a user's or a system's settings must not change a hash."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env["HOME"] = nowhere
    env["XDG_CONFIG_HOME"] = nowhere
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    env["GIT_ATTR_NOSYSTEM"] = "1"
    return env


class Repository:
    """A case directory as the repository an implementation is handed.

    Blob ids come from `git hash-object` in an empty repository of the case's
    object format, so they are git's, not this runner's. A merge is kindkit's
    `gitmerge.merge`, a stock `git merge` in a repository of its own."""

    def __init__(self, expect: Mapping, files: Mapping[str, str]) -> None:
        self.expect = expect
        self.object_format = expect.get("object_format", "sha1")
        self._dir = tempfile.mkdtemp(prefix="blockspec-anchor-")
        self._env = _stock_env(os.path.join(self._dir, ".no-home"))
        self._ids: dict[str, str] = {}
        repo = os.path.join(self._dir, "repo")
        done = subprocess.run(
            ["git", "init", "-q", f"--object-format={self.object_format}", repo],
            capture_output=True,
            text=True,
            env=self._env,
        )
        if done.returncode:
            self.close()
            raise RuntimeError(f"git init failed: {done.stderr.strip()}")
        self._repo = repo
        self.files = substitute(files, self.blob_id)

    def close(self) -> None:
        shutil.rmtree(self._dir, ignore_errors=True)

    def blob_id(self, text: str) -> str:
        if text not in self._ids:
            done = subprocess.run(
                ["git", "hash-object", "--no-filters", "--stdin"],
                input=text.encode("utf-8"),
                capture_output=True,
                cwd=self._repo,
                env=self._env,
            )
            if done.returncode:
                raise RuntimeError(f"git hash-object failed: {done.stderr.decode().strip()}")
            self._ids[text] = done.stdout.decode("ascii").strip()
        return self._ids[text]

    def build(self) -> tuple[dict, list[str]]:
        """The `repo` argument of `resolve`, and a message for each merge
        whose outcome is not the one the case states."""
        from kindkit.gitmerge import merge

        messages = []
        tree = {p[len(TREE) :]: t for p, t in self.files.items() if p.startswith(TREE)}
        readable = [t for p, t in self.files.items() if p.startswith((TREE, BLOBS, MERGE))]
        for path, want in self.expect.get("merge", {}).items():
            base, ours, theirs = (self.files[f"{MERGE}{side}/{path}"] for side in SIDES)
            outcome, text = merge(base, [ours, theirs], os.path.basename(path))
            if outcome != want:
                messages.append(f"merge {path!r}: expected {want}, stock git reported {outcome}")
            tree[path] = text
            readable.append(text)
        blobs = {self.blob_id(text): text for text in readable}
        repo = {"object_format": self.object_format, "tree": tree, "blobs": blobs}
        return repo, messages


def queries(expect: Mapping) -> dict[str, list[str]]:
    return {
        "records": list(expect.get("records", {})),
        "transclusions": list(expect.get("transclusions", {})),
    }


def not_integers(value: object) -> Iterator[object]:
    """Every bool or float in `value`: Python's == takes True for 1 and 1.0
    for 1, so a path index or an offset has to be checked for its type."""
    if isinstance(value, bool | float):
        yield value
    elif isinstance(value, Mapping):
        for item in value.values():
            yield from not_integers(item)
    elif isinstance(value, list | tuple):
        for item in value:
            yield from not_integers(item)


def compare(expect: Mapping, got: object, files: Mapping[str, str]) -> Iterator[str]:
    """One message per way `got` differs from the case. `files` are the case's
    files after placeholder substitution, for a suggestion's written file."""
    if not isinstance(got, Mapping):
        yield f"the implementation returned {type(got).__name__}, not an object"
        return
    records = got.get("records")
    records = records if isinstance(records, Mapping) else {}
    for path, want in expect.get("records", {}).items():
        have = records.get(path)
        if not isinstance(have, Mapping):
            yield f"record {path!r}: no outcome reported"
            continue
        for field in ("status", "leaf", "span"):
            if have.get(field) != want[field]:
                yield f"record {path!r} {field}: expected {want[field]!r}, got {have.get(field)!r}"
            for value in not_integers(have.get(field)):
                yield f"record {path!r} {field}: {value!r} is not an integer"
        yield from _compare_suggestion(path, want["suggestion"], have.get("suggestion"), files)
    lists = got.get("transclusions")
    lists = lists if isinstance(lists, Mapping) else {}
    for path, want in expect.get("transclusions", {}).items():
        have = lists.get(path)
        if not isinstance(have, list):
            yield f"transclusions in {path!r}: no list reported"
            continue
        if len(have) != len(want):
            yield f"transclusions in {path!r}: expected {len(want)}, got {len(have)}"
        for at, (one, other) in enumerate(zip(want, have, strict=False)):
            if not isinstance(other, Mapping):
                yield f"transclusion {at} in {path!r}: not an object"
                continue
            for field in TRANSCLUSION_FIELDS:
                if other.get(field) != one[field]:
                    yield (
                        f"transclusion {at} in {path!r} {field}: "
                        f"expected {one[field]!r}, got {other.get(field)!r}"
                    )
                for value in not_integers(other.get(field)):
                    yield f"transclusion {at} in {path!r} {field}: {value!r} is not an integer"


def _compare_suggestion(path: str, want, have, files: Mapping[str, str]) -> Iterator[str]:
    where = f"record {path!r} suggestion"
    if want is None:
        if have is not None:
            yield f"{where}: expected none, got {have!r}"
        return
    if not isinstance(have, Mapping):
        yield f"{where}: expected {want!r}, got {have!r}"
        return
    if have.get("gate") != want["gate"]:
        yield f"{where} gate: expected {want['gate']!r}, got {have.get('gate')!r}"
        return
    if want["gate"] == "apply":
        if have.get("written") != files[want["written"]]:
            yield f"{where}: the written document is not {want['written']!r}"
    elif have.get("reason") != want["reason"]:
        yield f"{where} reason: expected {want['reason']!r}, got {have.get('reason')!r}"


def answer(expect: Mapping, files: Mapping[str, str]) -> dict:
    """What a correct implementation returns for this case."""
    records = {}
    for path, want in expect.get("records", {}).items():
        outcome = {field: copy.deepcopy(want[field]) for field in RECORD_FIELDS}
        suggestion = outcome["suggestion"]
        if suggestion and suggestion["gate"] == "apply":
            suggestion["written"] = files[suggestion["written"]]
        records[path] = outcome
    return {"records": records, "transclusions": copy.deepcopy(expect.get("transclusions", {}))}


def _other_leaf(leaf):
    if leaf is None:
        return {"node": [0], "type": "paragraph"}
    return {**leaf, "node": [*leaf["node"], 0]}


def _floats(value):
    if isinstance(value, Mapping):
        return {k: _floats(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_floats(v) for v in value]
    return float(value) if isinstance(value, int) and not isinstance(value, bool) else value


def alterations(expect: Mapping, files: Mapping[str, str]) -> Iterator[tuple[str, dict]]:
    """Yield (label, answer) pairs, each differing from the right answer once."""
    right = answer(expect, files)
    for path, outcome in right["records"].items():
        where = f"record {path!r}"
        changes = {
            "dropped": None,
            "status": {
                **outcome,
                "status": "ORPHANED" if outcome["status"] != "ORPHANED" else "RESOLVED",
            },
            "leaf": {**outcome, "leaf": _other_leaf(outcome["leaf"])},
            "span": {
                **outcome,
                "span": [0, 1]
                if outcome["span"] is None
                else [*outcome["span"][:1], outcome["span"][1] + 1],
            },
        }
        suggestion = outcome["suggestion"]
        if suggestion is None:
            changes["suggestion"] = {**outcome, "suggestion": {"gate": "stale", "reason": None}}
        elif suggestion["gate"] == "apply":
            changes["suggestion gate"] = {
                **outcome,
                "suggestion": {"gate": "stale", "reason": None},
            }
            written = {**suggestion, "written": suggestion["written"] + "x"}
            changes["suggestion written"] = {**outcome, "suggestion": written}
        else:
            changes["suggestion dropped"] = {**outcome, "suggestion": None}
            flipped = None if suggestion["reason"] else "unmappable-offset"
            changes["suggestion reason"] = {
                **outcome,
                "suggestion": {**suggestion, "reason": flipped},
            }
        if outcome["leaf"] is not None:
            changes["leaf node as floats"] = {**outcome, "leaf": _floats(outcome["leaf"])}
        if outcome["span"] is not None:
            changes["span as floats"] = {**outcome, "span": _floats(outcome["span"])}
        for label, change in changes.items():
            alt = copy.deepcopy(right)
            if change is None:
                del alt["records"][path]
            else:
                alt["records"][path] = change
            yield f"{where} {label}", alt
    for path, entries in right["transclusions"].items():
        where = f"transclusions in {path!r}"
        alt = copy.deepcopy(right)
        alt["transclusions"][path].append(
            {"leaf": {"node": [9999], "type": "paragraph"}, "status": "RESOLVED", "unit": None}
        )
        yield f"{where}: one extra", alt
        for at, entry in enumerate(entries):
            changes = {
                "dropped": None,
                "leaf": {**entry, "leaf": _other_leaf(entry["leaf"])},
                "status": {
                    **entry,
                    "status": "REFUSED(name-rebound)"
                    if entry["status"] != "REFUSED(name-rebound)"
                    else "RESOLVED",
                },
                "unit": {
                    **entry,
                    "unit": {
                        "document": "zz-other.md",
                        "target": {"node": [0], "type": "paragraph"},
                    }
                    if entry["unit"] is None
                    else None,
                },
                "leaf node as floats": {**entry, "leaf": _floats(entry["leaf"])},
            }
            if entry["unit"] is not None:
                changes["unit as floats"] = {**entry, "unit": _floats(entry["unit"])}
            for label, change in changes.items():
                alt = copy.deepcopy(right)
                if change is None:
                    del alt["transclusions"][path][at]
                else:
                    alt["transclusions"][path][at] = change
                yield f"{where} entry {at} {label}", alt


def refuses(expect: Mapping) -> bool:
    """Whether the case expects any `REFUSED(...)` outcome, so that it must
    name a control."""
    statuses = [o["status"] for o in expect.get("records", {}).values()]
    statuses += [e["status"] for es in expect.get("transclusions", {}).values() for e in es]
    return any(s.startswith("REFUSED(") for s in statuses)
