# SPDX-License-Identifier: Apache-2.0 OR MIT
"""One kindkit commit, named in three places.

pyproject.toml's dev group installs the runner and the gate the tests and
`just` recipes use; conformance.yml's KINDKIT_SHA fetches the validator and
runner CI uses; run_cases.py's docstring tells a reader which kit to run it
with. Two kits would mean the gates check a contract the code under them does
not keep.
"""

import os
import re
import tomllib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as handle:
        return handle.read()


def test_every_kindkit_pin_names_the_same_commit():
    with open(os.path.join(ROOT, "pyproject.toml"), "rb") as handle:
        dev = tomllib.load(handle)["dependency-groups"]["dev"]
    pins = {
        "pyproject.toml": [
            m for dep in dev for m in re.findall(r"kindspec/kindkit@([0-9a-f]{40})", dep)
        ],
        "conformance.yml": re.findall(
            r"KINDKIT_SHA: ([0-9a-f]{40})", _read(".github", "workflows", "conformance.yml")
        ),
        "run_cases.py": re.findall(
            r"kindspec/kindkit@([0-9a-f]{40})", _read("conformance", "run_cases.py")
        ),
    }
    for where, found in pins.items():
        assert len(found) == 1, f"{where}: expected one kindkit pin, found {found}"
    assert len({found[0] for found in pins.values()}) == 1, pins
