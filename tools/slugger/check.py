# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Check the reference's slug table against github-slugger's regex.

    python3 tools/slugger/check.py PATH/TO/github-slugger/package/regex.js

Runs tools/slugger/ranges.mjs under node (see its header for how to fetch
github-slugger 2.0.0) and compares its ranges with `_SLUG_REMOVED_RANGES` in
reference/blockspec/document.py. Exit 0 when they are the same, 1 when they
differ, 2 when either side could not be read.

Only the removed-character class is compared. Lower-casing is the runtime's
own, and node and Python can disagree where their Unicode versions do.
"""

import ast
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOCUMENT = os.path.join(ROOT, "reference", "blockspec", "document.py")
RANGES = os.path.join(ROOT, "tools", "slugger", "ranges.mjs")


def _table() -> str:
    """The table as the source spells it. Read with `ast`, not imported, so a
    `.pyc` left by an earlier version of the file cannot answer for it."""
    with open(DOCUMENT, encoding="utf-8") as handle:
        tree = ast.parse(handle.read(), DOCUMENT)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "_SLUG_REMOVED_RANGES" for t in node.targets
        ):
            return ast.literal_eval(node.value)
    raise SystemExit(f"no _SLUG_REMOVED_RANGES in {DOCUMENT}")


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    done = subprocess.run(["node", RANGES, argv[0]], capture_output=True, text=True)
    if done.returncode != 0 or not done.stdout.split():
        print(f"node produced no ranges: {done.stderr.strip()}", file=sys.stderr)
        return 2
    theirs = done.stdout.split()
    ours = _table().split()
    if theirs == ours:
        print(f"{len(ours)} ranges, identical")
        return 0
    only_theirs = sorted(set(theirs) - set(ours))
    only_ours = sorted(set(ours) - set(theirs))
    print(
        f"differ: {len(only_theirs)} ranges only in the regex, {len(only_ours)} only in the table"
    )
    print(f"  only in the regex: {only_theirs[:10]}")
    print(f"  only in the table: {only_ours[:10]}")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
