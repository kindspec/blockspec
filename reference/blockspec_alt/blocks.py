# SPDX-License-Identifier: Apache-2.0 OR MIT
"""The block parser: CommonMark 0.31.2 block structure, GFM pipe tables, and the
refusals of SPEC.md sections 4 and 9.

It follows CommonMark's phases-of-a-line algorithm (spec appendix, "A parsing
strategy"): walk the open containers, try block starts, then add the rest of
the line. Every character of a leaf's content remembers where it came from in
the file, so a suggestion can be written back (SPEC.md section 11.7).
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

CONFLICT = re.compile(r"(?:<{7,}|>{7,}|\|{7,})(?: |\Z)|={7,}\Z")
EOL = re.compile(r"\r\n|\n|\r")

RE_ATX = re.compile(r"#{1,6}(?:[ \t]+|\Z)")
RE_ATX_ONLY_CLOSE = re.compile(r"\A[ \t]*#+[ \t]*\Z")
RE_ATX_CLOSE = re.compile(r"[ \t]+#+[ \t]*\Z")
RE_FENCE = re.compile(r"`{3,}(?!.*`)|~{3,}")
RE_FENCE_CLOSE = re.compile(r"(?:`{3,}|~{3,})(?=[ \t]*\Z)")
RE_SETEXT = re.compile(r"(?:=+|-+)[ \t]*\Z")
RE_THEMATIC = re.compile(r"(?:(?:\*[ \t]*){3,}|(?:_[ \t]*){3,}|(?:-[ \t]*){3,})\Z")
RE_BULLET = re.compile(r"[*+-]")
RE_ORDERED = re.compile(r"(\d{1,9})([.)])")
RE_MARKER = re.compile(r"[ \t]*<!--[ \t]*#([a-z0-9][a-z0-9-]*)(:begin|:end)?[ \t]*-->[ \t]*\Z")
RE_DELIMITER_CELL = re.compile(r":?-+:?\Z")

_SP = r"[ \t]"
_TAG = r"[A-Za-z][A-Za-z0-9-]*"
_ATTR_NAME = r"[a-zA-Z_:][a-zA-Z0-9:._-]*"
_UNQUOTED = "[^ \t\"'=<>`]+"
_ATTR_VALUE = rf"(?:{_UNQUOTED}|'[^']*'|\"[^\"]*\")"
_ATTR = rf"(?:{_SP}+{_ATTR_NAME}(?:{_SP}*={_SP}*{_ATTR_VALUE})?)"
_OPEN_TAG = rf"<{_TAG}{_ATTR}*{_SP}*/?>"
_CLOSE_TAG = rf"</{_TAG}{_SP}*>"
_BLOCK_NAMES = (
    "address|article|aside|base|basefont|blockquote|body|caption|center|col|colgroup|"
    "dd|details|dialog|dir|div|dl|dt|fieldset|figcaption|figure|footer|form|frame|"
    "frameset|h1|h2|h3|h4|h5|h6|head|header|hr|html|iframe|legend|li|link|main|menu|"
    "menuitem|meta|nav|noframes|ol|optgroup|option|p|param|section|search|summary|"
    "table|tbody|td|tfoot|th|thead|title|tr|track|ul"
)
RE_HTML_START = (
    re.compile(r"<(?:script|pre|textarea|style)(?:[ \t]|>|\Z)", re.I | re.A),
    re.compile(r"<!--"),
    re.compile(r"<\?"),
    re.compile(r"<![A-Za-z]"),
    re.compile(r"<!\[CDATA\["),
    re.compile(rf"</?(?:{_BLOCK_NAMES})(?:[ \t]|/?>|\Z)", re.I | re.A),
)
RE_HTML_7 = re.compile(rf"(?:{_OPEN_TAG}|{_CLOSE_TAG}){_SP}*\Z")


class Refusal(Exception):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def split_lines(text: str) -> list[tuple[int, int, str]]:
    """Each line as (start, end, ending), end excluding the ending."""
    out, at = [], 0
    for m in EOL.finditer(text):
        out.append((at, m.start(), m.group()))
        at = m.end()
    if at < len(text):
        out.append((at, len(text), ""))
    return out


def blank(s: str) -> bool:
    return not s.strip(" \t")


def frontmatter_range(lines: list[str]) -> tuple[int, int] | None:
    """(0-based opening index, closing index), or None (SPEC.md section 5)."""
    if len(lines) < 2 or lines[0] != "---" or blank(lines[1]):
        return None
    for i in range(1, len(lines)):
        if lines[i].startswith("---") and not lines[i][3:].strip(" \t"):
            return 0, i
    return None


@dataclass
class Line:
    """One line of a leaf: its content and each character's raw offset."""

    text: str
    srcs: list[int | None]
    number: int
    lazy: bool
    as_it_stands: str = ""


@dataclass
class LineInfo:
    """What write-back needs about a line that holds leaf content."""

    prefix: str
    has_tab: bool
    first_of_item: bool
    lazy: bool


@dataclass
class Node:
    type: str
    parent: Node | None
    start: int
    end: int = 0
    open: bool = True
    children: list[Node] = field(default_factory=list)
    path: tuple[int, ...] = ()
    lines: list[Line] = field(default_factory=list)
    content: object = None
    srcs: list[int | None] = field(default_factory=list)
    rows: list[list[str]] = field(default_factory=list)
    level: int = 0
    marker: tuple[str, str | None] | None = None
    fence_char: str = ""
    fence_len: int = 0
    fence_offset: int = 0
    list_data: tuple | None = None
    marker_offset: int = 0
    padding: int = 0


CONTAINERS = ("doc", "block_quote", "list_item")


def split_cells(s: str, keep_leading: bool = False) -> list[str]:
    """A table row's cells: trimmed, `\\|` read as `|`, outer pipes dropped."""
    s = s.rstrip(" \t")
    if not keep_leading:
        s = s.lstrip(" \t")
    at = 1 if s.startswith("|") else 0
    cells, cur = [], []
    ended_by_pipe = False
    while at < len(s):
        c = s[at]
        if c == "\\" and s[at + 1 : at + 2] == "|":
            cur.append("|")
            at += 2
            ended_by_pipe = False
            continue
        if c == "|":
            cells.append("".join(cur))
            cur = []
            at += 1
            ended_by_pipe = True
            continue
        cur.append(c)
        at += 1
        ended_by_pipe = False
    if not ended_by_pipe:
        cells.append("".join(cur))
    return [c.strip(" \t") for c in cells]


def has_unescaped_pipe(s: str) -> bool:
    return any(c == "|" and (i == 0 or s[i - 1] != "\\") for i, c in enumerate(s))


_ASCII_PUNCT = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"


def _skip_ws(s: str, i: int) -> int:
    """Spaces or tabs, including up to one line ending."""
    while i < len(s) and s[i] in " \t":
        i += 1
    if i < len(s) and s[i] == "\n":
        i += 1
        while i < len(s) and s[i] in " \t":
            i += 1
    return i


def parse_destination(s: str, i: int) -> int | None:
    """End of a link destination at `i`, or None."""
    if s[i : i + 1] == "<":
        j = i + 1
        while j < len(s):
            c = s[j]
            if c == "\n" or c == "<":
                return None
            if c == "\\" and j + 1 < len(s) and s[j + 1] != "\n":
                j += 2
                continue
            if c == ">":
                return j + 1
            j += 1
        return None
    j, depth = i, 0
    while j < len(s):
        c = s[j]
        if c == "\\" and s[j + 1 : j + 2] and s[j + 1] in _ASCII_PUNCT:
            j += 2
            continue
        if c == "(":
            depth += 1
        elif c == ")":
            if depth == 0:
                break
            depth -= 1
        elif c <= " " or c == "\x7f":
            break
        j += 1
    if j == i or depth:
        return None
    return j


def parse_title(s: str, i: int) -> int | None:
    """End of a link title at `i`, or None."""
    opener = s[i : i + 1]
    if opener not in ('"', "'", "("):
        return None
    closer = ")" if opener == "(" else opener
    j = i + 1
    while j < len(s):
        c = s[j]
        if c == "\\" and j + 1 < len(s):
            j += 2
            continue
        if c == closer:
            return j + 1
        if opener == "(" and c == "(":
            return None
        j += 1
    return None


def starts_with_reference(s: str) -> bool:
    """Whether paragraph content `s` begins with a link reference definition."""
    if not s.startswith("["):
        return False
    i, n = 1, 0
    while True:
        if i >= len(s):
            return False
        c = s[i]
        if c == "]":
            break
        if c == "[":
            return False
        if c == "\\" and i + 1 < len(s):
            i += 2
            n += 2
        else:
            i += 1
            n += 1
        if n > 999:
            return False
    if blank(s[1:i].replace("\n", " ")) or s[i + 1 : i + 2] != ":":
        return False
    at = _skip_ws(s, i + 2)
    end = parse_destination(s, at)
    if end is None:
        return False

    def at_line_end(p: int) -> bool:
        while p < len(s) and s[p] in " \t":
            p += 1
        return p == len(s) or s[p] == "\n"

    after = _skip_ws(s, end)
    if after != end:
        t = parse_title(s, after)
        if t is not None and at_line_end(t):
            return True
    return at_line_end(end)


class Parser:
    def __init__(self, text: str, spans: list[tuple[int, int, str]], first: int) -> None:
        self.text = text
        self.spans = spans
        self.first = first
        self.doc = Node("doc", None, 1)
        self.tip = self.doc
        self.old_tip = self.doc
        self.last_matched = self.doc
        self.all_closed = True
        self.line = ""
        self.base = 0
        self.number = 0
        self.offset = 0
        self.column = 0
        self.partial = False
        self.next_nonspace = 0
        self.next_nonspace_column = 0
        self.indent = 0
        self.indented = False
        self.is_blank = False
        self.prefix_end = 0
        self.prefix_partial = False
        self.first_of_item = False
        self.line_info: dict[int, LineInfo] = {}
        self.item_blank_lines: set[int] = set()

    # Moving along a line.

    def peek(self, at: int) -> str:
        return self.line[at] if at < len(self.line) else ""

    def find_next_nonspace(self) -> None:
        i, col = self.offset, self.column
        while i < len(self.line):
            c = self.line[i]
            if c == " ":
                i += 1
                col += 1
            elif c == "\t":
                i += 1
                col += 4 - col % 4
            else:
                break
        self.is_blank = i >= len(self.line)
        self.next_nonspace = i
        self.next_nonspace_column = col
        self.indent = col - self.column
        self.indented = self.indent >= 4

    def advance_next_nonspace(self) -> None:
        self.offset = self.next_nonspace
        self.column = self.next_nonspace_column
        self.partial = False

    def advance_offset(self, count: int, columns: bool) -> None:
        while count > 0 and self.offset < len(self.line):
            c = self.line[self.offset]
            if c == "\t":
                to_tab = 4 - self.column % 4
                if columns:
                    self.partial = to_tab > count
                    step = min(count, to_tab)
                    self.column += step
                    if not self.partial:
                        self.offset += 1
                    count -= step
                else:
                    self.partial = False
                    self.column += to_tab
                    self.offset += 1
                    count -= 1
            else:
                self.partial = False
                self.offset += 1
                self.column += 1
                count -= 1

    def mark_prefix(self) -> None:
        self.prefix_end = self.offset
        self.prefix_partial = self.partial

    # The tree.

    def finalize(self, node: Node, line: int) -> None:
        node.open = False
        node.end = line
        if node.type in ("list", "list_item"):
            # An item continues through blank lines. Those are not its lines,
            # and they stay blank in the item's own container (`>` included).
            while node.end > node.start and node.end in self.item_blank_lines:
                node.end -= 1
        if node.type == "paragraph":
            self.finish_paragraph(node)
        self.tip = node.parent  # type: ignore[assignment]

    def finish_paragraph(self, node: Node) -> None:
        text, srcs = "", []
        last = len(node.lines) - 1
        for i, ln in enumerate(node.lines):
            t, s = ln.text, ln.srcs
            if i == last:
                kept = len(t.rstrip(" \t"))
                t, s = t[:kept], s[:kept]
            text += t
            srcs += s
            if i < last:
                text += "\n"
                srcs.append(self.spans[ln.number - 1][1])
        node.content, node.srcs = text, srcs
        if starts_with_reference(text):
            raise Refusal("link-reference-definition")

    def add_child(self, kind: str) -> Node:
        while not self.can_contain(self.tip, kind):
            self.finalize(self.tip, self.number - 1)
        node = Node(kind, self.tip, self.number)
        self.tip.children.append(node)
        self.tip = node
        return node

    @staticmethod
    def can_contain(parent: Node, kind: str) -> bool:
        if parent.type == "list":
            return kind == "list_item"
        return parent.type in CONTAINERS and kind != "list_item"

    def close_unmatched(self) -> None:
        if not self.all_closed:
            while self.old_tip is not self.last_matched:
                parent = self.old_tip.parent
                self.finalize(self.old_tip, self.number - 1)
                self.old_tip = parent  # type: ignore[assignment]
            self.all_closed = True

    def remainder(self) -> tuple[str, list[int | None]]:
        """The rest of the line and each character's raw offset. What is left
        of a partly consumed tab is spaces that come from no raw character."""
        text, srcs = "", []
        offset = self.offset
        if self.partial:
            spaces = 4 - self.column % 4
            text = " " * spaces
            srcs = [None] * spaces
            offset += 1
        rest = self.line[offset:]
        text += rest
        srcs += list(range(self.base + offset, self.base + len(self.line)))
        return text, srcs

    def add_line(self, lazy: bool = False) -> None:
        text, srcs = self.remainder()
        as_it_stands = self.line[self.prefix_end :] if lazy else text
        self.tip.lines.append(Line(text, srcs, self.number, lazy, as_it_stands))
        self.note_line(lazy)

    def note_line(self, lazy: bool) -> None:
        prefix = self.line[: self.prefix_end]
        self.line_info[self.number] = LineInfo(
            prefix, "\t" in prefix or self.prefix_partial, self.first_of_item, lazy
        )

    # One line.

    def incorporate(self, index: int) -> None:
        start, end, _ = self.spans[index]
        self.line = self.text[start:end]
        self.base = start
        self.number = index + 1
        self.offset = self.column = 0
        self.partial = False
        self.prefix_end = 0
        self.prefix_partial = False
        self.first_of_item = False
        self.old_tip = self.tip
        container = self.doc
        while container.children and container.children[-1].open:
            container = container.children[-1]
            self.find_next_nonspace()
            outcome = self.continues(container)
            if outcome == 2:
                return
            if outcome == 1:
                container = container.parent  # type: ignore[assignment]
                break
        self.all_closed = container is self.old_tip
        self.last_matched = container
        if container.type == "table":
            self.table_line(container)
            return
        leaf_taking_lines = container.type in ("code_block", "html_block")
        while not leaf_taking_lines:
            self.find_next_nonspace()
            outcome = self.block_start(container)
            if outcome == 2:
                return
            if outcome == 1:
                container = self.tip
                continue
            if container.type == "paragraph" and not self.indented and self.try_table(container):
                return
            self.advance_next_nonspace()
            break
        if not self.all_closed and not self.is_blank and self.tip.type == "paragraph":
            self.add_line(lazy=True)
            return
        self.close_unmatched()
        if container.type in ("paragraph", "code_block", "html_block"):
            self.add_line()
        elif self.offset < len(self.line) and not self.is_blank:
            self.add_child("paragraph")
            self.advance_next_nonspace()
            self.add_line()

    def continues(self, c: Node) -> int:
        """0 matched, 1 not matched, 2 the line is consumed (a closing fence)."""
        kind = c.type
        if kind == "block_quote":
            if not self.indented and self.peek(self.next_nonspace) == ">":
                self.advance_next_nonspace()
                self.advance_offset(1, False)
                if self.peek(self.offset) in (" ", "\t"):
                    self.advance_offset(1, True)
                self.mark_prefix()
                return 0
            return 1
        if kind == "list":
            return 0
        if kind == "list_item":
            if self.is_blank:
                if not c.children:
                    return 1
                self.item_blank_lines.add(self.number)
                self.advance_next_nonspace()
            elif self.indent >= c.marker_offset + c.padding:
                self.advance_offset(c.marker_offset + c.padding, True)
            else:
                return 1
            self.mark_prefix()
            return 0
        if kind == "code_block":
            rest = self.line[self.next_nonspace :]
            m = RE_FENCE_CLOSE.match(rest)
            if (
                self.indent <= 3
                and rest[:1] == c.fence_char
                and m is not None
                and len(m.group()) >= c.fence_len
            ):
                self.all_closed = True
                self.finalize(c, self.number)
                return 2
            i = c.fence_offset
            while i > 0 and self.peek(self.offset) in (" ", "\t"):
                self.advance_offset(1, True)
                i -= 1
            return 0
        if kind == "paragraph":
            return 1 if self.is_blank else 0
        if kind == "table":
            return 1 if self.is_blank else 0
        return 1

    def block_start(self, container: Node) -> int:
        rest = self.line[self.next_nonspace :]
        if not self.indented:
            if rest[:1] == ">":
                self.advance_next_nonspace()
                self.advance_offset(1, False)
                if self.peek(self.offset) in (" ", "\t"):
                    self.advance_offset(1, True)
                self.close_unmatched()
                self.add_child("block_quote")
                self.mark_prefix()
                return 1
            m = RE_ATX.match(rest)
            if m:
                self.atx_heading(m)
                return 2
            m = RE_FENCE.match(rest)
            if m:
                self.close_unmatched()
                node = self.add_child("code_block")
                node.fence_char = m.group()[0]
                node.fence_len = len(m.group())
                node.fence_offset = self.indent
                return 2
            if rest[:1] == "<":
                outcome = self.html_start(container, rest)
                if outcome:
                    return outcome
            if container.type == "paragraph" and RE_SETEXT.match(rest):
                self.close_unmatched()
                if starts_with_reference("\n".join(ln.text for ln in container.lines)):
                    raise Refusal("link-reference-definition")
                raise Refusal("setext-heading")
            if RE_THEMATIC.match(rest):
                self.close_unmatched()
                self.add_child("thematic_break")
                self.tip.content = ""
                return 2
        marker = self.match_list_marker(container)
        if marker is not None:
            self.start_list_item(container, marker)
            return 1
        if self.indented and self.tip.type != "paragraph" and not self.is_blank:
            raise Refusal("indented-code")
        return 0

    def html_start(self, container: Node, rest: str) -> int:
        kind = next((t for t, r in enumerate(RE_HTML_START, 1) if r.match(rest)), 0)
        maybe_lazy = not self.all_closed and not self.is_blank and self.tip.type == "paragraph"
        if not kind and container.type != "paragraph" and not maybe_lazy:
            if RE_HTML_7.match(rest):
                kind = 7
        if not kind:
            return 0
        m = RE_MARKER.match(rest) if kind == 2 else None
        if m is None:
            raise Refusal("raw-html")
        self.close_unmatched()
        node = self.add_child("html_block")
        node.marker = (m.group(1), m.group(2)[1:] if m.group(2) else None)
        node.content = self.remainder()[0] + "\n"
        self.finalize(node, self.number)
        return 2

    def atx_heading(self, m: re.Match) -> None:
        self.advance_next_nonspace()
        self.advance_offset(len(m.group()), False)
        self.close_unmatched()
        node = self.add_child("heading")
        node.level = len(m.group().strip(" \t"))
        rest = self.line[self.offset :]
        rest = RE_ATX_ONLY_CLOSE.sub("", rest, count=1)
        rest = RE_ATX_CLOSE.sub("", rest, count=1)
        rest = rest.rstrip(" \t")
        lead = len(rest) - len(rest.lstrip(" \t"))
        node.content = rest[lead:]
        base = self.base + self.offset + lead
        node.srcs = list(range(base, base + len(node.content)))
        self.note_line(False)

    def match_list_marker(self, container: Node):
        """The list marker this line opens, or None. Moves nothing."""
        if self.indent >= 4:
            return None
        rest = self.line[self.next_nonspace :]
        m = RE_BULLET.match(rest)
        ordered = None
        if not m:
            ordered = RE_ORDERED.match(rest)
            if ordered is None or (container.type == "paragraph" and int(ordered.group(1)) != 1):
                return None
            m = ordered
        after = rest[m.end() :]
        if after[:1] not in ("", " ", "\t"):
            return None
        if container.type == "paragraph" and blank(after):
            return None
        return m, ordered

    def start_list_item(self, container: Node, marker) -> None:
        m, ordered = marker
        data = ("ordered", ordered.group(2)) if ordered else ("bullet", m.group())
        indent = self.indent
        self.advance_next_nonspace()
        self.advance_offset(m.end(), True)
        col, off = self.column, self.offset
        while True:
            self.advance_offset(1, True)
            if not (self.column - col < 5 and self.peek(self.offset) in (" ", "\t")):
                break
        blank_item = self.offset >= len(self.line)
        spaces = self.column - col
        if spaces >= 5 or spaces < 1 or blank_item:
            padding = m.end() + 1
            self.column, self.offset = col, off
            self.partial = False
            if self.peek(self.offset) in (" ", "\t"):
                self.advance_offset(1, True)
        else:
            padding = m.end() + spaces
        self.close_unmatched()
        if self.tip.type != "list" or self.tip.list_data != data:
            lst = self.add_child("list")
            lst.list_data = data
        item = self.add_child("list_item")
        item.marker_offset = indent
        item.padding = padding
        self.first_of_item = True
        self.mark_prefix()

    # Tables (SPEC.md section 4.3).

    def try_table(self, para: Node) -> bool:
        rest = self.line[self.next_nonspace :]
        head = para.lines[-1]
        header = head.as_it_stands
        if ("\f" in rest or "\v" in rest or "\f" in header or "\v" in header) and (
            "-" in rest and not rest.strip("|:- \t\f\v")
        ):
            raise Refusal("ambiguous-table")
        cells = split_cells(rest)
        if not cells or not all(RE_DELIMITER_CELL.match(c) for c in cells):
            return False
        if header.strip(" \t") == "|":  # no cells at all
            return False
        head_cells = split_cells(header, keep_leading=head.lazy)
        if len(head_cells) != len(cells):
            return False
        if not has_unescaped_pipe(rest) or not has_unescaped_pipe(header):
            raise Refusal("ambiguous-table")
        if len(para.lines) > 1:
            raise Refusal("table-not-blank-above")
        siblings = para.parent.children  # type: ignore[union-attr]
        at = siblings.index(para)
        if at and siblings[at - 1].end == para.start - 1:
            raise Refusal("table-not-blank-above")
        para.type = "table"
        para.lines = []
        para.rows = [head_cells]
        para.level = len(head_cells)
        return True

    def table_line(self, table: Node) -> None:
        self.find_next_nonspace()
        rest = self.line[self.next_nonspace :]
        if (
            self.starts_block(table.parent)
            or not has_unescaped_pipe(rest)
            or rest.strip(" \t") == "|"
        ):
            raise Refusal("table-not-blank-below")
        width = table.level
        cells = split_cells(rest)[:width]
        table.rows.append(cells + [""] * (width - len(cells)))

    def starts_block(self, parent: Node | None) -> bool:
        rest = self.line[self.next_nonspace :]
        if self.indented:
            return True
        if rest[:1] == ">" or RE_ATX.match(rest) or RE_FENCE.match(rest):
            return True
        if rest[:1] == "<" and (any(r.match(rest) for r in RE_HTML_START) or RE_HTML_7.match(rest)):
            return True
        if RE_THEMATIC.match(rest):
            return True
        return self.match_list_marker(parent) is not None  # type: ignore[arg-type]

    def parse(self) -> Node:
        for index in range(self.first, len(self.spans)):
            self.incorporate(index)
        self.number = len(self.spans) + 1
        while self.tip is not None:
            self.finalize(self.tip, len(self.spans))
        return self.doc


def _assign(node: Node, path: tuple[int, ...]) -> None:
    node.path = path
    for i, child in enumerate(node.children):
        _assign(child, (*path, i))


@dataclass
class Leaf:
    node: Node
    type: str
    text: str
    kind: str


def _finish_leaf(node: Node, spans: list[tuple[int, int, str]]) -> None:
    if node.type == "code_block":
        text, srcs = "", []
        for ln in node.lines:
            text += ln.text + "\n"
            srcs += [*ln.srcs, spans[ln.number - 1][1]]
        node.content, node.srcs = text, srcs
    elif node.type == "table":
        node.content = node.rows


LEAF_TYPES = ("paragraph", "heading", "code_block", "html_block", "thematic_break", "table")


def walk(node: Node):
    yield node
    for child in node.children:
        yield from walk(child)


def table_text(rows: list[list[str]]) -> str:
    text = "\n".join(" | ".join(c.replace("|", "\\|") for c in row) for row in rows)
    return unicodedata.normalize("NFC", text)


def parse_document(text: str):
    """Parse `text` (after section 3's U+0000 replacement). Returns
    (doc node, frontmatter range or None, spans, line info); raises Refusal."""
    spans = split_lines(text)
    lines = [text[a:b] for a, b, _ in spans]
    for ln in lines:
        if CONFLICT.match(ln):
            raise Refusal("conflict-marker")
    fm = frontmatter_range(lines)
    parser = Parser(text, spans, fm[1] + 1 if fm else 0)
    doc = parser.parse()
    _assign(doc, ())
    for node in walk(doc):
        if node.type in LEAF_TYPES:
            _finish_leaf(node, spans)
        if node is not doc:
            while node.end > node.start and blank(lines[node.end - 1]):
                node.end -= 1
    return doc, fm, spans, parser.line_info
