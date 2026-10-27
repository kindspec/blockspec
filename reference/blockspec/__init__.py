# SPDX-License-Identifier: Apache-2.0 OR MIT
"""blockspec's reference reader for draft 0. See `document.py`, and `edit.py`
for the editing API."""

from blockspec import edit
from blockspec.document import Document, Refusal, conform, parse, resolve

__all__ = ["Document", "Refusal", "conform", "edit", "parse", "resolve"]
