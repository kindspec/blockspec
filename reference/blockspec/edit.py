# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Edit a blockspec document one block at a time: `docs/editing-api.md`.

Three operations, each text in and text out: replace a block, insert one
beside a block, delete a block. A block is a top-level node (SPEC.md section
6.1), named by its node path `[i]`. Every function changes only the lines its
operation is about, reads the result back with the reader, and refuses rather
than return a document whose other blocks or names read differently. Nothing
here reads or writes a `<doc>.notes/` record.
"""

from __future__ import annotations

import re

from .document import Document, Refusal, parse

__all__ = ["EditRefused", "REASONS", "delete_block", "insert_block", "replace_block"]

#: The API's own refusal reasons, none spelled like a SPEC.md section 9 code.
REASONS = (
    "bad-position",
    "no-such-block",
    "nested-node",
    "not-one-block",
    "changes-another-block",
    "rebinds-name",
)


class EditRefused(Refusal):
    """An edit refused for a reason of the API's own, in `code`."""


def _lines(text: str) -> list[list[str]]:
    """[body, line ending] per line, split as the reader splits lines."""
    out = []
    for match in re.finditer(r"([^\r\n]*)(\r\n|\r|\n|$)", text):
        if match.start() == len(text) and (not out or out[-1][1]):
            break
        out.append([match.group(1), match.group(2)])
        if not match.group(2):
            break
    return out


def _join(lines: list[list[str]]) -> str:
    return "".join(body + eol for body, eol in lines)


def _blank(body: str) -> bool:
    return not body.strip(" \t")


def _eol(lines: list[list[str]], at: int) -> str:
    """The line ending a new line at index `at` takes (editing-api.md, *Where
    the lines go*)."""
    if at > 0 and lines[at - 1][1]:
        return lines[at - 1][1]
    return next((eol for _, eol in lines if eol), "\n")


def _check_types(text, node=None, source=None) -> None:
    if not isinstance(text, str):
        raise TypeError(f"text must be a str, not {type(text).__name__}")
    if source is not None and not isinstance(source, str):
        raise TypeError(f"source must be a str, not {type(source).__name__}")
    if node is not None and not (
        isinstance(node, list | tuple)
        and all(isinstance(i, int) and not isinstance(i, bool) for i in node)
    ):
        raise TypeError("a node path must be a list or tuple of ints")


def _block(doc: Document, node) -> int:
    """The index of the block `node` names, or a refusal."""
    path = list(node)
    if len(path) == 1 and 0 <= path[0] < len(doc.blocks):
        return path[0]
    at = doc.root
    for i in path:
        if not 0 <= i < len(at.children):
            at = None
            break
        at = at.children[i]
    if len(path) > 1 and at is not None:
        raise EditRefused("nested-node", f"{path} is a node inside block [{path[0]}]")
    raise EditRefused("no-such-block", f"{path} names no block of the document")


def _source_lines(source: str) -> list[str]:
    lines = [body for body, _ in _lines(source)]
    if not lines:
        raise EditRefused("not-one-block", "the source is empty")
    return lines


def _declared(doc: Document, block: int | None) -> set[str]:
    """The names markers in block `block` declare."""
    if block is None:
        return set()
    return {
        node.marker[0]
        for node in doc.nodes
        if node.marker is not None and node.path[0] == block and node.marker[1] != ":end"
    }


def _by_block(doc: Document) -> dict[int, list]:
    out: dict[int, list] = {}
    for leaf in doc.leaves:
        out.setdefault(leaf["node"][0], []).append(
            (leaf["node"][1:], leaf["type"], leaf["content"])
        )
    return out


def _move(target: dict, mapping) -> dict | None:
    if "region" in target:
        region = [_move(n, mapping) for n in target["region"]]
        return {"region": [n for n in region if n is not None]}
    first = mapping(target["node"][0])
    if first is None:
        return None
    return {"node": [first, *target["node"][1:]], "type": target["type"]}


def _read_back(old: Document, text: str, edited: int | None, new: int | None, span, mapping) -> str:
    """Refuse `text` unless it reads as `old` with the edit applied: block
    `edited` of `old` replaced or removed, block `new` of the result made of
    exactly the lines `span`, and every other block and name as it was."""
    doc = parse(text)
    if new is not None:
        if new >= len(doc.blocks) or doc.blocks[new]["lines"] != list(span):
            raise EditRefused("not-one-block", "the new lines do not read as one block")
    expected = len(old.blocks) + (new is not None) - (edited is not None)
    if len(doc.blocks) != expected or doc.frontmatter != old.frontmatter:
        raise EditRefused("changes-another-block", "the document's blocks would change")
    before, after = _by_block(old), _by_block(doc)
    for j, block in enumerate(old.blocks):
        if j == edited:
            continue
        k = mapping(j)
        got = doc.blocks[k]
        if (
            got["type"] != block["type"]
            or got["lines"][1] - got["lines"][0] != block["lines"][1] - block["lines"][0]
            or after.get(k, []) != before.get(j, [])
        ):
            raise EditRefused("changes-another-block", f"block [{j}] would read differently")
    gone, added = _declared(old, edited), _declared(doc, new)
    want = {n: _move(t, mapping) for n, t in old.names.items() if n not in gone}
    got = {}
    for name, target in doc.names.items():
        if name in added:
            continue
        if "region" in target and new is not None:
            target = {"region": [n for n in target["region"] if n["node"] != [new]]}
        got[name] = target
    if want != got:
        moved = sorted(n for n in set(want) | set(got) if want.get(n) != got.get(n))
        raise EditRefused("rebinds-name", f"#{moved[0]} would bind to something else")
    return text


def replace_block(text: str, node, source: str, /) -> str:
    """Replace block `node`'s lines with `source`'s. The diff is the block."""
    _check_types(text, node, source)
    doc = parse(text)
    i = _block(doc, node)
    new = _source_lines(source)
    lines = _lines(text)
    first, last = doc.blocks[i]["lines"]
    if [body for body, _ in lines[first - 1 : last]] == new:
        return text
    eol = _eol(lines, first - 1)
    lines[first - 1 : last] = [[b, eol] for b in new[:-1]] + [[new[-1], lines[last - 1][1]]]
    span = (first, first + len(new) - 1)
    return _read_back(doc, _join(lines), i, i, span, lambda j: j)


def insert_block(text: str, source: str, /, *, before=None, after=None) -> str:
    """Insert `source` as a block before or after the block named, or after
    the last block. A blank line separates it from a non-blank neighbour."""
    _check_types(text, before, source)
    _check_types(text, after)
    doc = parse(text)
    if before is not None and after is not None:
        raise EditRefused("bad-position", "give before= or after=, not both")
    lines = _lines(text)
    if after is not None:
        k = _block(doc, after) + 1
        at = doc.blocks[k - 1]["lines"][1]
    elif before is not None:
        k = _block(doc, before)
        at = doc.blocks[k]["lines"][0] - 1
    else:
        k = len(doc.blocks)
        at = doc.blocks[-1]["lines"][1] if doc.blocks else len(lines)
    new = _source_lines(source)
    eol = _eol(lines, at)
    above = at > 0 and not _blank(lines[at - 1][0])
    below = at < len(lines) and not _blank(lines[at][0])
    added = [[""]] * above + [[b] for b in new] + [[""]] * below
    added = [[b[0], eol] for b in added]
    if at == len(lines) and lines and not lines[-1][1]:
        lines[-1][1] = eol
        added[-1][1] = ""
    lines[at:at] = added
    first = at + 1 + above
    span = (first, first + len(new) - 1)
    return _read_back(doc, _join(lines), None, k, span, lambda j: j + (j >= k))


def delete_block(text: str, node, /) -> str:
    """Delete block `node` and the blank lines between it and the next block,
    or, for the last block, those between it and the line before it."""
    _check_types(text, node)
    doc = parse(text)
    i = _block(doc, node)
    lines = _lines(text)
    first, last = doc.blocks[i]["lines"]
    start, end = first - 1, last
    following = next((j for j in range(last, len(lines)) if not _blank(lines[j][0])), None)
    if following is not None:
        end = following
    else:
        while start > 0 and _blank(lines[start - 1][0]):
            start -= 1
    took_bare_end = end == len(lines) and not lines[-1][1]
    del lines[start:end]
    if took_bare_end and lines:
        lines[-1][1] = ""
    return _read_back(doc, _join(lines), i, None, (), lambda j: None if j == i else j - (j > i))
