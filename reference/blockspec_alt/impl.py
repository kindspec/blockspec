# SPDX-License-Identifier: Apache-2.0 OR MIT
"""The entry points the conformance runner loads: `conform` and `resolve`."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from blockspec_alt.anchors import Repository  # noqa: E402
from blockspec_alt.blocks import Refusal  # noqa: E402
from blockspec_alt.document import Document  # noqa: E402


def conform(text: str, queries: list[str]) -> dict:
    try:
        return Document(text).report(queries)
    except Refusal as refusal:
        return {"accept": False, "refusal": refusal.code}


def resolve(repo: dict, queries: dict) -> dict:
    return Repository(repo).run(queries)
