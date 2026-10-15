# SPDX-License-Identifier: Apache-2.0 OR MIT
"""`reference/` imports the standard library and nothing else.

A dependency there is one every independent implementation of the format
inherits, and taking one is an escalation in the org contract (section 7).
The audit parses the tree rather than importing it, so an import inside a
function no test calls is still seen.
"""

import ast
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFERENCE = os.path.join(ROOT, "reference")
INTERNAL = {"blockspec"}


def _imports(path):
    with open(path, encoding="utf-8") as handle:
        tree = ast.parse(handle.read(), path)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name.split(".")[0]
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            yield node.module.split(".")[0]


def _python_files():
    for dirpath, dirnames, files in os.walk(REFERENCE):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        yield from (os.path.join(dirpath, f) for f in files if f.endswith(".py"))


def test_reference_imports_only_the_standard_library():
    allowed = set(sys.stdlib_module_names) | INTERNAL | {"__future__"}
    files = list(_python_files())
    assert files, "found no Python under reference/, so nothing was audited"
    outside = {
        (os.path.relpath(path, ROOT), name)
        for path in files
        for name in _imports(path)
        if name not in allowed
    }
    assert not outside, sorted(outside)
