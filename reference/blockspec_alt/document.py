# SPDX-License-Identifier: Apache-2.0 OR MIT
"""A read document: its leaves, names and slugs (SPEC.md sections 6 to 8)."""

from __future__ import annotations

import bisect
import unicodedata

from .blocks import CONTAINERS, LEAF_TYPES, Node, Refusal, parse_document, table_text, walk
from .slugclass import REMOVED

_STARTS = [a for a, _ in REMOVED]
NO_SLUG = set("*_`[<&")
TEXT_TYPES = ("paragraph", "heading", "code_block", "table")
SHORT = {"paragraph": "p", "code_block": "code", "table": "table"}


def is_removed(cp: int) -> bool:
    i = bisect.bisect_right(_STARTS, cp) - 1
    return i >= 0 and cp <= REMOVED[i][1]


def slug(raw: str) -> str | None:
    if NO_SLUG & set(raw):
        return None
    kept = "".join(c for c in raw.lower() if not is_removed(ord(c)))
    return kept.replace(" ", "-")


def ref(node: Node) -> dict:
    return {"node": list(node.path), "type": node.type}


class TextLeaf:
    """A text-bearing leaf as section 11.2 sees it."""

    __slots__ = ("node", "type", "text")

    def __init__(self, node: Node) -> None:
        self.node = node
        if node.type == "heading":
            self.type = f"h{node.level}"
        else:
            self.type = SHORT[node.type]
        if node.type == "table":
            self.text = table_text(node.rows)
        else:
            self.text = unicodedata.normalize("NFC", node.content)

    @property
    def key(self) -> tuple[str, str]:
        return self.type, self.text


class Document:
    def __init__(self, text: str) -> None:
        self.text = text.replace("\0", "�")
        self.root, self.frontmatter, self.spans, self.line_info = parse_document(self.text)
        self.names: dict[str, dict] = {}
        self.bound: dict[str, list[Node]] = {}
        self._bind_names()
        nodes = list(walk(self.root))
        self.text_leaves = [TextLeaf(n) for n in nodes if n.type in TEXT_TYPES]
        self.slugs: dict[str, list[Node]] = {}
        for n in nodes:
            if n.type == "heading":
                s = slug(n.content)
                if s is not None:
                    self.slugs.setdefault(s, []).append(n)

    def _bind_names(self) -> None:
        containers = [n for n in walk(self.root) if n.type in CONTAINERS]
        seen: set[str] = set()
        duplicate = False
        for c in containers:
            for child in c.children:
                if child.marker and child.marker[1] != "end":
                    duplicate = duplicate or child.marker[0] in seen
                    seen.add(child.marker[0])
        if duplicate:
            raise Refusal("duplicate-name")
        dangling = False
        for c in containers:
            kids = c.children
            ends: dict[str, list[int]] = {}
            for i, k in enumerate(kids):
                if k.marker and k.marker[1] == "end":
                    ends.setdefault(k.marker[0], []).append(i)
            for i, k in enumerate(kids):
                if not k.marker:
                    continue
                name, kind = k.marker
                if kind is None:
                    nxt = kids[i + 1] if i + 1 < len(kids) else None
                    if nxt is None or nxt.marker:
                        dangling = True
                    else:
                        self.names[name] = ref(nxt)
                        self.bound[name] = [nxt]
                elif kind == "begin":
                    closing = [j for j in ends.get(name, []) if j > i]
                    if not closing:
                        raise Refusal("unpaired-region")
                    j = closing[0]
                    ends[name].remove(j)
                    between = kids[i + 1 : j]
                    if not between:
                        dangling = True
                    self.names[name] = {"region": [ref(n) for n in between]}
                    self.bound[name] = between
            if any(ends.values()):
                raise Refusal("unpaired-region")
        if dangling:
            raise Refusal("dangling-marker")

    def resolve(self, name: str):
        if name in self.names:
            return self.names[name]
        hits = self.slugs.get(name, [])
        if len(hits) == 1:
            return ref(hits[0])
        return f"#REF!({name})"

    def report(self, queries: list[str]) -> dict:
        leaves = []
        for node in walk(self.root):
            if node.type in LEAF_TYPES:
                leaves.append({"node": list(node.path), "type": node.type, "content": node.content})
        fm = self.frontmatter
        return {
            "accept": True,
            "frontmatter": [fm[0] + 1, fm[1] + 1] if fm else None,
            "blocks": [{"type": n.type, "lines": [n.start, n.end]} for n in self.root.children],
            "leaves": leaves,
            "names": self.names,
            "resolve": {q: self.resolve(q) for q in queries},
        }
