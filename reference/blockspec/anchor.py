# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Resolve blockspec draft 0's anchors and transclusions: `SPEC.md` section 11.

Decided by `docs/adjudications/0003-anchors.md` and its addendum of
2026-10-16. Standard library only, like the reader it builds on
(`document.py`), which it is handed rather than imports, so that a mutated
copy of the reader is the one it runs.

Where SPEC.md does not decide an input, this module does not guess: it raises
`Undecided` with the question, and `resolve` reports that record or
transclusion as `UNDECIDED`, which no conformance case can expect. The
questions are listed where each is raised.
"""

from __future__ import annotations

import html
import json
import re
import unicodedata
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from types import SimpleNamespace

__all__ = ["Undecided", "resolve", "duplicate_record_ids"]


class Undecided(Exception):
    """SPEC.md does not decide what this input resolves to."""

    def __init__(self, question: str) -> None:
        super().__init__(question)
        self.question = question


class _Refused(Exception):
    """A resolution reason (SPEC.md section 11.10)."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


CONTEXT = 32  # code points of prefix and of suffix (section 11.1)
LEAF_TYPES = ("p", "h1", "h2", "h3", "h4", "h5", "h6", "code", "table")
STATUSES = ("open", "accepted", "rejected", "resolved")
TEXT_BEARING = ("paragraph", "heading", "code_block", "table")
HEX_DIGITS = {"sha1": 40, "sha256": 64}
_HEX = re.compile(r"[0-9a-f]+")
# A ULID: 26 characters of Crockford's base 32, the first at most 7.
_ULID = re.compile(r"[0-7][0-9A-HJKMNP-TV-Z]{25}")


# --- canonical JSON (section 11.1, 0003 addendum detail 1) ------------------

_ESCAPE = {0x22: '\\"', 0x5C: "\\\\", 0x0A: "\\n"}
_U_ESCAPED = frozenset(
    [*range(0x00, 0x20), *range(0x7F, 0xA0), 0x2028, 0x2029, 0xFEFF, 0xFFFE, 0xFFFF]
)


def canonical_string(value: str) -> str:
    """A string in the one form section 11.1 allows."""
    out = ['"']
    for ch in value:
        point = ord(ch)
        if point in _ESCAPE:
            out.append(_ESCAPE[point])
        elif point in _U_ESCAPED:
            out.append(f"\\u{point:04x}")
        else:
            out.append(ch)
    out.append('"')
    return "".join(out)


class _Object(list):
    """A JSON object, as its list of (key, value) pairs: told apart from a
    JSON array, which stays a plain list."""


def _pairs(text: str):
    """`text` read as JSON, every object as its list of (key, value) pairs,
    so that key order and a repeated key stay visible. None if it is not
    JSON."""
    try:
        return json.loads(text, object_pairs_hook=_Object)
    except (ValueError, RecursionError):
        return None


def _is_int(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _hex_id(value, object_format: str) -> bool:
    return (
        isinstance(value, str)
        and len(value) == HEX_DIGITS[object_format]
        and _HEX.fullmatch(value) is not None
    )


@dataclass(frozen=True)
class Anchor:
    base: str
    type: str
    nth: int
    text: str
    span: str
    prefix: str
    suffix: str
    replace: str | None


def write_anchor(anchor: Anchor) -> str:
    """The anchor's one canonical line value."""
    s = canonical_string
    out = (
        f'{{"base": {s(anchor.base)}, "leaf": {{"type": {s(anchor.type)}, '
        f'"nth": {anchor.nth}, "text": {s(anchor.text)}}}, "span": {s(anchor.span)}, '
        f'"prefix": {s(anchor.prefix)}, "suffix": {s(anchor.suffix)}'
    )
    if anchor.replace is not None:
        out += f', "replace": {s(anchor.replace)}'
    return out + "}"


def read_anchor(value: str, object_format: str) -> Anchor | None:
    """The anchor a line value holds, or None when it is not in the canonical
    form, or holds a value section 11.1 does not allow."""
    pairs = _pairs(value)
    if not isinstance(pairs, _Object):
        return None
    keys = [k for k, _ in pairs]
    if keys not in (
        ["base", "leaf", "span", "prefix", "suffix"],
        ["base", "leaf", "span", "prefix", "suffix", "replace"],
    ):
        return None
    got = dict(pairs)
    leaf = got["leaf"]
    if not isinstance(leaf, _Object) or [k for k, _ in leaf] != ["type", "nth", "text"]:
        return None
    leaf = dict(leaf)
    strings = [got["base"], leaf["type"], leaf["text"], got["span"], got["prefix"], got["suffix"]]
    if "replace" in got:
        strings.append(got["replace"])
    if not all(isinstance(v, str) for v in strings) or not _is_int(leaf["nth"]):
        return None
    if leaf["nth"] < 0 or leaf["type"] not in LEAF_TYPES or not _hex_id(got["base"], object_format):
        return None
    anchor = Anchor(
        got["base"],
        leaf["type"],
        leaf["nth"],
        leaf["text"],
        got["span"],
        got["prefix"],
        got["suffix"],
        got.get("replace"),
    )
    return anchor if write_anchor(anchor) == value else None


def read_string(value: str) -> str | None:
    """A canonical JSON string's text, or None."""
    got = _pairs(value)
    if not isinstance(got, str) or canonical_string(got) != value:
        return None
    return got


# --- records (section 11.1) --------------------------------------------------


@dataclass(frozen=True)
class Record:
    """A record whose frontmatter is in the grammar. `anchor` is None for a
    reply, and `reply_to` None for a comment or a suggestion."""

    kind: str
    status: str | None
    anchor: Anchor | None
    reply_to: str | None


def _frontmatter_lines(doc, lines: list[str]) -> list[str] | None:
    if doc.frontmatter is None:
        return None
    first, last = doc.frontmatter
    return lines[first : last - 1]


def read_record(lines: list[str] | None, object_format: str) -> Record | None:
    """The record a frontmatter's lines hold, or None when they break the
    grammar (section 11.1, 0003 addendum detail 1)."""
    if lines is None:
        return None
    if len(lines) == 3 and lines[0].startswith("anchor: "):
        anchor = read_anchor(lines[0][len("anchor: ") :], object_format)
        kind = {"kind: comment": "comment", "kind: suggestion": "suggestion"}.get(lines[1])
        status = lines[2][len("status: ") :] if lines[2].startswith("status: ") else None
        if anchor is None or kind is None or status not in STATUSES:
            return None
        if (anchor.replace is not None) != (kind == "suggestion"):
            return None
        return Record(kind, status, anchor, None)
    if len(lines) == 2 and lines[0].startswith("reply-to: ") and lines[1] == "kind: comment":
        parent = read_string(lines[0][len("reply-to: ") :])
        if parent is None or not _ULID.fullmatch(parent):
            return None
        return Record("comment", None, None, parent)
    return None


# --- snapshots and their leaves (section 11.2) ------------------------------


@dataclass
class Leaf:
    index: int  # among the snapshot's text-bearing leaves
    node: object  # the reader's node
    type: str  # the record's leaf.type: p, h1 to h6, code or table
    text: str  # section 11's text: the content, NFC, a table as one string

    @property
    def key(self) -> tuple[str, str]:
        return (self.type, self.text)

    @property
    def written_key(self) -> str:
        return f"{self.type}\x1f{self.text}"

    def ref(self) -> dict:
        return {"node": list(self.node.path), "type": self.node.type}


def table_text(rows: list[list[str]]) -> str:
    """A table as one string (section 11.2, 0003 addendum detail 3)."""
    text = "\n".join(" | ".join(cell.replace("|", "\\|") for cell in row) for row in rows)
    return unicodedata.normalize("NFC", text)


def _heading_level(raw_line: str) -> int:
    # Container prefixes are `>`, list markers and spaces, so the first `#`
    # opens the heading's run.
    at = raw_line.index("#")
    level = 0
    while at + level < len(raw_line) and raw_line[at + level] == "#":
        level += 1
    return level


class Snapshot:
    """One text of a document, read, with its text-bearing leaves."""

    def __init__(self, reader, text: str) -> None:
        self.text = text
        self.doc = reader.parse(text)
        self.lines = reader.split_lines(text)
        self.leaves: list[Leaf] = []
        for node in self.doc.nodes:
            if node.type not in TEXT_BEARING:
                continue
            if node.type == "paragraph":
                kind, text_ = "p", node.content()
            elif node.type == "heading":
                kind, text_ = f"h{_heading_level(self.lines[node.start - 1])}", node.content()
            elif node.type == "code_block":
                kind, text_ = "code", node.content()
            else:
                kind, text_ = "table", None
            if kind == "table":
                text_ = table_text(node.content())
            else:
                text_ = unicodedata.normalize("NFC", text_)
            self.leaves.append(Leaf(len(self.leaves), node, kind, text_))


def _read(reader, text: str) -> Snapshot:
    """`text` as a snapshot, or `not-in-profile`."""
    try:
        return Snapshot(reader, text)
    except reader.Refusal as refusal:
        raise _Refused("not-in-profile") from refusal


# --- similarity and alignment (section 11.2, 0003 addendum detail 5) -------


def lcs_length(a: str, b: str) -> int:
    if len(a) < len(b):
        a, b = b, a
    previous = [0] * (len(b) + 1)
    for x in a:
        current = [0]
        for j, y in enumerate(b):
            current.append(previous[j] + 1 if x == y else max(previous[j + 1], current[j]))
        previous = current
    return previous[-1]


def lcs_alignment(a, b) -> dict[int, int]:
    """Section 11.2's longest common subsequence alignment: position in `a`
    to the position in `b` it is paired with."""
    m, n = len(a), len(b)
    suffix = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m - 1, -1, -1):
        row, below = suffix[i], suffix[i + 1]
        for j in range(n - 1, -1, -1):
            row[j] = below[j + 1] + 1 if a[i] == b[j] else max(below[j], row[j + 1])
    paired = {}
    i = j = 0
    while i < m and j < n:
        if a[i] == b[j]:
            paired[i] = j
            i += 1
            j += 1
        elif suffix[i + 1][j] == suffix[i][j]:
            i += 1
        else:
            j += 1
    return paired


def similarity(a: Leaf, b: Leaf) -> tuple[int, int]:
    """`(L, T)`: the similarity is `2·L/T`, kept as integers."""
    return lcs_length(a.written_key, b.written_key), len(a.written_key) + len(b.written_key)


_SPACE = re.compile(r"[\t\n\r ]+")


def words(leaf: Leaf) -> list[str]:
    """A leaf's words (0004): its type, then its text split at runs of tab,
    LF, CR and space."""
    return [leaf.type, *(w for w in _SPACE.split(leaf.text) if w)]


def word_similarity(a: Leaf, b: Leaf) -> tuple[int, int]:
    """`(L, T)` over words: the word similarity is `2·L/T` (0004)."""
    wa, wb = words(a), words(b)
    return lcs_length(wa, wb), len(wa) + len(wb)


def at_least_three_tenths(sim: tuple[int, int]) -> bool:
    return 20 * sim[0] >= 3 * sim[1]


def at_least_half(sim: tuple[int, int]) -> bool:
    return 4 * sim[0] >= sim[1]


def below_one(sim: tuple[int, int]) -> bool:
    return 2 * sim[0] < sim[1]


def exceeds_by_margin(one: tuple[int, int], other: tuple[int, int]) -> bool:
    """Whether `one` exceeds `other` by at least 0.15."""
    (l1, t1), (l2, t2) = one, other
    return 40 * l1 * t2 - 40 * l2 * t1 >= 3 * t1 * t2


# --- correspondence (section 11.3) ------------------------------------------

EXACT, MOVED, EDITED = "EXACT", "MOVED", "EDITED"


def leftmost_chain(pairs: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Of the longest subsequences of `pairs` (in base order) whose current
    positions increase, the one whose current positions are lexicographically
    smallest (0003 addendum detail 4)."""
    n = len(pairs)
    longest = [1] * n  # the longest increasing run that starts at each pair
    for k in range(n - 1, -1, -1):
        for later in range(k + 1, n):
            if pairs[later][1] > pairs[k][1]:
                longest[k] = max(longest[k], longest[later] + 1)
    chain: list[tuple[int, int]] = []
    start, last = 0, -1
    for need in range(max(longest, default=0), 0, -1):
        options = [k for k in range(start, n) if longest[k] == need and pairs[k][1] > last]
        k = min(options, key=lambda k: pairs[k][1])
        chain.append(pairs[k])
        start, last = k + 1, pairs[k][1]
    return chain


class Correspondence:
    """Section 11.3 between a base snapshot's leaves and a current one's."""

    def __init__(self, base: list[Leaf], current: list[Leaf]) -> None:
        self.base, self.current = base, current
        self._similarity: dict[tuple[int, int], tuple[int, int]] = {}
        self._words: dict[tuple[int, int], tuple[int, int]] = {}
        base_count = _counts(base)
        current_count = _counts(current)
        unique = {leaf.key: leaf.index for leaf in current if current_count[leaf.key] == 1}
        pairs = [
            (leaf.index, unique[leaf.key])
            for leaf in base
            if base_count[leaf.key] == 1 and leaf.key in unique
        ]
        self.chain = leftmost_chain(pairs)
        self.pair: dict[int, tuple[int, str]] = {b: (c, EXACT) for b, c in self.chain}
        on_chain = set(self.chain)
        for b, c in pairs:
            if (b, c) not in on_chain:
                self.pair[b] = (c, MOVED)
        moved_current = {c for c, kind in self.pair.values() if kind == MOVED}
        bounds = [(-1, -1), *self.chain, (len(base), len(current))]
        for (b0, c0), (b1, c1) in zip(bounds, bounds[1:], strict=False):
            gap_base = [b for b in range(b0 + 1, b1) if b not in self.pair]
            gap_current = [c for c in range(c0 + 1, c1) if c not in moved_current]
            keys_b = [base[b].key for b in gap_base]
            keys_c = [current[c].key for c in gap_current]
            for i, j in lcs_alignment(keys_b, keys_c).items():
                self.pair[gap_base[i]] = (gap_current[j], EXACT)
            paired_current = {c for c, _ in self.pair.values()}
            left_base = [b for b in gap_base if b not in self.pair]
            left_current = [c for c in gap_current if c not in paired_current]
            for b in left_base:
                for c in left_current:
                    if self._edited(b, c, left_base, left_current):
                        self.pair[b] = (c, EDITED)
        self.matched = {c for c, _ in self.pair.values()}

    def similarity(self, b: int, c: int) -> tuple[int, int]:
        if (b, c) not in self._similarity:
            self._similarity[(b, c)] = similarity(self.base[b], self.current[c])
        return self._similarity[(b, c)]

    def word_similarity(self, b: int, c: int) -> tuple[int, int]:
        if (b, c) not in self._words:
            self._words[(b, c)] = word_similarity(self.base[b], self.current[c])
        return self._words[(b, c)]

    def _edited(self, b: int, c: int, left_base: list[int], left_current: list[int]) -> bool:
        sim = self.similarity(b, c)
        if not at_least_half(sim):
            return False
        if not all(exceeds_by_margin(sim, self.similarity(b, o)) for o in left_current if o != c):
            return False
        return all(exceeds_by_margin(sim, self.similarity(o, c)) for o in left_base if o != b)

    def unmatched(self) -> list[int]:
        return [c for c in range(len(self.current)) if c not in self.matched]

    def gap(self, k: int) -> tuple[range, range]:
        """`k`'s gap (section 11.4): the base and current positions strictly
        between the nearest chain pairs before and after it, in base order."""
        before = max(((b, c) for b, c in self.chain if b < k), default=(-1, -1))
        after = min(((b, c) for b, c in self.chain if b > k), default=None)
        if after is None:
            after = (len(self.base), len(self.current))
        return range(before[0] + 1, after[0]), range(before[1] + 1, after[1])


def _counts(leaves: list[Leaf]) -> dict[tuple[str, str], int]:
    counts: dict[tuple[str, str], int] = {}
    for leaf in leaves:
        counts[leaf.key] = counts.get(leaf.key, 0) + 1
    return counts


def check_pair(corr: Correspondence, k: int) -> tuple[int, str]:
    """Section 11.4 for base leaf `k`: its pair, or `_Refused`, or None as the
    pair when the leaf is ORPHANED."""
    leaf = corr.base[k]
    copies = [c.index for c in corr.current if c.key == leaf.key]
    if k not in corr.pair:
        if copies:
            raise _Refused("unaccounted-copy")
        return None, "ORPHANED"
    c, kind = corr.pair[k]
    unmatched = corr.unmatched()
    gap_base, gap_current = corr.gap(k)

    def near(also_exact: bool) -> bool:
        for u in unmatched:
            sim = corr.word_similarity(k, u)
            if at_least_half(sim) and (also_exact or below_one(sim)):
                return True
        return False

    if kind == EXACT:
        base_copies = [b.index for b in corr.base if b.key == leaf.key]
        if len(base_copies) > 1 or len(copies) > 1:
            in_base = sum(1 for b in base_copies if b in gap_base)
            in_current = sum(1 for d in copies if d in gap_current)
            if in_base != in_current:
                raise _Refused("repeat")
        if near(also_exact=False):
            raise _Refused("near-copy")
    elif kind == MOVED:
        if near(also_exact=True):
            raise _Refused("near-copy")
        if any(u in gap_current for u in unmatched):
            raise _Refused("refilled-gap")
    else:
        if any(u in copies for u in unmatched):
            raise _Refused("exact-copy")
        if any(
            u in gap_current and at_least_three_tenths(corr.word_similarity(k, u))
            for u in unmatched
        ):
            raise _Refused("crowded-gap")
        if near(True):
            raise _Refused("near-copy")
    return c, kind


# --- the span (section 11.5) ------------------------------------------------


def occurrences(text: str, part: str) -> list[int]:
    """Every start of `part` in `text`, overlapping ones included."""
    found, at = [], text.find(part)
    while at != -1:
        found.append(at)
        at = text.find(part, at + 1)
    return found


def span_in_base(anchor: Anchor) -> int:
    """Where the span starts in `leaf.text`, or `record-inconsistent` when the
    record's context breaks section 11.1's consistency rules."""
    text = anchor.text
    if not anchor.span:
        raise _Refused("record-inconsistent")
    found = occurrences(text, anchor.prefix + anchor.span + anchor.suffix)
    if len(found) != 1:
        raise _Refused("record-inconsistent")
    at = found[0]
    end = at + len(anchor.prefix) + len(anchor.span) + len(anchor.suffix)
    if len(anchor.prefix) < CONTEXT and at > 0:
        raise _Refused("record-inconsistent")
    if len(anchor.suffix) < CONTEXT and end < len(text):
        raise _Refused("record-inconsistent")
    if len(anchor.prefix) > CONTEXT or len(anchor.suffix) > CONTEXT:
        raise _Refused("record-inconsistent")  # second addendum, item 1
    return at + len(anchor.prefix)


def _spaced(text: str) -> str:
    """`text` with each run of tab, LF, CR and space as one space (0004)."""
    return _SPACE.sub(" ", text)


def _word_code_point(c: str) -> bool:
    return unicodedata.category(c)[0] in "LN"


def _edge(text: str, at: int) -> bool:
    """Whether `at` is a word boundary in `text` (0004): an end of the text,
    or a position not between two letters or numbers."""
    return (
        at <= 0
        or at >= len(text)
        or not (_word_code_point(text[at - 1]) and _word_code_point(text[at]))
    )


def find_span(anchor: Anchor, start: int, base: Leaf, current: Leaf) -> tuple[str, list | None]:
    """Section 11.5 for an EDITED pair: `EDITED` with the span, `DETACHED`,
    or `_Refused("span-ambiguous")`."""
    text = current.text
    span, prefix, suffix = anchor.span, anchor.prefix, anchor.suffix
    begins, ends = _edge(base.text, start), _edge(base.text, start + len(span))
    hits = []
    for at in occurrences(text, span):
        if _edge(text, at) != begins or _edge(text, at + len(span)) != ends:
            continue
        before, after = _spaced(text[:at]), _spaced(text[at + len(span) :])
        if len(prefix) < CONTEXT:
            prefix_holds = before == _spaced(prefix)
        else:
            prefix_holds = before.endswith(_spaced(prefix))
        if len(suffix) < CONTEXT:
            suffix_holds = after == _spaced(suffix)
        else:
            suffix_holds = after.startswith(_spaced(suffix))
        if prefix_holds or suffix_holds:
            hits.append(at)
    if not hits:
        return "DETACHED", None
    if len(hits) > 1:
        raise _Refused("span-ambiguous")
    hit = hits[0]
    paired = lcs_alignment(base.text, text)
    if any(paired.get(start + d) != hit + d for d in range(len(span))):
        return "DETACHED", None
    return "EDITED", [hit, hit + len(span)]


# --- write-back (section 11.7) ----------------------------------------------


class _Unmappable(Exception):
    pass


def _raw_lines(text: str) -> list[tuple[int, int, int]]:
    """Each line as (start, end of its text, end of its line ending), as the
    reader splits lines: a final empty line is no line."""
    out = []
    for match in re.finditer(r"[^\r\n]*(\r\n|\r|\n|$)", text):
        if match.start() == len(text) and (not out or out[-1][2] == len(text)):
            break
        end = match.end(0) - len(match.group(1))
        out.append((match.start(), end, match.end(0)))
    return out


def _content_positions(snapshot: Snapshot, leaf: Leaf) -> tuple[str, list]:
    """The leaf's content as the reader gives it, before NFC, and for each of
    its code points the raw (start, end) it comes from, or None for a code
    point no single raw character gives."""
    node = leaf.node
    lines = _raw_lines(snapshot.text)
    content = node.content()
    positions: list = []
    if node.type == "heading":
        start, end, _ = lines[node.start - 1]
        raw = snapshot.text[start:end]
        at = raw.index("#")
        while at < len(raw) and raw[at] == "#":
            at += 1
        while at < len(raw) and raw[at] in " \t":
            at += 1
        if raw[at : at + len(content)] != content:
            raise _Unmappable()
        return content, [(start + at + k, start + at + k + 1) for k in range(len(content))]
    for number, text in node.lines:
        start, end, after = lines[number - 1]
        raw = snapshot.text[start:end]
        synthetic = None
        for k in range(4):
            tail = text[k:]
            if text[:k] != " " * k or not raw.endswith(tail):
                continue
            if k and raw[len(raw) - len(tail) - 1] != "\t":
                continue
            synthetic = k
            break
        if synthetic is None:
            raise _Unmappable()
        offset = start + len(raw) - (len(text) - synthetic)
        positions += [None] * synthetic
        positions += [(offset + k, offset + k + 1) for k in range(len(text) - synthetic)]
        positions.append((end, after) if after > end else None)
    if node.type == "paragraph":
        # Lines are joined, not ended, by \n, and final spaces are dropped.
        positions = positions[: len(content)]
    if len(positions) != len(content):
        raise _Unmappable()
    return content, positions


def _map_span(content: str, text: str, start: int, end: int) -> tuple[int, int]:
    """Section 11.7 step 1: positions `a` and `b` in the content before NFC."""
    nfc = unicodedata.normalize
    for a in range(len(content) + 1):
        if nfc("NFC", content[:a]) != text[:start]:
            continue
        for b in range(a, len(content) + 1):
            if nfc("NFC", content[a:b]) == text[start:end]:
                return a, b
        break
    raise _Unmappable()


def _container_prefix(leaf: Leaf, raw_line: str, number: int) -> str:
    """The container prefixes the parse gives line `number`, or
    `_Unmappable` where a new line cannot repeat them (section 11.7, *A line
    break that cannot be written back*)."""
    chain = []
    node = leaf.node.parent
    while node is not None and node.type != "document":
        chain.append(node)
        node = node.parent
    at = 0
    for node in reversed(chain):
        if node.type == "block_quote":
            j = at
            while j < at + 3 and j < len(raw_line) and raw_line[j] == " ":
                j += 1
            if j >= len(raw_line) or raw_line[j] != ">":
                raise _Unmappable()  # a lazy line, which has no prefix to repeat
            j += 1
            if j < len(raw_line) and raw_line[j] == "\t":
                raise _Unmappable()  # a tab in the container prefix
            if j < len(raw_line) and raw_line[j] == " ":
                j += 1
            at = j
        elif node.type == "list_item":
            if node.start == number:
                raise _Unmappable()  # the item's first line: its prefix is the marker
            width = node.list_data["offset"] + node.list_data["padding"]
            part = raw_line[at : at + width]
            if "\t" in part:
                raise _Unmappable()  # a tab in the container prefix
            if part != " " * width:
                raise _Unmappable()  # a lazy line, which has no prefix to repeat
            at += width
    return raw_line[:at]


def write_back(snapshot: Snapshot, leaf: Leaf, span: list[int], replace: str) -> str:
    """The document's text with `replace` written over the span (section
    11.7 steps 1 to 3), or `_Unmappable`."""
    if leaf.type == "table":
        raise Undecided(
            "writing a suggestion back into a table, whose text holds separators, "
            "escapes and padding that no raw character gives"
        )
    content, positions = _content_positions(snapshot, leaf)
    a, b = _map_span(content, leaf.text, *span)
    if leaf.node.type == "code_block" and b == len(content):
        raise _Unmappable()  # the block's final line ending (third addendum, item 4)
    if any(p is None for p in positions[a:b]) or a == b:
        raise _Unmappable()
    if b < len(positions) and positions[b] is None:
        raise _Unmappable()
    first = positions[a][0]
    last = positions[b][0] if b < len(positions) else positions[b - 1][1]
    if "\n" in replace:
        lines = _raw_lines(snapshot.text)
        line_of = {}
        for number, (start, _end, after) in enumerate(lines, 1):
            for p in range(start, after):
                line_of[p] = number
        breaks = {line_of[first], line_of[positions[b - 1][0]]}
        endings, prefixes = set(), set()
        for number in breaks:
            start, end, after = lines[number - 1]
            endings.add(snapshot.text[end:after])
            prefixes.add(_container_prefix(leaf, snapshot.text[start:end], number))
        if len(endings) > 1 or len(prefixes) > 1:
            raise Undecided(
                "a line break written over a span whose lines end or are prefixed "
                "differently: which line it breaks"
            )
        ending, prefix = endings.pop(), prefixes.pop()
        if not ending:
            raise _Unmappable()  # the file's last line, with no line ending to copy
        replace = replace.replace("\n", ending + prefix)
    return snapshot.text[:first] + replace + snapshot.text[last:]


# --- records: resolution (sections 11.4 to 11.8) -----------------------------

PAIRED_STATUS = {EXACT: "RESOLVED", MOVED: "MOVED"}


def _raw_frontmatter(lines: list[str]) -> list[str] | None:
    """The lines between a frontmatter's `---` lines, found by section 5's
    rule on the raw lines, so that a record whose body the profile refuses
    still shows whether it is a suggestion."""
    if len(lines) > 1 and lines[0] == "---" and lines[1].strip(" \t"):
        for at in range(1, len(lines)):
            if lines[at].rstrip(" \t") == "---":
                return lines[1:at]
    return None


def _record_location(path: str) -> str:
    """The document a record path belongs to, or `record-inconsistent` for an
    entry of a notes directory that is not a record (section 11.1)."""
    parts = path.split("/")
    notes = [i for i, part in enumerate(parts[:-1]) if part.endswith(".notes")]
    if not notes:
        raise Undecided("a path that is in no notes directory")
    if notes[-1] != len(parts) - 2:
        raise _Refused("record-inconsistent")  # in a subfolder of a notes directory
    name = parts[-1]
    if not name.endswith(".md") or not _ULID.fullmatch(name[: -len(".md")]):
        raise _Refused("record-inconsistent")
    return "/".join(parts[:-1])[: -len(".notes")]


def resolve_record(reader, repo: Mapping, path: str) -> dict:
    """One record's outcome. Input problems are reported in section 11.10's
    order, *Which reason is reported*: the first that applies decides."""
    tree = repo["tree"]
    outcome = {"status": None, "leaf": None, "span": None, "suggestion": None}
    if path not in tree:
        raise Undecided("a record that is not in the tree")
    fm = _raw_frontmatter(reader.split_lines(tree[path]))
    if fm is not None and "kind: suggestion" in fm:
        outcome["suggestion"] = {"gate": "stale", "reason": None}
    try:
        document = _record_location(path)
        record = _read_record(reader, tree[path], fm, repo["object_format"])
        if record.anchor is None:
            # A reply is a record: steps 2 and 3 of the order apply to it,
            # and steps 4 to 6 read an anchor (third addendum, item 2).
            if document not in tree:
                raise _Refused("document-missing")
            _read(reader, tree[document])
            directory = path.rpartition("/")[0]
            found = f"{directory}/{record.reply_to}.md" in tree
            outcome["status"] = "REPLY" if found else "#REF!(reply-to)"
            return outcome
        anchor = record.anchor
        start = span_in_base(anchor)  # step 1: the checks that read only the record
        current, base, k = _record_inputs(reader, repo, document, anchor)
    except _Refused as refused:
        outcome["status"] = f"REFUSED({refused.reason})"
        return outcome
    corr = Correspondence(base.leaves, current.leaves)
    try:
        c, kind = check_pair(corr, k)
        if c is None:
            outcome["status"] = "ORPHANED"
            return outcome
        paired = current.leaves[c]
        if kind == EDITED:
            status, span = find_span(anchor, start, base.leaves[k], paired)
        else:
            status, span = PAIRED_STATUS[kind], [start, start + len(anchor.span)]
    except _Refused as refused:
        outcome["status"] = f"REFUSED({refused.reason})"
        return outcome
    outcome.update(status=status, leaf=paired.ref(), span=span)
    if record.kind == "suggestion":
        outcome["suggestion"] = _gate(record, status, current, paired, span)
    return outcome


def _read_record(reader, text: str, fm: list[str] | None, object_format: str) -> Record:
    """The record, or `record-inconsistent` for its grammar or for a body the
    profile refuses (section 11.1)."""
    try:
        reader.parse(text)
    except reader.Refusal as refusal:
        raise _Refused("record-inconsistent") from refusal
    record = read_record(fm, object_format)
    if record is None:
        raise _Refused("record-inconsistent")
    return record


def _record_inputs(reader, repo: Mapping, document: str, anchor: Anchor):
    """Steps 2 to 6 of section 11.10's order: the current snapshot, the base
    snapshot and the anchored leaf, or the first reason that applies."""
    if document not in repo["tree"]:
        raise _Refused("document-missing")
    current = _read(reader, repo["tree"][document])
    if anchor.base not in repo["blobs"]:
        raise _Refused("base-unavailable")
    base = _read(reader, repo["blobs"][anchor.base])
    k = _anchored_leaf(base, anchor)
    if k is None:
        raise _Refused("record-inconsistent")
    return current, base, k


def _anchored_leaf(base: Snapshot, anchor: Anchor) -> int | None:
    same = [leaf.index for leaf in base.leaves if leaf.key == (anchor.type, anchor.text)]
    return same[anchor.nth] if anchor.nth < len(same) else None


def _gate(record: Record, status: str, current: Snapshot, leaf: Leaf, span) -> dict:
    """Section 11.7's gate for a suggestion that resolved to a leaf."""
    if record.status != "open" or status not in ("RESOLVED", "EDITED"):
        return {"gate": "stale", "reason": None}
    try:
        written = write_back(current, leaf, span, record.anchor.replace)
    except _Unmappable:
        return {"gate": "stale", "reason": "unmappable-offset"}
    return {"gate": "apply", "written": written}


def duplicate_record_ids(tree: Mapping[str, str]) -> dict[str, list[str]]:
    """Record ids found in more than one notes directory, each with its
    directories: section 11.8's warning, which is not a refusal."""
    seen: dict[str, list[str]] = {}
    for path in sorted(tree):
        directory, _, name = path.rpartition("/")
        if directory.endswith(".notes") and name.endswith(".md"):
            seen.setdefault(name[: -len(".md")], []).append(directory)
    return {rid: dirs for rid, dirs in seen.items() if len(dirs) > 1}


# --- transclusion (section 11.9) --------------------------------------------

_TITLE = re.compile(
    r"""[ \t\n]("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|\((?:[^()\\]|\\.)*\))[ \t\n]*\)"""
)


@dataclass(frozen=True)
class Transclusion:
    leaf: Leaf
    path: str  # the destination's part before the `#`, as raw text
    name: str


class _NotALink(Exception):
    """CommonMark reads the paragraph's opening bracket as no link."""


_QUOTED_TITLE = re.compile(r""""(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|\((?:[^()\\]|\\.)*\)""")


def _skip_space(content: str, at: int) -> int:
    """Past spaces and tabs, with at most one line ending among them."""
    newline = False
    while at < len(content) and content[at] in " \t\n":
        if content[at] == "\n":
            if newline:
                break
            newline = True
        at += 1
    return at


def _inline_link_tail(content: str, at: int) -> int | None:
    """Where an inline link's `(destination "title")` that starts at `at`,
    just after `(`, ends, or None when it is no link tail (CommonMark
    0.31.2, *Links*)."""
    at = _skip_space(content, at)
    if content[at : at + 1] == "<":
        end = at + 1
        while end < len(content) and content[end] not in "<>\n":
            end += 2 if content[end] == "\\" else 1
        if end >= len(content) or content[end] != ">":
            return None
        at = end + 1
    else:
        at = _destination_end(content, at)
    gap = _skip_space(content, at)
    if content[gap : gap + 1] == ")":
        return gap + 1
    title = _QUOTED_TITLE.match(content, gap) if gap > at else None
    if title is None:
        return None
    end = _skip_space(content, title.end())
    return end + 1 if content[end : end + 1] == ")" else None


def _link_text_end(content: str) -> int | None:
    """Where a link's text ends, after `[`, or None. Brackets nest and a
    backslash escapes; text a code span or raw HTML could reshape is left
    undecided. A link inside the text means the outer brackets are no link
    (CommonMark 0.31.2, example 518): `_NotALink`."""
    depth = 0
    at = 1
    while at < len(content):
        ch = content[at]
        if ch == "\\":
            at += 2
            continue
        if ch in "`<":
            raise Undecided("a transclusion link whose text holds a code span or HTML")
        if ch == "[" and content[at - 1] != "!":
            inner = _link_text_end(content[at:])
            if inner is not None and content[at + inner + 1 : at + inner + 2] == "(":
                if _inline_link_tail(content, at + inner + 2) is not None:
                    raise _NotALink()
        if ch == "[":
            depth += 1
        elif ch == "]":
            if depth == 0:
                return at
            depth -= 1
        at += 1
    return None


def _destination_end(content: str, at: int) -> int:
    """Where a destination that is not in angle brackets ends, from `at`."""
    depth = 0
    while at < len(content):
        ch = content[at]
        if ch == "\\" and at + 1 < len(content):
            at += 2
            continue
        if ch == "(":
            depth += 1
        elif ch == ")":
            if depth == 0:
                break
            depth -= 1
        elif ord(ch) <= 0x20 or ch == "\x7f":
            break
        at += 1
    return at


_ENTITY = re.compile(r"&(?:#[0-9]{1,7}|#[xX][0-9a-fA-F]{1,6}|[A-Za-z][A-Za-z0-9]{1,31});")


def _reads_transclude(title: str) -> bool:
    """Whether a link title, with its delimiters, reads as `transclude` once
    its backslash escapes and entity references are decoded. CommonMark
    decodes an entity only with its closing `;`."""
    inner = re.sub(r"\\([!-/:-@\[-`{-~])", r"\1", title[1:-1])
    return _ENTITY.sub(lambda m: html.unescape(m.group()), inner) == "transclude"


def _link_destination(content: str) -> str | None:
    """The destination of a paragraph that is exactly one inline link titled
    `"transclude"`, or None when it is not that shape."""
    if not content.startswith("["):
        return None
    close = _link_text_end(content)
    if close is None or content[close : close + 2] != "](":
        return None
    at = close + 2
    if content[at : at + 1] == "<":
        raise Undecided("a transclusion destination in angle brackets")
    end = _destination_end(content, at)
    title = re.fullmatch(
        r'(?:[ \t]+(?:\n[ \t]*)?|\n[ \t]*)"transclude"[ \t]*(?:\n[ \t]*)?\)', content[end:]
    )
    if end == at or title is None:
        return None
    return content[at:end]


def classify(leaf: Leaf) -> Transclusion | None:
    """Whether a paragraph is a transclusion (section 11.9): None, or the
    transclusion, or `Undecided` for a shape section 12 leaves open."""
    content = leaf.node.content()
    if "](" not in content:
        return None  # no inline link at all
    titles = [m.group(1) for m in _TITLE.finditer(content) if _reads_transclude(m.group(1))]
    if not titles:
        return None
    if any(t != '"transclude"' for t in titles):
        raise Undecided(
            "a link title that reads as `transclude` but is written another way: "
            "another quoting form, a backslash escape or an entity reference"
        )
    try:
        if content.startswith("![") and _link_destination(content[1:]) is not None:
            return None  # an image, which is no link
        destination = _link_destination(content)
    except _NotALink:
        return None
    if destination is None:
        raise Undecided("a `transclude` link in a paragraph that holds other text")
    if len(leaf.node.path) > 1:
        raise Undecided("a transclusion paragraph inside a list item or a block quote")
    path, hash_, name = destination.partition("#")
    if not hash_:
        raise Undecided("a transclusion destination with no `#name`")
    if not path:
        raise Undecided("a transclusion destination with no path")
    return Transclusion(leaf, path, name)


def resolve_path(referrer: str, path: str) -> str:
    """The repository path a transclusion's path names (0003 addendum
    detail 7), or `unresolvable-path`."""
    segments = path.split("/")
    if path.startswith("/") or ":" in segments[0]:
        raise _Refused("unresolvable-path")
    if "" in segments:
        raise Undecided("an empty segment in a transclusion path")
    out = referrer.split("/")[:-1]
    for segment in segments:
        if segment == ".":
            continue
        if segment == "..":
            if not out:
                raise _Refused("unresolvable-path")
            out.pop()
        else:
            out.append(segment)
    return "/".join(out)


def read_pins(lines: list[str] | None, object_format: str) -> dict[str, str] | None:
    """A referrer's pins by path (0003 addendum detail 2): `{}` when it has
    none, None when they break the grammar."""
    lines = lines or []
    heads = [i for i, line in enumerate(lines) if line.startswith("pins:")]
    if not heads:
        return {}
    if len(heads) > 1 or lines[heads[0]] != "pins:":
        return None
    pins: dict[str, str] = {}
    at = heads[0] + 1
    while at < len(lines) and lines[at].startswith("  - "):
        value = lines[at][len("  - ") :]
        pairs = _pairs(value)
        if not isinstance(pairs, _Object) or [k for k, _ in pairs] != ["path", "blob"]:
            return None
        got = dict(pairs)
        if not isinstance(got["path"], str) or not _hex_id(got["blob"], object_format):
            return None
        written = (
            f'{{"path": {canonical_string(got["path"])}, "blob": {canonical_string(got["blob"])}}}'
        )
        if written != value:
            return None
        if pins and got["path"] <= list(pins)[-1]:
            return None  # out of order, or a path twice
        pins[got["path"]] = got["blob"]
        at += 1
    for later in range(at, len(lines)):
        if lines[later].startswith("  - ") and all(
            not line.strip(" \t") or line.startswith((" ", "#")) for line in lines[at:later]
        ):
            return None
    return pins


def _bound_leaves(snapshot: Snapshot, binding: Mapping) -> list[Leaf]:
    roots = binding["region"] if "region" in binding else [binding]
    paths = [tuple(r["node"]) for r in roots]
    return [
        leaf for leaf in snapshot.leaves if any(tuple(leaf.node.path[: len(p)]) == p for p in paths)
    ]


def _reaches(reader, tree: Mapping, start: str, goal: str, seen: set[str]) -> bool:
    """Whether `start`'s transclusions lead back to `goal`, in the current
    tree. A paragraph whose shape is itself undecided is not followed, and
    the rest of its document still is."""
    if start in seen or start not in tree:
        return False
    seen.add(start)
    try:
        snapshot = Snapshot(reader, tree[start])
    except reader.Refusal:
        return False
    for leaf in snapshot.leaves:
        if leaf.node.type != "paragraph":
            continue
        try:
            one = classify(leaf)
            if one is None:
                continue
            target = resolve_path(start, one.path)
        except (_Refused, Undecided):
            continue
        if target == goal or _reaches(reader, tree, target, goal, seen):
            return True
    return False


def resolve_transclusions(reader, repo: Mapping, referrer: str) -> list[dict] | str:
    """Each transclusion of a referrer, in document order, or the one
    referrer-level status of a referrer the profile refuses (section 11.9,
    step 0)."""
    tree = repo["tree"]
    if referrer not in tree:
        raise Undecided("a referrer that is not in the tree")
    try:
        snapshot = Snapshot(reader, tree[referrer])
    except reader.Refusal:
        return "REFUSED(not-in-profile)"
    pins = read_pins(_frontmatter_lines(snapshot.doc, snapshot.lines), repo["object_format"])
    out = []
    for leaf in snapshot.leaves:
        if leaf.node.type != "paragraph":
            continue
        try:
            one = classify(leaf)
            if one is None:
                continue
            outcome = _resolve_one(reader, repo, referrer, one, pins)
        except Undecided as undecided:
            outcome = {"status": "UNDECIDED", "question": undecided.question, "unit": None}
        except _Refused as refused:
            outcome = {"status": f"REFUSED({refused.reason})", "unit": None}
        out.append({"leaf": leaf.ref(), **outcome})
    return out


def _slug_only(reader, current: Snapshot, name: str) -> bool:
    """Whether only a heading slug matches `name` in the current target."""
    if name in current.doc.names:
        return False
    return any(
        node.type == "heading" and reader.slug(node.text) == name for node in current.doc.nodes
    )


def _resolve_one(reader, repo: Mapping, referrer: str, one: Transclusion, pins) -> dict:
    """Section 11.9, steps 1 to 4, for one transclusion of an accepted
    referrer. The first step that fails decides."""
    tree, blobs = repo["tree"], repo["blobs"]
    target = resolve_path(referrer, one.path)  # 1.1
    if not target.endswith(".md"):
        raise Undecided("a transclusion path that names a file that is not markdown")
    if target == referrer or _reaches(reader, tree, target, referrer, set()):
        raise Undecided("a document that transcludes itself, directly or through another")
    if pins is None:  # 1.2
        raise _Refused("record-inconsistent")
    if target not in tree:  # 1.3
        raise _Refused("document-missing")
    current = _read(reader, tree[target])  # 1.4
    if _slug_only(reader, current, one.name):  # 1.5
        return {"status": f"#REF!({one.name})", "unit": None}
    if one.path not in pins:
        raise Undecided("a transclusion with no pin")
    if pins[one.path] not in blobs:  # 1.6
        raise _Refused("base-unavailable")
    pinned = _read(reader, blobs[pins[one.path]])  # 1.7
    if one.name not in pinned.doc.names:  # 1.8
        raise _Refused("record-inconsistent")
    binding = current.doc.names.get(one.name)  # 2
    if binding is None:
        return {"status": f"#REF!({one.name})", "unit": None}
    corr = Correspondence(pinned.leaves, current.leaves)  # 3
    pairs = []
    for leaf in _bound_leaves(pinned, pinned.doc.names[one.name]):
        try:
            c, _kind = check_pair(corr, leaf.index)
        except _Refused as refused:
            raise _Refused(f"pinned-{refused.reason}") from refused
        if c is None:
            raise _Refused("pinned-orphaned")
        pairs.append(c)
    inside = {leaf.index for leaf in _bound_leaves(current, binding)}  # 4
    if any(c not in inside for c in pairs):
        raise _Refused("name-rebound")
    return {"status": "RESOLVED", "unit": {"document": target, "target": binding}}


# --- the entry point --------------------------------------------------------


def _default_reader():
    from blockspec import document

    return SimpleNamespace(
        parse=document.parse,
        Refusal=document.Refusal,
        split_lines=document._split_lines,
        slug=document._slug,
    )


def resolve(repo: Mapping, queries: Mapping, reader=None) -> dict:
    """The `anchor` kind's interface (`conformance/run_cases.py`): each queried
    record's outcome, and each queried referrer's transclusions."""
    reader = reader or _default_reader()
    records = {}
    for path in queries.get("records", []):
        records[path] = _undecided_or(lambda p=path: resolve_record(reader, repo, p))
    transclusions = {}
    for path in queries.get("transclusions", []):
        transclusions[path] = _undecided_or(lambda p=path: resolve_transclusions(reader, repo, p))
    return {"records": records, "transclusions": transclusions}


def _undecided_or(work: Callable[[], object]):
    try:
        return work()
    except Undecided as undecided:
        return {"status": "UNDECIDED", "question": undecided.question}
