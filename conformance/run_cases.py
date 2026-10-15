# SPDX-License-Identifier: MIT
"""Run blockspec's conformance tree against an implementation.

    python conformance/run_cases.py --impl FILE [root] [--min-cases N] [--report-json PATH]

FILE is a Python file that defines

    conform(text: str, queries: list[str]) -> dict

`text` is a case's `input.md`, exactly as its bytes decode. `queries` is the
case's `resolve` names, in order. The returned object has the shape of the
case's `expect.json` body (see cases/README.md): `accept`, and then either
`refusal`, or `frontmatter` (absent or null when there is none), `blocks`,
`leaves`, `names` and `resolve`. An implementation in
another language needs a FILE that calls out to it.

Nothing is checked without an implementation, so there is no pass to report:

    no --impl                  exit 2, no verdict
    a missing or empty tree    exit 2, no verdict  (kindkit)
    fewer than MIN_CASES       exit 2, no verdict  (kindkit, --min-cases)
    any case failed            exit 1
    every case passed          exit 0

Exit 2 writes no report, so a caller that only counts failures cannot read
"nothing ran" as "nothing failed".

kindkit is not vendored. Run this with it on the path, for example:

    KINDKIT="git+https://github.com/kindspec/kindkit@6ebd80daba23e0d49a19e24b7ee4c85cedb926df"
    uv run --no-project --with "kindkit @ $KINDKIT" \
        python conformance/run_cases.py --impl FILE
"""

from __future__ import annotations

import importlib.util
import os
import sys
from collections.abc import Callable, Iterator, Mapping

HERE = os.path.dirname(os.path.abspath(__file__))
CASES = os.path.join(HERE, "cases")

#: The floor. A run that finds fewer cases than this is a tree that shrank, and
#: is no verdict rather than a pass. Raise it when cases are added; never lower
#: it to make a run go green.
MIN_CASES = 237

EXIT_NO_VERDICT = 2

ACCEPT_FIELDS = ("blocks", "leaves", "names")


def _not_integers(value: object) -> Iterator[object]:
    """Every bool or float in `value`. Python's == treats True as 1 and 1.0 as
    1, so a line number or a path index has to be checked for its type."""
    if isinstance(value, bool | float):
        yield value
    elif isinstance(value, Mapping):
        for item in value.values():
            yield from _not_integers(item)
    elif isinstance(value, list | tuple):
        for item in value:
            yield from _not_integers(item)


def compare(expect: Mapping[str, object], got: object) -> Iterator[str]:
    """Yield one message per way `got` differs from the case's `expect`."""
    if not isinstance(got, Mapping):
        yield f"the implementation returned {type(got).__name__}, not an object"
        return
    if got.get("accept") is not expect["accept"]:
        want = "accept" if expect["accept"] else f"refuse with {expect['refusal']!r}"
        have = "accept" if got.get("accept") is True else f"refuse with {got.get('refusal')!r}"
        yield f"expected {want}, got {have}"
        return
    if not expect["accept"]:
        if got.get("refusal") != expect["refusal"]:
            yield f"expected refusal {expect['refusal']!r}, got {got.get('refusal')!r}"
        return
    if got.get("frontmatter") != expect.get("frontmatter"):
        yield f"frontmatter: expected {expect.get('frontmatter')!r}, got {got.get('frontmatter')!r}"
    for field in ACCEPT_FIELDS:
        if got.get(field) != expect[field]:
            yield f"{field}: expected {expect[field]!r}, got {got.get(field)!r}"
    for field in ("frontmatter", *ACCEPT_FIELDS):
        for value in _not_integers(got.get(field)):
            yield f"{field}: {value!r} where a line number or path index must be an integer"
    wanted = expect.get("resolve", {})
    resolved = got.get("resolve")
    if not isinstance(resolved, Mapping):
        resolved = {}
    for name, target in wanted.items():
        if resolved.get(name) != target:
            yield f"resolve {name!r}: expected {target!r}, got {resolved.get(name)!r}"
        for value in _not_integers(resolved.get(name)):
            yield f"resolve {name!r}: {value!r} where a path index must be an integer"


def handler(conform: Callable[[str, list[str]], object]):
    def parse(case) -> Iterator[str]:
        if "input" not in case.files:
            yield "the case has no input.md"
            return
        queries = list(case.expect.get("resolve", {}))
        yield from compare(case.expect, conform(case.files["input"], queries))

    return parse


def load(path: str) -> Callable[[str, list[str]], object]:
    spec = importlib.util.spec_from_file_location("blockspec_under_test", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path!r} as a Python file")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.conform


def main(argv: list[str]) -> int:
    impl = None
    rest = list(argv)
    for at, arg in enumerate(rest):
        if arg.startswith("--impl="):
            rest[at : at + 1] = ["--impl", arg[len("--impl=") :]]
            break
    if "--impl" in rest:
        at = rest.index("--impl")
        if at + 1 >= len(rest):
            print("HARD FAILURE: --impl needs a file", file=sys.stderr)
            return EXIT_NO_VERDICT
        impl = rest[at + 1]
        del rest[at : at + 2]
    if impl is None:
        print(
            "HARD FAILURE: no implementation under test (--impl FILE). "
            "Nothing was checked, so there is no pass to report.",
            file=sys.stderr,
        )
        return EXIT_NO_VERDICT
    try:
        from kindkit import Adapter, cli
    except ImportError as exc:
        print(f"HARD FAILURE: kindkit is not importable: {exc}", file=sys.stderr)
        return EXIT_NO_VERDICT
    try:
        conform = load(impl)
    except Exception as exc:  # noqa: BLE001 -- any failure to load is no verdict
        print(f"HARD FAILURE: cannot load the implementation: {exc}", file=sys.stderr)
        return EXIT_NO_VERDICT
    adapter = Adapter(fixture_suffixes=(".md",), handlers={"parse": handler(conform)})
    return cli.main(
        adapter,
        rest,
        prog="run_cases.py",
        default_root=CASES,
        default_min_cases=MIN_CASES,
    )


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
