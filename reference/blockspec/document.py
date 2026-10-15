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
narrower reading: a row with no unescaped pipe, or no cells, ends a table
(GFM would make it a row), and a header row with no pipe is a paragraph
(GitHub would make it a one-column table). Standard library only, and one
file on purpose: `conformance/run_cases.py --impl FILE` loads this file by
path, and so does the mutation gate, from a mutated copy of it.
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
_MARKER = re.compile(r"^<!--[ \t]*#([a-z0-9][a-z0-9-]*)(:begin|:end)?[ \t]*-->[ \t]*$")

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


def _split_row(text: str) -> list[str] | None:
    """A table row's cells as GFM splits them: on unescaped pipes, outer pipes
    dropped, each cell trimmed, `\\|` read as `|`. None when the row has no
    unescaped pipe at all."""
    row = text.strip(" \t")
    cells: list[str] = []
    cell: list[str] = []
    pipes = 0
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
            pipes += 1
            ends_with_pipe = True
        else:
            cell.append(c)
            ends_with_pipe = False
        i += 1
    cells.append("".join(cell))
    if not pipes:
        return None
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
            if self.blank or not _split_row(self.line[self.next_nonspace :]):
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
        A header row with no pipe is a one-column table to GitHub and a
        paragraph to pandoc and markdown-it. It stays a paragraph here, and is
        refused where the table-not-blank-above rule would refuse the table
        GitHub reads."""
        if self.indented or container.type != "paragraph":
            return 0
        delimiter = _split_row(self.line[self.next_nonspace :])
        if not delimiter or not all(_DELIMITER_CELL.match(cell) for cell in delimiter):
            return 0
        header_line, header_text = container.lines[-1]
        header = _split_row(header_text)
        github_only = header is None
        if github_only:
            header = [header_text.strip(" \t")]
        if len(header) != len(delimiter):
            return 0
        parent = container.parent
        if len(container.lines) > 1:
            raise Refusal("table-not-blank-above", "a table directly under a paragraph line")
        at = parent.children.index(container)
        if at and parent.children[at - 1].last_content == header_line - 1:
            raise Refusal("table-not-blank-above", "a table directly under a non-blank line")
        if github_only:
            return 0
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


def _slug(text: str) -> str:
    text = re.sub(r"[^\w\- ]", "", text.strip().lower())
    return text.replace(" ", "-")


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
        declared: list[tuple[str, dict]] = []
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
                    if i + 1 >= len(siblings):
                        raise Refusal("dangling-marker", f"#{name} has no next sibling")
                    declared.append((name, siblings[i + 1].ref()))
                elif form == ":begin":
                    if name in begun:
                        raise Refusal("duplicate-name", f"#{name} is declared twice")
                    begun[name] = i
                else:
                    if name not in begun:
                        raise Refusal("unpaired-region", f"#{name}:end has no :begin beside it")
                    first = begun.pop(name)
                    declared.append((name, {"region": [n.ref() for n in siblings[first + 1 : i]]}))
            if begun:
                name = next(iter(begun))
                raise Refusal("unpaired-region", f"#{name}:begin has no :end beside it")
        names: dict[str, dict] = {}
        for name, target in declared:
            if name in names:
                raise Refusal("duplicate-name", f"#{name} is declared twice")
            names[name] = target
        return names

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
