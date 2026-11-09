# SPDX-License-Identifier: Apache-2.0 OR MIT
"""A read document: its leaves, names and slugs (SPEC.md sections 6 to 8)."""

from __future__ import annotations

import bisect
import re
import unicodedata

from .blocks import CONTAINERS, LEAF_TYPES, Node, Refusal, parse_document, table_text, walk
from .inlines import find_links
from .slugclass import REMOVED

_STARTS = [a for a, _ in REMOVED]
NAME = re.compile(r"[a-z0-9][a-z0-9-]*")
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
    return kept.replace(" ", "-") or None


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
    def __init__(self, text: str, check_links: bool = True) -> None:
        """`check_links` is off only for a record (section 9, item 12)."""
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
        self._check_shadows()
        if check_links:
            self._check_links(nodes)

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

    def _check_shadows(self) -> None:
        """Section 9's `name-shadows-slug`: each heading holding the slug is read."""
        for name, bound in self.bound.items():
            if any(not any(h is b for b in bound) for h in self.slugs.get(name, [])):
                raise Refusal("name-shadows-slug")

    def _check_links(self, nodes: list[Node]) -> None:
        """Section 9's `dangling-link`."""
        for n in nodes:
            if n.type in ("paragraph", "heading"):
                self._check_text(n.content)
            elif n.type == "table":
                for row in n.rows:
                    for cell in row:
                        self._check_text(cell)

    def _check_text(self, text: str) -> None:
        for link in find_links(text):
            if link.title == '"transclude"' or not link.destination.startswith("#"):
                continue
            name = link.destination[1:]
            if NAME.fullmatch(name) and isinstance(self.resolve(name), str):
                raise Refusal("dangling-link")

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
