# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Anchors, suggestions and transclusions (SPEC.md section 11)."""

from __future__ import annotations

import bisect
import re
import unicodedata

from .blocks import Refusal, blank, frontmatter_range, split_lines, walk
from .document import Document, TextLeaf, ref
from .inlines import find_links

ULID = re.compile(r"[0-7][0-9A-HJKMNP-TV-Z]{25}\Z")
TYPES = {"p", "code", "table", "h1", "h2", "h3", "h4", "h5", "h6"}
STATUSES = {"open", "accepted", "rejected", "resolved"}
WS = "\t\n\r "
COLLAPSE = re.compile(r"[\t\n\r ]+")
CONTEXT = 32


class Inconsistent(Exception):
    pass


# The canonical JSON of section 11.1.


def _must_escape(cp: int) -> bool:
    return cp <= 0x1F or 0x7F <= cp <= 0x9F or cp in (0x2028, 0x2029, 0xFEFF, 0xFFFE, 0xFFFF)


class Reader:
    """Reads a canonical value, refusing anything written another way."""

    def __init__(self, s: str) -> None:
        self.s = s
        self.at = 0

    def lit(self, text: str) -> None:
        if not self.s.startswith(text, self.at):
            raise Inconsistent
        self.at += len(text)

    def string(self) -> str:
        self.lit('"')
        out = []
        s = self.s
        while True:
            if self.at >= len(s):
                raise Inconsistent
            c = s[self.at]
            if c == '"':
                self.at += 1
                return "".join(out)
            if c == "\\":
                e = s[self.at + 1 : self.at + 2]
                if e in ('"', "\\"):
                    out.append(e)
                    self.at += 2
                elif e == "n":
                    out.append("\n")
                    self.at += 2
                elif e == "u":
                    h = s[self.at + 2 : self.at + 6]
                    if not re.fullmatch(r"[0-9a-f]{4}", h):
                        raise Inconsistent
                    cp = int(h, 16)
                    if not _must_escape(cp) or cp == 0x0A:
                        raise Inconsistent
                    out.append(chr(cp))
                    self.at += 6
                else:
                    raise Inconsistent
                continue
            if _must_escape(ord(c)):
                raise Inconsistent
            out.append(c)
            self.at += 1

    def number(self) -> int:
        m = re.compile(r"0|[1-9][0-9]*").match(self.s, self.at)
        if not m:
            raise Inconsistent
        self.at = m.end()
        return int(m.group())

    def done(self) -> None:
        if self.at != len(self.s):
            raise Inconsistent


def _oid(value: str, fmt: str) -> str:
    size = 64 if fmt == "sha256" else 40
    if not re.fullmatch(rf"[0-9a-f]{{{size}}}", value):
        raise Inconsistent
    return value


class Anchor:
    def __init__(self, value: str, fmt: str, suggestion: bool) -> None:
        r = Reader(value)
        r.lit('{"base": ')
        self.base = _oid(r.string(), fmt)
        r.lit(', "leaf": {"type": ')
        self.type = r.string()
        if self.type not in TYPES:
            raise Inconsistent
        r.lit(', "nth": ')
        self.nth = r.number()
        r.lit(', "text": ')
        self.text = r.string()
        r.lit('}, "span": ')
        self.span = r.string()
        r.lit(', "prefix": ')
        self.prefix = r.string()
        r.lit(', "suffix": ')
        self.suffix = r.string()
        self.replace = None
        if suggestion:
            r.lit(', "replace": ')
            self.replace = r.string()
        r.lit("}")
        r.done()
        self._check_self()

    def _check_self(self) -> None:
        if not self.span:
            raise Inconsistent
        if len(self.prefix) > CONTEXT or len(self.suffix) > CONTEXT:
            raise Inconsistent
        triple = self.prefix + self.span + self.suffix
        hits = _occurrences(self.text, triple)
        if len(hits) != 1:
            raise Inconsistent
        at = hits[0]
        if len(self.prefix) < CONTEXT and at != 0:
            raise Inconsistent
        if len(self.suffix) < CONTEXT and at + len(triple) != len(self.text):
            raise Inconsistent
        self.span_at = at + len(self.prefix)


def _occurrences(text: str, needle: str) -> list[int]:
    out, at = [], text.find(needle)
    while at != -1:
        out.append(at)
        at = text.find(needle, at + 1)
    return out


def raw_frontmatter(text: str) -> list[str] | None:
    """The frontmatter's lines as the file holds them, or None."""
    lines = [text[a:b] for a, b, _ in split_lines(text)]
    fm = frontmatter_range(lines)
    return lines[fm[0] + 1 : fm[1]] if fm else None


def parse_pins(fm: list[str] | None, fmt: str) -> dict[str, str]:
    """The pin lines of section 11.9. Raises Inconsistent when they are broken."""
    if fm is None:
        return {}
    headers = [i for i, ln in enumerate(fm) if ln.startswith("pins:")]
    if not headers:
        return {}
    if len(headers) > 1 or fm[headers[0]] != "pins:":
        raise Inconsistent
    pins: dict[str, str] = {}
    previous = None
    i = headers[0] + 1
    while i < len(fm) and fm[i].startswith("  - "):
        r = Reader(fm[i][4:])
        r.lit('{"path": ')
        path = r.string()
        r.lit(', "blob": ')
        blob = _oid(r.string(), fmt)
        r.lit("}")
        r.done()
        if previous is not None and not previous < path:
            raise Inconsistent
        previous = path
        pins[path] = blob
        i += 1
    tail_from = i
    for j in range(tail_from, len(fm)):
        if fm[j].startswith("  - "):
            between = fm[tail_from:j]
            if all(blank(x) or x[:1] in (" ", "#") for x in between):
                raise Inconsistent
    return pins


# Longest common subsequences.


def lcs_length(a, b) -> int:
    masks: dict = {}
    for i, c in enumerate(a):
        masks[c] = masks.get(c, 0) | (1 << i)
    full = (1 << len(a)) - 1
    v = full
    for c in b:
        m = masks.get(c, 0)
        u = v & m
        v = ((v + u) | (v - u)) & full
    return len(a) - bin(v).count("1")


def lcs_table(a, b) -> list[list[int]]:
    t = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) - 1, -1, -1):
        ti, tn = t[i], t[i + 1]
        for j in range(len(b) - 1, -1, -1):
            ti[j] = tn[j + 1] + 1 if a[i] == b[j] else max(tn[j], ti[j + 1])
    return t


def alignment(a, b) -> list[tuple[int, int]]:
    """Section 11.2's alignment: pairs of (index in a, index in b)."""
    t = lcs_table(a, b)
    out, i, j = [], 0, 0
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            out.append((i, j))
            i += 1
            j += 1
        elif t[i + 1][j] == t[i][j]:
            i += 1
        else:
            j += 1
    return out


def similar(a: TextLeaf, b: TextLeaf) -> tuple[int, int]:
    """(L, T) of the similarity 2L/T over keys."""
    x, y = f"{a.type}\x1f{a.text}", f"{b.type}\x1f{b.text}"
    return lcs_length(x, y), len(x) + len(y)


def words(text: str) -> list[str]:
    return [w for w in re.split(r"[\t\n\r ]+", text) if w]


def word_at_least_half(a: TextLeaf, b: TextLeaf) -> bool:
    x, y = words(a.text), words(b.text)
    if not x or not y:
        return False
    return 4 * lcs_length(x, y) >= len(x) + len(y)


def half(s: tuple[int, int]) -> bool:
    return 4 * s[0] >= s[1]


def exceeds(s1: tuple[int, int], s2: tuple[int, int]) -> bool:
    l1, t1 = s1
    l2, t2 = s2
    return 40 * l1 * t2 - 40 * l2 * t1 >= 3 * t1 * t2


class Correspondence:
    """Sections 11.3 and 11.4 for one pair of snapshots."""

    def __init__(self, base: list[TextLeaf], cur: list[TextLeaf]) -> None:
        self.base, self.cur = base, cur
        self.pair: dict[int, tuple[str, int]] = {}
        self.base_count = _counts(base)
        self.cur_count = _counts(cur)
        self.chain = self._chain()
        self._gaps()
        paired = {j for _, j in self.pair.values()}
        self.unmatched = [j for j in range(len(cur)) if j not in paired]

    def _chain(self) -> list[tuple[int, int]]:
        where = {}
        for j, c in enumerate(self.cur):
            if self.cur_count[c.key] == 1:
                where[c.key] = j
        pairs = [
            (i, where[b.key])
            for i, b in enumerate(self.base)
            if self.base_count[b.key] == 1 and b.key in where
        ]
        n = len(pairs)
        best = [1] * n
        for i in range(n - 1, -1, -1):
            for j in range(i + 1, n):
                if pairs[j][1] > pairs[i][1] and best[j] + 1 > best[i]:
                    best[i] = best[j] + 1
        chain: list[tuple[int, int]] = []
        length = max(best, default=0)
        low, prev_c = 0, -1
        while length:
            pick = min(
                (i for i in range(low, n) if best[i] == length and pairs[i][1] > prev_c),
                key=lambda i: pairs[i][1],
            )
            chain.append(pairs[pick])
            low, prev_c = pick + 1, pairs[pick][1]
            length -= 1
        for p in pairs:
            self.pair[p[0]] = ("EXACT" if p in chain else "MOVED", p[1])
        return chain

    def _gap_bounds(self):
        pts = [(-1, -1), *self.chain, (len(self.base), len(self.cur))]
        return list(zip(pts, pts[1:], strict=False))

    def _gaps(self) -> None:
        moved_cur = {j for kind, j in self.pair.values() if kind == "MOVED"}
        for (b0, c0), (b1, c1) in self._gap_bounds():
            bs = [i for i in range(b0 + 1, b1) if i not in self.pair]
            cs = [j for j in range(c0 + 1, c1) if j not in moved_cur]
            ka = [self.base[i].key for i in bs]
            kb = [self.cur[j].key for j in cs]
            used_a, used_b = set(), set()
            for x, y in alignment(ka, kb):
                self.pair[bs[x]] = ("EXACT", cs[y])
                used_a.add(x)
                used_b.add(y)
            left_b = [bs[x] for x in range(len(bs)) if x not in used_a]
            left_c = [cs[y] for y in range(len(cs)) if y not in used_b]
            self._edits(left_b, left_c)

    def _edits(self, left_b: list[int], left_c: list[int]) -> None:
        sims = {(i, j): similar(self.base[i], self.cur[j]) for i in left_b for j in left_c}
        for i in left_b:
            for j in left_c:
                s = sims[i, j]
                if not half(s):
                    continue
                if all(exceeds(s, sims[i, o]) for o in left_c if o != j) and all(
                    exceeds(s, sims[o, j]) for o in left_b if o != i
                ):
                    self.pair[i] = ("EDITED", j)
                    break

    def gap_of(self, k: int) -> tuple[range, range]:
        before = [p for p in self.chain if p[0] < k]
        after = [p for p in self.chain if p[0] > k]
        b0, c0 = before[-1] if before else (-1, -1)
        b1, c1 = after[0] if after else (len(self.base), len(self.cur))
        return range(b0 + 1, b1), range(c0 + 1, c1)

    def judge(self, k: int) -> tuple[str, int | None]:
        """(kind, paired current index), or ("REFUSED:<reason>", None)."""
        leaf = self.base[k]
        pair = self.pair.get(k)
        if pair is None:
            if self.cur_count.get(leaf.key, 0):
                return "REFUSED:unaccounted-copy", None
            return "ORPHANED", None
        kind, j = pair
        gap_b, gap_c = self.gap_of(k)
        if kind == "EXACT":
            if self.base_count[leaf.key] > 1 or self.cur_count[leaf.key] > 1:
                nb = sum(self.base[i].key == leaf.key for i in gap_b)
                nc = sum(self.cur[x].key == leaf.key for x in gap_c)
                if nb != nc:
                    return "REFUSED:repeat", None
            for u in self.unmatched:
                c = self.cur[u]
                if c.key != leaf.key and word_at_least_half(leaf, c):
                    return "REFUSED:near-copy", None
        elif kind == "MOVED":
            for u in self.unmatched:
                if half(similar(leaf, self.cur[u])):
                    return "REFUSED:near-copy", None
            if any(u in gap_c for u in self.unmatched):
                return "REFUSED:refilled-gap", None
        else:
            if any(self.cur[u].key == leaf.key for u in self.unmatched):
                return "REFUSED:exact-copy", None
            if any(u in gap_c for u in self.unmatched):
                return "REFUSED:crowded-gap", None
            for u in self.unmatched:
                if half(similar(leaf, self.cur[u])):
                    return "REFUSED:near-copy", None
        return kind, j


def _counts(leaves: list[TextLeaf]) -> dict:
    out: dict = {}
    for leaf in leaves:
        out[leaf.key] = out.get(leaf.key, 0) + 1
    return out


# The span (section 11.5).


def _collapse(s: str) -> str:
    return COLLAPSE.sub(" ", s)


def _neighbour_equal(a: str, b: str) -> bool:
    if a == "" or b == "":
        return a == b
    return a == b or (a in WS and b in WS)


def _side_holds(context: str, text: str, is_prefix: bool, prose: bool) -> bool:
    short = len(context) < CONTEXT
    if prose:
        context, text = _collapse(context), _collapse(text)
    if short:
        return text == context
    return text.endswith(context) if is_prefix else text.startswith(context)


def find_span(anchor: Anchor, paired: TextLeaf, comment: bool) -> tuple[str, int | None]:
    """("HIT", offset), ("DETACHED", None) or ("REFUSED:span-ambiguous", None)."""
    text = paired.text
    span = anchor.span
    start = anchor.span_at
    end = start + len(span)
    old = anchor.text
    before_old = old[start - 1 : start] if start else ""
    after_old = old[end : end + 1]
    prose = anchor.type not in ("code", "table") and paired.type not in ("code", "table")
    hits = []
    for at in _occurrences(text, span):
        stop = at + len(span)
        before = text[at - 1 : at] if at else ""
        after = text[stop : stop + 1]
        if not (_neighbour_equal(before_old, before) and _neighbour_equal(after_old, after)):
            continue
        p_ok = _side_holds(anchor.prefix, text[:at], True, prose)
        s_ok = _side_holds(anchor.suffix, text[stop:], False, prose)
        if prose and comment:
            if not anchor.prefix and not anchor.suffix:
                ok = p_ok and s_ok
            else:
                ok = (p_ok and bool(anchor.prefix)) or (s_ok and bool(anchor.suffix))
        else:
            ok = p_ok and s_ok
        if ok:
            hits.append(at)
    if not hits:
        return "DETACHED", None
    if len(hits) > 1:
        return "REFUSED:span-ambiguous", None
    hit = hits[0]
    pairs = dict(alignment(old, text))
    for offset in range(len(span)):
        if pairs.get(start + offset) != hit + offset:
            return "DETACHED", None
    return "HIT", hit


# Write-back (section 11.7).


def write_back(doc: Document, raw: str, leaf: TextLeaf, hit: int, span_len: int, replace: str):
    """The document after the suggestion, or None when the span does not map."""
    node = leaf.node
    if node.type == "table":
        return None
    content: str = node.content
    srcs = node.srcs
    before = leaf.text[:hit]
    span = leaf.text[hit : hit + span_len]

    def nfc(piece: str) -> str:
        return unicodedata.normalize("NFC", piece)

    a = next((i for i in range(len(content) + 1) if nfc(content[:i]) == before), None)
    if a is None:
        return None
    b = next((i for i in range(a + 1, len(content) + 1) if nfc(content[a:i]) == span), None)
    if b is None:
        return None
    if node.type == "code_block" and b == len(content) and content[b - 1] == "\n":
        return None
    if any(srcs[i] is None for i in range(a, b)):
        return None
    if b < len(content) and srcs[b] is None:
        return None
    raw_a = srcs[a]
    raw_b = srcs[b] if b < len(content) else srcs[b - 1] + 1
    text = replace
    if "\n" in replace:
        starts = [s for s, _, _ in doc.spans]
        at = bisect.bisect_right(starts, raw_a) - 1
        _, _, eol = doc.spans[at]
        info = doc.line_info.get(at + 1)
        if info is None or info.first_of_item or info.lazy or info.has_tab or not eol:
            return None
        text = replace.replace("\n", eol + info.prefix)
    return raw[:raw_a] + text + raw[raw_b:]


# Transclusions: the one inline shape (section 11.9).


def transclusion_link(content: str) -> tuple[str, str] | None:
    """(path, name) when the paragraph is exactly one link titled `transclude`."""
    links = find_links(content)
    if len(links) != 1:
        return None
    link = links[0]
    if link.start != 0 or link.end != len(content) or link.title != '"transclude"':
        return None
    if "#" not in link.destination:
        return None
    path, name = link.destination.split("#", 1)
    return path, name


def resolve_path(referrer: str, path: str) -> str | None:
    """The repository path, or None when unresolvable."""
    segs = path.split("/")
    if path.startswith("/") or ":" in segs[0]:
        return None
    out = referrer.split("/")[:-1]
    for seg in segs:
        if seg == ".":
            continue
        if seg == "..":
            if not out:
                return None
            out.pop()
        else:
            out.append(seg)
    return "/".join(out)


def _under(path: tuple[int, ...], roots: list[tuple[int, ...]]) -> bool:
    return any(path[: len(r)] == r for r in roots)


def _refused(reason: str, suggestion) -> dict:
    return {"status": f"REFUSED({reason})", "leaf": None, "span": None, "suggestion": suggestion}


class Repository:
    def __init__(self, repo: dict) -> None:
        self.fmt = repo.get("object_format", "sha1")
        self.tree: dict[str, str] = repo["tree"]
        self.blobs: dict[str, str] = repo["blobs"]
        self._docs: dict[str, Document | None] = {}

    def run(self, queries: dict) -> dict:
        return {
            "records": {p: self.record(p) for p in queries.get("records", [])},
            "transclusions": {p: self.referrer(p) for p in queries.get("transclusions", [])},
        }

    def document(self, text: str) -> Document | None:
        """The read document, or None when the profile refuses it."""
        if text not in self._docs:
            try:
                self._docs[text] = Document(text)
            except Refusal:
                self._docs[text] = None
        return self._docs[text]

    # Records.

    def record(self, path: str) -> dict:
        text = self.tree[path]
        lines = raw_frontmatter(text)
        is_suggestion = lines is not None and "kind: suggestion" in lines
        stale = {"gate": "stale", "reason": None} if is_suggestion else None
        try:
            kind = self._check_record(path, text, lines)
        except Inconsistent:
            return _refused("record-inconsistent", stale)
        directory, _, _ = path.rpartition("/")
        doc_path = directory[: -len(".notes")]
        if doc_path not in self.tree:
            return _refused("document-missing", stale)
        current = self.document(self.tree[doc_path])
        if current is None:
            return _refused("not-in-profile", stale)
        if kind == "reply":
            parent = f"{directory}/{self._reply_to}.md"
            status = "REPLY" if parent in self.tree else "#REF!(reply-to)"
            return {"status": status, "leaf": None, "span": None, "suggestion": None}
        anchor = self._anchor
        base_text = self.blobs.get(anchor.base)
        if base_text is None:
            return _refused("base-unavailable", stale)
        base = self.document(base_text)
        if base is None:
            return _refused("not-in-profile", stale)
        wanted = (anchor.type, anchor.text)
        ordinals = [i for i, leaf in enumerate(base.text_leaves) if leaf.key == wanted]
        if anchor.nth >= len(ordinals):
            return _refused("record-inconsistent", stale)
        k = ordinals[anchor.nth]
        corr = Correspondence(base.text_leaves, current.text_leaves)
        verdict, j = corr.judge(k)
        if verdict.startswith("REFUSED:"):
            return _refused(verdict[len("REFUSED:") :], stale)
        if verdict == "ORPHANED":
            return {"status": "ORPHANED", "leaf": None, "span": None, "suggestion": stale}
        paired = current.text_leaves[j]
        leaf = ref(paired.node)
        if verdict == "EDITED":
            found, hit = find_span(anchor, paired, not is_suggestion)
            if found.startswith("REFUSED:"):
                return _refused(found[len("REFUSED:") :], stale)
            if found == "DETACHED":
                return {"status": "DETACHED", "leaf": leaf, "span": None, "suggestion": stale}
            status = "EDITED"
        else:
            hit = anchor.span_at
            status = "RESOLVED" if verdict == "EXACT" else "MOVED"
        suggestion = stale
        if is_suggestion and status in ("RESOLVED", "EDITED") and self._open:
            written = write_back(
                current, self.tree[doc_path], paired, hit, len(anchor.span), anchor.replace
            )
            if written is None:
                suggestion = {"gate": "stale", "reason": "unmappable-offset"}
            else:
                suggestion = {"gate": "apply", "written": written}
        return {
            "status": status,
            "leaf": leaf,
            "span": [hit, hit + len(anchor.span)],
            "suggestion": suggestion,
        }

    def _check_record(self, path: str, text: str, lines: list[str] | None) -> str:
        directory, _, name = path.rpartition("/")
        if not directory.endswith(".notes") or not name.endswith(".md"):
            raise Inconsistent
        if not ULID.match(name[:-3]):
            raise Inconsistent
        if lines is None:
            raise Inconsistent
        if len(lines) == 2 and lines[0].startswith("reply-to: "):
            if lines[1] != "kind: comment":
                raise Inconsistent
            r = Reader(lines[0][len("reply-to: ") :])
            target = r.string()
            r.done()
            if not ULID.match(target):
                raise Inconsistent
            self._reply_to = target
            kind = "reply"
        elif len(lines) == 3 and lines[0].startswith("anchor: "):
            if lines[1] not in ("kind: comment", "kind: suggestion"):
                raise Inconsistent
            if not lines[2].startswith("status: ") or lines[2][8:] not in STATUSES:
                raise Inconsistent
            self._anchor = Anchor(lines[0][8:], self.fmt, lines[1] == "kind: suggestion")
            self._open = lines[2] == "status: open"
            kind = "anchor"
        else:
            raise Inconsistent
        try:
            Document(text, check_links=False)
        except Refusal:
            raise Inconsistent from None
        return kind

    # Transclusions.

    def referrer(self, path: str):
        text = self.tree[path]
        doc = self.document(text)
        if doc is None:
            return "REFUSED(not-in-profile)"
        out = []
        for node in walk(doc.root):
            if node.type != "paragraph":
                continue
            link = transclusion_link(node.content)
            if link is None:
                continue
            status, unit = self._transclude(path, text, link)
            out.append({"leaf": ref(node), "status": status, "unit": unit})
        return out

    def _transclude(self, path: str, text: str, link: tuple[str, str]):
        raw_path, name = link
        target_path = resolve_path(path, raw_path)
        if target_path is None:
            return "REFUSED(unresolvable-path)", None
        try:
            pins = parse_pins(raw_frontmatter(text), self.fmt)
        except Inconsistent:
            return "REFUSED(record-inconsistent)", None
        if target_path not in self.tree:
            return "REFUSED(document-missing)", None
        current = self.document(self.tree[target_path])
        if current is None:
            return "REFUSED(not-in-profile)", None
        if name not in current.names and name in current.slugs:
            return f"#REF!({name})", None
        blob = pins.get(raw_path)
        pinned_text = None if blob is None else self.blobs.get(blob)
        if pinned_text is None:
            return "REFUSED(base-unavailable)", None
        pinned = self.document(pinned_text)
        if pinned is None:
            return "REFUSED(not-in-profile)", None
        if name not in pinned.names:
            return "REFUSED(record-inconsistent)", None
        if name not in current.names:
            return f"#REF!({name})", None
        corr = Correspondence(pinned.text_leaves, current.text_leaves)
        roots = [n.path for n in pinned.bound[name]]
        pairs = []
        for k, leaf in enumerate(pinned.text_leaves):
            if not _under(leaf.node.path, roots):
                continue
            verdict, j = corr.judge(k)
            if verdict.startswith("REFUSED:"):
                return f"REFUSED(pinned-{verdict[len('REFUSED:') :]})", None
            if verdict == "ORPHANED":
                return "REFUSED(pinned-orphaned)", None
            pairs.append(j)
        now = [n.path for n in current.bound[name]]
        for j in pairs:
            if not _under(current.text_leaves[j].node.path, now):
                return "REFUSED(name-rebound)", None
        return "RESOLVED", {"document": target_path, "target": current.names[name]}
