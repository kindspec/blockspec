# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Read a blockspec draft 0 document: refuse it, or return its structure.

Draft 0 is decided by `docs/adjudications/0001-syntax.md` and `0002-block.md`
(each section's *What draft 0 carries*, and 0002's frontmatter addendum). In
short: a pinned CommonMark 0.31.2 block-level profile with GFM pipe tables,
inline content opaque, region markers as the one convention, and a fixed list
of refusals.

The block parser is the line-by-line algorithm of CommonMark's reference
implementation (commonmark.js), cut down to the profile: every block the
profile refuses raises `Refusal` where it is recognised. GFM's table extension
is a block start tried after every core one, as cmark-gfm tries its
extensions. Where this reader and GFM part ways on tables, it takes the
narrower reading: a row with no unescaped pipe ends a table, where GFM would
make it a row, and a header row with no pipe over a one-cell delimiter row, a
table to GitHub alone, is refused. A row that is only `|` ends a table too, as
GitHub ends it. Standard library only, and one file on purpose:
`conformance/run_cases.py --impl FILE` loads this file by path, and so does
the mutation gate, from a mutated copy of it.
"""

from __future__ import annotations

import re
import string

__all__ = ["Document", "Refusal", "conform", "parse"]


class Refusal(Exception):
    """The document is not in the profile. `code` is one of the codes in
    `conformance/cases/case-body.schema.json`."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


LEAVES = ("paragraph", "heading", "code_block", "html_block", "thematic_break", "table")
CONTAINERS = ("document", "block_quote", "list", "list_item")

_PUNCT = frozenset(string.punctuation)
_WS = "[ \\t\\n\\v\\f\\r]"

# A git conflict-marker line: a column-0 run of seven or more `<`, `>` or `|`
# followed by a space or the end of the line, or seven or more `=` alone
# (conformance/cases/README.md, reading 14).
_CONFLICT = re.compile(r"^(?:(?:<{7,}|>{7,}|\|{7,})(?: |$)|={7,}$)")

# D8 section 7.2's region marker, in its two forms.
_MARKER = re.compile(r"^[ \t]*<!--[ \t]*#([a-z0-9][a-z0-9-]*)(:begin|:end)?[ \t]*-->[ \t]*$")

_ATX = re.compile(r"^#{1,6}(?:[ \t]+|$)")
_FENCE = re.compile(r"^`{3,}(?!.*`)|^~{3,}")
_CLOSING_FENCE = re.compile(r"^(?:`{3,}|~{3,})(?=[ \t]*$)")
_THEMATIC = re.compile(r"^(?:(?:\*[ \t]*){3,}|(?:_[ \t]*){3,}|(?:-[ \t]*){3,})$")
_SETEXT = re.compile(r"^(?:=+|-+)[ \t]*$")
_BULLET = re.compile(r"^[*+-]")
_ORDERED = re.compile(r"^(\d{1,9})([.)])")
_DELIMITER_CELL = re.compile(r"^:?-+:?$")

_TAGNAME = "[A-Za-z][A-Za-z0-9-]*"
_ATTRIBUTE = (
    f"(?:{_WS}+[a-zA-Z_:][a-zA-Z0-9_.:-]*"
    f"(?:{_WS}*={_WS}*(?:[^\"'=<>`\\x00-\\x20]+|'[^']*'|\"[^\"]*\"))?)"
)
_OPENTAG = f"<{_TAGNAME}{_ATTRIBUTE}*{_WS}*/?>"
_CLOSETAG = f"</{_TAGNAME}{_WS}*>"
_BLOCK_TAGS = (
    "address|article|aside|base|basefont|blockquote|body|caption|center|col|colgroup|dd|"
    "details|dialog|dir|div|dl|dt|fieldset|figcaption|figure|footer|form|frame|frameset|"
    "h[1-6]|head|header|hr|html|iframe|legend|li|link|main|menu|menuitem|nav|noframes|ol|"
    "optgroup|option|p|param|search|section|summary|table|tbody|td|tfoot|th|thead|title|"
    "tr|track|ul"
)
# CommonMark 0.31.2 section 4.6: the start conditions of HTML block types 1-7.
_HTML_OPEN = (
    re.compile(r"^<(?:pre|script|style|textarea)(?:[ \t>]|$)", re.I),
    re.compile(r"^<!--"),
    re.compile(r"^<\?"),
    re.compile(r"^<![A-Za-z]"),
    re.compile(r"^<!\[CDATA\["),
    re.compile(f"^</?(?:{_BLOCK_TAGS})(?:[ \\t]|/?>|$)", re.I),
    re.compile(f"^(?:{_OPENTAG}|{_CLOSETAG}){_WS}*$", re.I),
)


class Node:
    """One node of the CommonMark tree, with what the profile reports of it."""

    def __init__(self, kind: str, line: int) -> None:
        self.type = kind
        self.parent: Node | None = None
        self.children: list[Node] = []
        self.open = True
        self.start = line
        self.end = line
        #: The last line on which this node, or a node inside it, held a
        #: non-blank line. A table's neighbours are measured with it.
        self.last_content = line
        self.lines: list[tuple[int, str]] = []  # paragraph lines, code lines
        self.text = ""  # heading content, or an html_block's line
        self.rows: list[list[str]] = []  # table
        self.list_data: dict = {}
        self.fence = ("", 0, 0)  # character, length, indentation
        self.marker: tuple[str, str | None] | None = None
        self.path: tuple[int, ...] = ()

    def content(self) -> str | list[list[str]]:
        if self.type == "paragraph":
            return "\n".join(text for _, text in self.lines).rstrip(" \t")
        if self.type == "heading":
            return self.text
        if self.type == "code_block":
            return "".join(text + "\n" for _, text in self.lines)
        if self.type == "html_block":
            return self.text + "\n"
        if self.type == "table":
            width = len(self.rows[0])
            return [self.rows[0]] + [(row + [""] * width)[:width] for row in self.rows[1:]]
        return ""

    def ref(self) -> dict:
        return {"node": list(self.path), "type": self.type}


def _split_lines(text: str) -> list[str]:
    lines = re.split(r"\r\n|\r|\n", text)
    if lines and lines[-1] == "":
        lines.pop()
    return lines


def _blank(line: str) -> bool:
    return not line.strip(" \t")


def _has_pipe(text: str) -> bool:
    """Whether `text` holds a `|` that no backslash escapes."""
    return re.search(r"(?:^|[^\\])(?:\\\\)*\|", text) is not None


def _split_row(text: str) -> list[str]:
    """A table row's cells as GFM splits them: on unescaped pipes, outer pipes
    dropped, each cell trimmed, `\\|` read as `|`."""
    row = text.strip(" \t")
    cells: list[str] = []
    cell: list[str] = []
    ends_with_pipe = False
    i = 0
    while i < len(row):
        c = row[i]
        if c == "\\" and i + 1 < len(row):
            cell.append("|" if row[i + 1] == "|" else row[i : i + 2])
            i += 2
            ends_with_pipe = False
            continue
        if c == "|":
            cells.append("".join(cell))
            cell = []
            ends_with_pipe = True
        else:
            cell.append(c)
            ends_with_pipe = False
        i += 1
    cells.append("".join(cell))
    if row.startswith("|"):
        cells.pop(0)
    if ends_with_pipe and cells:
        cells.pop()
    return [cell.strip(" \t") for cell in cells]


def _link_reference_definition(text: str) -> bool:
    """Whether a paragraph's raw content opens with a link reference
    definition (CommonMark 0.31.2 section 4.7)."""
    n = len(text)
    if not text.startswith("["):
        return False
    j = 1
    while j < n:
        c = text[j]
        if c == "\\" and j + 1 < n and text[j + 1] in _PUNCT:
            j += 2
            continue
        if c == "[":
            return False
        if c == "]":
            break
        j += 1
    else:
        return False
    label = text[1:j]
    if len(label) > 999 or not label.strip(" \t\n"):
        return False
    j += 1
    if j >= n or text[j] != ":":
        return False
    j += 1
    while j < n and text[j] in " \t":
        j += 1
    if j < n and text[j] == "\n":
        j += 1
        while j < n and text[j] in " \t":
            j += 1
    if j >= n:
        return False
    k = j
    if text[k] == "<":
        k += 1
        while k < n:
            c = text[k]
            if c == "\\" and k + 1 < n and text[k + 1] in _PUNCT:
                k += 2
                continue
            if c in "\n<":
                return False
            if c == ">":
                break
            k += 1
        else:
            return False
        k += 1
    else:
        depth = 0
        while k < n:
            c = text[k]
            if c == "\\" and k + 1 < n and text[k + 1] in _PUNCT:
                k += 2
                continue
            if c == "(":
                depth += 1
            elif c == ")":
                if depth == 0:
                    break
                depth -= 1
            elif ord(c) <= 0x20 or c == "\x7f":
                break
            k += 1
        if k == j or depth:
            return False
    p = k
    while p < n and text[p] in " \t":
        p += 1
    destination_ends_its_line = p >= n or text[p] == "\n"
    q = p
    if q < n and text[q] == "\n":
        q += 1
        while q < n and text[q] in " \t":
            q += 1
    if q > k and q < n and text[q] in "\"'(":
        opener = text[q]
        closer = ")" if opener == "(" else opener
        r = q + 1
        while r < n:
            c = text[r]
            if c == "\\" and r + 1 < n and text[r + 1] in _PUNCT:
                r += 2
                continue
            if c == closer:
                r += 1
                while r < n and text[r] in " \t":
                    r += 1
                if r >= n or text[r] == "\n":
                    return True
                break
            if opener == "(" and c == "(":
                break
            r += 1
    return destination_ends_its_line


class _Parser:
    """commonmark.js's block parser, cut down to the profile."""

    def __init__(self) -> None:
        self.doc = Node("document", 1)
        self.tip = self.doc
        self.oldtip = self.doc
        self.last_matched = self.doc
        self.all_closed = True
        self.line = ""
        self.line_no = 0
        self.offset = 0
        self.column = 0
        self.next_nonspace = 0
        self.next_nonspace_column = 0
        self.indent = 0
        self.indented = False
        self.blank = False
        self.partially_consumed_tab = False

    # --- the cursor ---------------------------------------------------------

    def find_next_nonspace(self) -> None:
        i, cols = self.offset, self.column
        while i < len(self.line):
            c = self.line[i]
            if c == " ":
                i += 1
                cols += 1
            elif c == "\t":
                i += 1
                cols += 4 - cols % 4
            else:
                break
        self.blank = i >= len(self.line)
        self.next_nonspace = i
        self.next_nonspace_column = cols
        self.indent = cols - self.column
        self.indented = self.indent >= 4

    def advance_next_nonspace(self) -> None:
        self.offset = self.next_nonspace
        self.column = self.next_nonspace_column
        self.partially_consumed_tab = False

    def advance_offset(self, count: int, columns: bool) -> None:
        while count > 0 and self.offset < len(self.line):
            if self.line[self.offset] == "\t":
                to_tab = 4 - self.column % 4
                if columns:
                    self.partially_consumed_tab = to_tab > count
                    step = min(to_tab, count)
                    self.column += step
                    self.offset += 0 if self.partially_consumed_tab else 1
                    count -= step
                else:
                    self.partially_consumed_tab = False
                    self.column += to_tab
                    self.offset += 1
                    count -= 1
            else:
                self.partially_consumed_tab = False
                self.offset += 1
                self.column += 1
                count -= 1

    def peek(self, at: int) -> str:
        return self.line[at] if at < len(self.line) else ""

    def rest(self) -> str:
        """The rest of the line from the offset, a partly consumed tab
        counting as the spaces it has left."""
        prefix = ""
        if self.partially_consumed_tab:
            self.offset += 1
            prefix = " " * (4 - self.column % 4)
        return prefix + self.line[self.offset :]

    # --- the tree -----------------------------------------------------------

    def add_child(self, kind: str) -> Node:
        allowed = {
            "document": lambda t: t != "list_item",
            "block_quote": lambda t: t != "list_item",
            "list_item": lambda t: t != "list_item",
            "list": lambda t: t == "list_item",
        }
        while not allowed.get(self.tip.type, lambda t: False)(kind):
            self.finalize(self.tip, self.line_no - 1)
        node = Node(kind, self.line_no)
        node.parent = self.tip
        self.tip.children.append(node)
        self.tip = node
        return node

    def finalize(self, node: Node, line: int) -> None:
        node.open = False
        node.end = line
        if node.type == "paragraph" and _link_reference_definition(node.content()):
            raise Refusal("link-reference-definition", "a link reference definition")
        self.tip = node.parent

    def close_unmatched(self) -> None:
        if not self.all_closed:
            while self.oldtip is not self.last_matched:
                parent = self.oldtip.parent
                self.finalize(self.oldtip, self.line_no - 1)
                self.oldtip = parent
            self.all_closed = True

    def touch(self, node: Node | None) -> None:
        while node is not None:
            node.last_content = self.line_no
            node = node.parent

    # --- continuation: 0 matched, 1 not matched, 2 line consumed ------------

    def proceed(self, node: Node) -> int:
        kind = node.type
        if kind == "block_quote":
            if not self.indented and self.peek(self.next_nonspace) == ">":
                self.advance_next_nonspace()
                self.advance_offset(1, False)
                if self.peek(self.offset) in (" ", "\t"):
                    self.advance_offset(1, True)
                return 0
            return 1
        if kind == "list_item":
            data = node.list_data
            if self.blank:
                if not node.children:
                    return 1
                self.advance_next_nonspace()
            elif self.indent >= data["offset"] + data["padding"]:
                self.advance_offset(data["offset"] + data["padding"], True)
            else:
                return 1
            return 0
        if kind == "list":
            return 0
        if kind == "code_block":
            char, length, indent = node.fence
            closing = self.indent <= 3 and self.peek(self.next_nonspace) == char
            match = closing and _CLOSING_FENCE.match(self.line[self.next_nonspace :])
            if match and len(match.group()) >= length:
                self.finalize(node, self.line_no)
                return 2
            while indent > 0 and self.peek(self.offset) in (" ", "\t"):
                self.advance_offset(1, True)
                indent -= 1
            return 0
        if kind == "paragraph":
            return 1 if self.blank else 0
        if kind == "table":
            row = self.line[self.next_nonspace :]
            if self.blank or not _has_pipe(row) or not _split_row(row):
                return 1
            return 0
        return 1

    # --- block starts: 0 none, 1 container, 2 leaf, 3 line consumed --------

    def block_quote(self, container: Node) -> int:
        if self.indented or self.peek(self.next_nonspace) != ">":
            return 0
        self.advance_next_nonspace()
        self.advance_offset(1, False)
        if self.peek(self.offset) in (" ", "\t"):
            self.advance_offset(1, True)
        self.close_unmatched()
        self.add_child("block_quote")
        return 1

    def atx_heading(self, container: Node) -> int:
        match = None if self.indented else _ATX.match(self.line[self.next_nonspace :])
        if not match:
            return 0
        self.advance_next_nonspace()
        self.advance_offset(len(match.group()), False)
        self.close_unmatched()
        node = self.add_child("heading")
        text = re.sub(r"^[ \t]*#+[ \t]*$", "", self.line[self.offset :])
        node.text = re.sub(r"[ \t]+#+[ \t]*$", "", text).strip(" \t")
        self.finalize(node, self.line_no)
        return 3

    def fenced_code(self, container: Node) -> int:
        match = None if self.indented else _FENCE.match(self.line[self.next_nonspace :])
        if not match:
            return 0
        self.close_unmatched()
        node = self.add_child("code_block")
        node.fence = (match.group()[0], len(match.group()), self.indent)
        return 3

    def html_block(self, container: Node) -> int:
        if self.indented or self.peek(self.next_nonspace) != "<":
            return 0
        text = self.line[self.next_nonspace :]
        for kind, pattern in enumerate(_HTML_OPEN, 1):
            if not pattern.match(text):
                continue
            if kind == 7 and (
                container.type == "paragraph"
                or (not self.all_closed and not self.blank and self.tip.type == "paragraph")
            ):
                continue
            marker = _MARKER.match(text) if kind == 2 else None
            if marker is None:
                raise Refusal("raw-html", "an HTML block that is not a region marker")
            self.close_unmatched()
            node = self.add_child("html_block")
            node.text = self.rest()
            node.marker = (marker.group(1), marker.group(2))
            self.finalize(node, self.line_no)
            return 3
        return 0

    def setext_heading(self, container: Node) -> int:
        if self.indented or container.type != "paragraph":
            return 0
        if not _SETEXT.match(self.line[self.next_nonspace :]):
            return 0
        if _link_reference_definition(container.content()):
            raise Refusal("link-reference-definition", "a link reference definition")
        raise Refusal("setext-heading", "a setext heading")

    def table(self, container: Node) -> int:
        """GFM's table extension: a delimiter row under a paragraph line whose
        cells it matches makes that line a table's header row.

        Tried after every core block start, as cmark-gfm tries its extensions,
        so `- | -` under a paragraph line is a list item, not a delimiter row.
        A header row with no pipe over a one-cell delimiter row is a
        one-column table to GitHub and a paragraph to pandoc and markdown-it,
        and is refused as ambiguous-table (0002, addendum on ambiguous
        tables)."""
        if self.indented or container.type != "paragraph":
            return 0
        delimiter_text = self.line[self.next_nonspace :]
        delimiter = _split_row(delimiter_text)
        if not _has_pipe(delimiter_text) or not all(
            _DELIMITER_CELL.match(cell) for cell in delimiter
        ):
            return 0
        header_line, header_text = container.lines[-1]
        if not _has_pipe(header_text):
            if len(delimiter) == 1:
                raise Refusal(
                    "ambiguous-table",
                    "a header row with no pipe over a delimiter row: a table to GitHub, "
                    "a paragraph to pandoc and markdown-it",
                )
            return 0
        header = _split_row(header_text)
        if len(header) != len(delimiter):
            return 0
        parent = container.parent
        if len(container.lines) > 1:
            raise Refusal("table-not-blank-above", "a table directly under a paragraph line")
        at = parent.children.index(container)
        if at and parent.children[at - 1].last_content == header_line - 1:
            raise Refusal("table-not-blank-above", "a table directly under a non-blank line")
        parent.children.pop(at)
        self.tip = parent
        node = self.add_child("table")
        node.start = header_line
        node.rows = [header]
        self.advance_offset(len(self.line) - self.offset, False)
        return 3

    def thematic_break(self, container: Node) -> int:
        if self.indented or not _THEMATIC.match(self.line[self.next_nonspace :]):
            return 0
        self.close_unmatched()
        node = self.add_child("thematic_break")
        self.finalize(node, self.line_no)
        return 3

    def list_item(self, container: Node) -> int:
        if self.indented and container.type != "list":
            return 0
        data = self.list_marker(container)
        if data is None:
            return 0
        self.close_unmatched()
        if self.tip.type != "list" or not all(
            self.tip.list_data[key] == data[key] for key in ("kind", "bullet", "delimiter")
        ):
            self.add_child("list").list_data = data
        self.add_child("list_item").list_data = data
        return 1

    def list_marker(self, container: Node) -> dict | None:
        if self.indent >= 4:
            return None
        rest = self.line[self.next_nonspace :]
        data = {"kind": "", "bullet": "", "delimiter": "", "offset": self.indent, "padding": 0}
        bullet = _BULLET.match(rest)
        ordered = _ORDERED.match(rest)
        if bullet:
            match = bullet
            data["kind"], data["bullet"] = "bullet", bullet.group()
        elif ordered and (container.type != "paragraph" or int(ordered.group(1)) == 1):
            match = ordered
            data["kind"], data["delimiter"] = "ordered", ordered.group(2)
        else:
            return None
        width = len(match.group())
        if self.peek(self.next_nonspace + width) not in ("", " ", "\t"):
            return None
        if container.type == "paragraph" and _blank(self.line[self.next_nonspace + width :]):
            return None
        self.advance_next_nonspace()
        self.advance_offset(width, True)
        start_column, start_offset = self.column, self.offset
        while True:
            self.advance_offset(1, True)
            nxt = self.peek(self.offset)
            if not (self.column - start_column < 5 and nxt in (" ", "\t")):
                break
        blank_item = self.peek(self.offset) == ""
        spaces = self.column - start_column
        if spaces >= 5 or spaces < 1 or blank_item:
            data["padding"] = width + 1
            self.column, self.offset = start_column, start_offset
            if self.peek(self.offset) in (" ", "\t"):
                self.advance_offset(1, True)
        else:
            data["padding"] = width + spaces
        return data

    def indented_code(self, container: Node) -> int:
        if self.indented and self.tip.type != "paragraph" and not self.blank:
            raise Refusal("indented-code", "an indented code block")
        return 0

    # --- one line -----------------------------------------------------------

    def incorporate(self, line: str, line_no: int) -> None:
        self.line, self.line_no = line, line_no
        self.offset = self.column = 0
        self.blank = self.partially_consumed_tab = False
        self.oldtip = self.tip
        container = self.doc
        while container.children and container.children[-1].open:
            container = container.children[-1]
            self.find_next_nonspace()
            outcome = self.proceed(container)
            if outcome == 2:
                self.touch(container)
                return
            if outcome == 1:
                container = container.parent
                break
        self.all_closed = container is self.oldtip
        self.last_matched = container
        starts = (
            self.block_quote,
            self.atx_heading,
            self.fenced_code,
            self.html_block,
            self.setext_heading,
            self.thematic_break,
            self.list_item,
            self.indented_code,
            self.table,
        )
        leaf = container.type == "code_block"
        while not leaf:
            self.find_next_nonspace()
            for start in starts:
                outcome = start(container)
                if outcome:
                    break
            else:
                self.advance_next_nonspace()
                break
            container = self.tip
            if outcome == 3:
                self.touch(self.tip)
                return
            leaf = outcome == 2
        if not self.all_closed and not self.blank and self.tip.type == "paragraph":
            self.tip.lines.append((line_no, self.rest()))
        else:
            self.close_unmatched()
            if container.type in ("paragraph", "code_block"):
                container.lines.append((line_no, self.rest()))
            elif container.type == "table":
                container.rows.append(_split_row(self.line[self.next_nonspace :]))
            elif self.offset < len(line) and not self.blank:
                node = self.add_child("paragraph")
                self.advance_next_nonspace()
                node.lines.append((line_no, self.rest()))
        if not _blank(line):
            self.touch(self.tip)

    def finish(self, last_line: int) -> Node:
        self.line_no = last_line + 1
        while self.tip is not None:
            self.finalize(self.tip, last_line)
        return self.doc


#: github-slugger 2.0.0's removed characters, as hex code point ranges. Generated
#: from its regex.js by evaluating the regex on every code point with node, so
#: it matches code point for code point rather than by reading the class.
_SLUG_REMOVED_RANGES = (
    "0-1f 21-2c 2e-2f 3a-40 5b-5e 60 7b-a9 ab-b4 b6-b9 bb-bf d7 f7 2c2-2c5 2d2-2df 2e5-2eb "
    "2ed 2ef-2ff 375 378-379 37e 380-385 387 38b 38d 3a2 3f6 482 530 557-558 55a-55f 589-590 "
    "5be 5c0 5c3 5c6 5c8-5cf 5eb-5ee 5f3-60f 61b-61f 66a-66d 6d4 6dd-6de 6e9 6fd-6fe 700-70f "
    "74b-74c 7b2-7bf 7f6-7f9 7fb-7fc 7fe-7ff 82e-83f 85c-85f 86b-89f 8b5 8c8-8d2 8e2 964-965 "
    "970 984 98d-98e 991-992 9a9 9b1 9b3-9b5 9ba-9bb 9c5-9c6 9c9-9ca 9cf-9d6 9d8-9db 9de "
    "9e4-9e5 9f2-9fb 9fd 9ff-a00 a04 a0b-a0e a11-a12 a29 a31 a34 a37 a3a-a3b a3d a43-a46 "
    "a49-a4a a4e-a50 a52-a58 a5d a5f-a65 a76-a80 a84 a8e a92 aa9 ab1 ab4 aba-abb ac6 aca "
    "ace-acf ad1-adf ae4-ae5 af0-af8 b00 b04 b0d-b0e b11-b12 b29 b31 b34 b3a-b3b b45-b46 "
    "b49-b4a b4e-b54 b58-b5b b5e b64-b65 b70 b72-b81 b84 b8b-b8d b91 b96-b98 b9b b9d ba0-ba2 "
    "ba5-ba7 bab-bad bba-bbd bc3-bc5 bc9 bce-bcf bd1-bd6 bd8-be5 bf0-bff c0d c11 c29 c3a-c3c "
    "c45 c49 c4e-c54 c57 c5b-c5f c64-c65 c70-c7f c84 c8d c91 ca9 cb4 cba-cbb cc5 cc9 cce-cd4 "
    "cd7-cdd cdf ce4-ce5 cf0 cf3-cff d0d d11 d45 d49 d4f-d53 d58-d5e d64-d65 d70-d79 d80 d84 "
    "d97-d99 db2 dbc dbe-dbf dc7-dc9 dcb-dce dd5 dd7 de0-de5 df0-df1 df4-e00 e3b-e3f e4f "
    "e5a-e80 e83 e85 e8b ea4 ea6 ebe-ebf ec5 ec7 ece-ecf eda-edb ee0-eff f01-f17 f1a-f1f "
    "f2a-f34 f36 f38 f3a-f3d f48 f6d-f70 f85 f98 fbd-fc5 fc7-fff 104a-104f 109e-109f 10c6 "
    "10c8-10cc 10ce-10cf 10fb 1249 124e-124f 1257 1259 125e-125f 1289 128e-128f 12b1 "
    "12b6-12b7 12bf 12c1 12c6-12c7 12d7 1311 1316-1317 135b-135c 1360-137f 1390-139f "
    "13f6-13f7 13fe-1400 166d-166e 1680 169b-169f 16eb-16ed 16f9-16ff 170d 1715-171f "
    "1735-173f 1754-175f 176d 1771 1774-177f 17d4-17d6 17d8-17db 17de-17df 17ea-180a "
    "180e-180f 181a-181f 1879-187f 18ab-18af 18f6-18ff 191f 192c-192f 193c-1945 196e-196f "
    "1975-197f 19ac-19af 19ca-19cf 19da-19ff 1a1c-1a1f 1a5f 1a7d-1a7e 1a8a-1a8f 1a9a-1aa6 "
    "1aa8-1aaf 1ac1-1aff 1b4c-1b4f 1b5a-1b6a 1b74-1b7f 1bf4-1bff 1c38-1c3f 1c4a-1c4c "
    "1c7e-1c7f 1c89-1c8f 1cbb-1cbc 1cc0-1ccf 1cd3 1cfb-1cff 1dfa 1f16-1f17 1f1e-1f1f "
    "1f46-1f47 1f4e-1f4f 1f58 1f5a 1f5c 1f5e 1f7e-1f7f 1fb5 1fbd 1fbf-1fc1 1fc5 1fcd-1fcf "
    "1fd4-1fd5 1fdc-1fdf 1fed-1ff1 1ff5 1ffd-203e 2041-2053 2055-2070 2072-207e 2080-208f "
    "209d-20cf 20f1-2101 2103-2106 2108-2109 2114 2116-2118 211e-2123 2125 2127 2129 212e "
    "213a-213b 2140-2144 214a-214d 214f-215f 2189-24b5 24ea-2bff 2c2f 2c5f 2ce5-2cea "
    "2cf4-2cff 2d26 2d28-2d2c 2d2e-2d2f 2d68-2d6e 2d70-2d7e 2d97-2d9f 2da7 2daf 2db7 2dbf "
    "2dc7 2dcf 2dd7 2ddf 2e00-2e2e 2e30-3004 3008-3020 3030 3036-3037 303d-3040 3097-3098 "
    "309b-309c 30a0 30fb 3100-3104 3130 318f-319f 31c0-31ef 3200-33ff 4dc0-4dff 9ffd-9fff "
    "a48d-a4cf a4fe-a4ff a60d-a60f a62c-a63f a673 a67e a6f2-a716 a720-a721 a789-a78a "
    "a7c0-a7c1 a7cb-a7f4 a828-a82b a82d-a83f a874-a87f a8c6-a8cf a8da-a8df a8f8-a8fa a8fc "
    "a92e-a92f a954-a95f a97d-a97f a9c1-a9ce a9da-a9df a9ff aa37-aa3f aa4e-aa4f aa5a-aa5f "
    "aa77-aa79 aac3-aada aade-aadf aaf0-aaf1 aaf7-ab00 ab07-ab08 ab0f-ab10 ab17-ab1f ab27 "
    "ab2f ab5b ab6a-ab6f abeb abee-abef abfa-abff d7a4-d7af d7c7-d7ca d7fc-d7ff e000-f8ff "
    "fa6e-fa6f fada-faff fb07-fb12 fb18-fb1c fb29 fb37 fb3d fb3f fb42 fb45 fbb2-fbd2 "
    "fd3e-fd4f fd90-fd91 fdc8-fdef fdfc-fdff fe10-fe1f fe30-fe32 fe35-fe4c fe50-fe6f fe75 "
    "fefd-ff0f ff1a-ff20 ff3b-ff3e ff40 ff5b-ff65 ffbf-ffc1 ffc8-ffc9 ffd0-ffd1 ffd8-ffd9 "
    "ffdd-ffff 1000c 10027 1003b 1003e 1004e-1004f 1005e-1007f 100fb-1013f 10175-101fc "
    "101fe-1027f 1029d-1029f 102d1-102df 102e1-102ff 10320-1032c 1034b-1034f 1037b-1037f "
    "1039e-1039f 103c4-103c7 103d0 103d6-103ff 1049e-1049f 104aa-104af 104d4-104d7 "
    "104fc-104ff 10528-1052f 10564-105ff 10737-1073f 10756-1075f 10768-107ff 10806-10807 "
    "10809 10836 10839-1083b 1083d-1083e 10856-1085f 10877-1087f 1089f-108df 108f3 "
    "108f6-108ff 10916-1091f 1093a-1097f 109b8-109bd 109c0-109ff 10a04 10a07-10a0b 10a14 "
    "10a18 10a36-10a37 10a3b-10a3e 10a40-10a5f 10a7d-10a7f 10a9d-10abf 10ac8 10ae7-10aff "
    "10b36-10b3f 10b56-10b5f 10b73-10b7f 10b92-10bff 10c49-10c7f 10cb3-10cbf 10cf3-10cff "
    "10d28-10d2f 10d3a-10e7f 10eaa 10ead-10eaf 10eb2-10eff 10f1d-10f26 10f28-10f2f "
    "10f51-10faf 10fc5-10fdf 10ff7-10fff 11047-11065 11070-1107e 110bb-110cf 110e9-110ef "
    "110fa-110ff 11135 11140-11143 11148-1114f 11174-11175 11177-1117f 111c5-111c8 111cd "
    "111db 111dd-111ff 11212 11238-1123d 1123f-1127f 11287 11289 1128e 1129e 112a9-112af "
    "112eb-112ef 112fa-112ff 11304 1130d-1130e 11311-11312 11329 11331 11334 1133a "
    "11345-11346 11349-1134a 1134e-1134f 11351-11356 11358-1135c 11364-11365 1136d-1136f "
    "11375-113ff 1144b-1144f 1145a-1145d 11462-1147f 114c6 114c8-114cf 114da-1157f "
    "115b6-115b7 115c1-115d7 115de-115ff 11641-11643 11645-1164f 1165a-1167f 116b9-116bf "
    "116ca-116ff 1171b-1171c 1172c-1172f 1173a-117ff 1183b-1189f 118ea-118fe 11907-11908 "
    "1190a-1190b 11914 11917 11936 11939-1193a 11944-1194f 1195a-1199f 119a8-119a9 "
    "119d8-119d9 119e2 119e5-119ff 11a3f-11a46 11a48-11a4f 11a9a-11a9c 11a9e-11abf "
    "11af9-11bff 11c09 11c37 11c41-11c4f 11c5a-11c71 11c90-11c91 11ca8 11cb7-11cff 11d07 "
    "11d0a 11d37-11d39 11d3b 11d3e 11d48-11d4f 11d5a-11d5f 11d66 11d69 11d8f 11d92 "
    "11d99-11d9f 11daa-11edf 11ef7-11faf 11fb1-11fff 1239a-123ff 1246f-1247f 12544-12fff "
    "1342f-143ff 14647-167ff 16a39-16a3f 16a5f 16a6a-16acf 16aee-16aef 16af5-16aff "
    "16b37-16b3f 16b44-16b4f 16b5a-16b62 16b78-16b7c 16b90-16e3f 16e80-16eff 16f4b-16f4e "
    "16f88-16f8e 16fa0-16fdf 16fe2 16fe5-16fef 16ff2-16fff 187f8-187ff 18cd6-18cff "
    "18d09-1afff 1b11f-1b14f 1b153-1b163 1b168-1b16f 1b2fc-1bbff 1bc6b-1bc6f 1bc7d-1bc7f "
    "1bc89-1bc8f 1bc9a-1bc9c 1bc9f-1d164 1d16a-1d16c 1d173-1d17a 1d183-1d184 1d18c-1d1a9 "
    "1d1ae-1d241 1d245-1d3ff 1d455 1d49d 1d4a0-1d4a1 1d4a3-1d4a4 1d4a7-1d4a8 1d4ad 1d4ba "
    "1d4bc 1d4c4 1d506 1d50b-1d50c 1d515 1d51d 1d53a 1d53f 1d545 1d547-1d549 1d551 "
    "1d6a6-1d6a7 1d6c1 1d6db 1d6fb 1d715 1d735 1d74f 1d76f 1d789 1d7a9 1d7c3 1d7cc-1d7cd "
    "1d800-1d9ff 1da37-1da3a 1da6d-1da74 1da76-1da83 1da85-1da9a 1daa0 1dab0-1dfff 1e007 "
    "1e019-1e01a 1e022 1e025 1e02b-1e0ff 1e12d-1e12f 1e13e-1e13f 1e14a-1e14d 1e14f-1e2bf "
    "1e2fa-1e7ff 1e8c5-1e8cf 1e8d7-1e8ff 1e94c-1e94f 1e95a-1edff 1ee04 1ee20 1ee23 "
    "1ee25-1ee26 1ee28 1ee33 1ee38 1ee3a 1ee3c-1ee41 1ee43-1ee46 1ee48 1ee4a 1ee4c 1ee50 "
    "1ee53 1ee55-1ee56 1ee58 1ee5a 1ee5c 1ee5e 1ee60 1ee63 1ee65-1ee66 1ee6b 1ee73 1ee78 "
    "1ee7d 1ee7f 1ee8a 1ee9c-1eea0 1eea4 1eeaa 1eebc-1f12f 1f14a-1f14f 1f16a-1f16f "
    "1f18a-1fbef 1fbfa-1ffff 2a6de-2a6ff 2b735-2b73f 2b81e-2b81f 2cea2-2ceaf 2ebe1-2f7ff "
    "2fa1e-2ffff 3134b-e00ff e01f0-10ffff"
)
_SLUG_REMOVED = re.compile(
    "["
    + "".join(
        f"\\U{int(lo, 16):08x}-\\U{int(hi or lo, 16):08x}"
        for lo, _, hi in (span.partition("-") for span in _SLUG_REMOVED_RANGES.split())
    )
    + "]"
)
#: A heading whose content holds one of these carries inline markup, and has
#: no slug (0001, addendum on the marker line and heading slugs).
_INLINE_MARKUP = frozenset("*_`[<")


def _slug(text: str) -> str | None:
    """GitHub's heading slug, as github-slugger 2.0.0 computes it from the
    heading's raw content: lower-cased, its removed characters dropped, each
    space turned into `-`. None for a heading whose content holds an
    inline-markup character, whose rendered text the raw content is not."""
    if _INLINE_MARKUP.intersection(text):
        return None
    return _SLUG_REMOVED.sub("", text.lower()).replace(" ", "-")


class Document:
    """An accepted document: its frontmatter, blocks, leaves and names."""

    def __init__(self, root: Node, lines: list[str], frontmatter: list[int] | None) -> None:
        self.root = root
        self.frontmatter = frontmatter
        self.blocks = []
        for node in root.children:
            end = node.end
            while end > node.start and _blank(lines[end - 1]):
                end -= 1
            self.blocks.append({"type": node.type, "lines": [node.start, end]})
        self.nodes = list(self._walk(root, ()))
        self.leaves = [
            {"node": list(node.path), "type": node.type, "content": node.content()}
            for node in self.nodes
            if node.type in LEAVES
        ]
        self.names = self._names()

    def _walk(self, node: Node, path: tuple[int, ...]):
        for i, child in enumerate(node.children):
            child.path = (*path, i)
            yield child
            yield from self._walk(child, child.path)

    def _names(self) -> dict[str, dict]:
        """What each marker names. Every problem is collected first, so that
        when several refusals apply the one reported does not depend on
        document order: duplicate-name, then unpaired-region, then
        dangling-marker (0002, addendum on markers that name nothing). A name is declared by a
        one-line marker or a `:begin`; an `:end` only closes one."""
        declared: dict[str, list[dict]] = {}
        unpaired: list[str] = []
        dangling: list[str] = []
        for container in [self.root, *self.nodes]:
            if container.type not in ("document", "block_quote", "list_item"):
                continue
            siblings = container.children
            begun: dict[str, int] = {}
            for i, node in enumerate(siblings):
                if node.marker is None:
                    continue
                name, form = node.marker
                if form is None:
                    target = siblings[i + 1] if i + 1 < len(siblings) else None
                    if target is None or target.marker is not None:
                        dangling.append(f"#{name} names no node")
                    else:
                        declared.setdefault(name, []).append(target.ref())
                elif form == ":begin":
                    declared.setdefault(name, []).append({})
                    begun.setdefault(name, i)
                elif name in begun:
                    first = begun.pop(name)
                    region = [n.ref() for n in siblings[first + 1 : i]]
                    if not region:
                        dangling.append(f"#{name}:begin and #{name}:end name no node")
                    declared[name][declared[name].index({})] = {"region": region}
                else:
                    unpaired.append(f"#{name}:end has no :begin beside it")
            unpaired += [f"#{name}:begin has no :end beside it" for name in begun]
        for name, targets in declared.items():
            if len(targets) > 1:
                raise Refusal("duplicate-name", f"#{name} is declared twice")
        if unpaired:
            raise Refusal("unpaired-region", unpaired[0])
        if dangling:
            raise Refusal("dangling-marker", dangling[0])
        return {name: targets[0] for name, targets in declared.items()}

    def resolve(self, name: str) -> dict | str:
        """Markers first, then heading slugs. Zero or several matches is
        `#REF!(name)`."""
        if name in self.names:
            return self.names[name]
        headings = [n for n in self.nodes if n.type == "heading" and _slug(n.text) == name]
        if len(headings) == 1:
            return headings[0].ref()
        return f"#REF!({name})"


def parse(text: str) -> Document:
    """Read `text` as a blockspec document, or raise `Refusal`."""
    lines = _split_lines(text)
    for line in lines:
        if _CONFLICT.match(line):
            raise Refusal("conflict-marker", "a git conflict-marker line")
    frontmatter = None
    first = 0
    if len(lines) > 1 and lines[0] == "---" and not _blank(lines[1]):
        for at in range(1, len(lines)):
            if lines[at] == "---":
                frontmatter = [1, at + 1]
                first = at + 1
                break
    parser = _Parser()
    for at in range(first, len(lines)):
        parser.incorporate(lines[at], at + 1)
    root = parser.finish(len(lines))
    for node in _tables(root):
        siblings = node.parent.children
        at = siblings.index(node)
        if at + 1 < len(siblings) and siblings[at + 1].start == node.end + 1:
            raise Refusal("table-not-blank-below", "a table directly above a non-blank line")
    return Document(root, lines, frontmatter)


def _tables(node: Node):
    for child in node.children:
        if child.type == "table":
            yield child
        yield from _tables(child)


def conform(text: str, queries: list[str]) -> dict:
    """The interface `conformance/run_cases.py --impl FILE` calls."""
    try:
        doc = parse(text)
    except Refusal as refusal:
        return {"accept": False, "refusal": refusal.code, "message": refusal.message}
    return {
        "accept": True,
        "frontmatter": doc.frontmatter,
        "blocks": doc.blocks,
        "leaves": doc.leaves,
        "names": doc.names,
        "resolve": {name: doc.resolve(name) for name in queries},
    }
