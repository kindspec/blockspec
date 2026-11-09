# SPDX-License-Identifier: Apache-2.0 OR MIT
"""The inline links of a piece of content, by CommonMark 0.31.2 section 6's rules.

Inline content is otherwise opaque. Two rules look inside it: a transclusion
(SPEC.md section 11.9) and `dangling-link` (section 9). Reference links cannot
occur, since the profile refuses every link reference definition.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .blocks import _ASCII_PUNCT, _skip_ws, parse_destination, parse_title

_WS = r"[ \t\n]"
_TAG = r"[A-Za-z][A-Za-z0-9-]*"
_NAME = r"[a-zA-Z_:][a-zA-Z0-9:._-]*"
_VALUE = "(?:[^ \t\n\"'=<>`]+|'[^']*'|\"[^\"]*\")"
_ATTR = rf"{_WS}+{_NAME}(?:{_WS}*={_WS}*{_VALUE})?"
_AT_EMAIL = (
    r"[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
    r"(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*"
)
_OPEN_TAG = re.compile(rf"<{_TAG}((?:{_ATTR})*){_WS}*/?>")
_CLOSE_TAG = re.compile(rf"</{_TAG}{_WS}*>")
_ONE_ATTR = re.compile(rf"{_WS}+({_NAME})(?:{_WS}*={_WS}*({_VALUE}))?")
_SKIP = re.compile(
    rf"<(?:[A-Za-z][A-Za-z0-9.+-]{{1,31}}:[^\x00-\x20\x7f<>]*>|{_AT_EMAIL}>"
    rf"|{_TAG}(?:{_ATTR})*{_WS}*/?>|/{_TAG}{_WS}*>"
    r"|!-->|!--->|!--.*?-->|\?.*?\?>|![A-Za-z][^>]*>|!\[CDATA\[.*?\]\]>)",
    re.S,
)


@dataclass
class Link:
    start: int
    end: int
    destination: str
    title: str | None
    close: int
    image: bool = False


@dataclass
class Inlines:
    """What CommonMark's inline rules find in a piece of content."""

    links: list[Link]
    tags: list[tuple[int, int]]
    ids: list[str]


def _inline_tail(s: str, i: int) -> tuple[int, str, str | None] | None:
    """After `](` at `i`: (end after `)`, destination, raw title), or None."""
    at = _skip_ws(s, i)
    if s[at : at + 1] == ")":
        return at + 1, "", None
    end = parse_destination(s, at)
    if end is None:
        return None
    dest = s[at + 1 : end - 1] if s[at] == "<" else s[at:end]
    after = _skip_ws(s, end)
    title = None
    if after != end and s[after : after + 1] != ")":
        stop = parse_title(s, after)
        if stop is None:
            return None
        title = s[after:stop]
        after = _skip_ws(s, stop)
    if s[after : after + 1] != ")":
        return None
    return after + 1, dest, title


def find_links(s: str) -> list[Link]:
    """The inline links of `s`: an image is not a link."""
    return [link for link in scan(s).links if not link.image]


def scan(s: str) -> Inlines:
    links: list[Link] = []
    tags: list[tuple[int, int]] = []
    ids: list[str] = []
    # Open brackets, innermost last: [position, is an image, still active].
    stack: list[list] = []
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c == "\\":
            i += 2 if s[i + 1 : i + 2] and s[i + 1] in _ASCII_PUNCT else 1
        elif c == "`":
            run = i
            while run < n and s[run] == "`":
                run += 1
            close = _closing_run(s, run, run - i)
            i = close if close is not None else run
        elif c == "<":
            m = _SKIP.match(s, i)
            if m is None:
                i += 1
                continue
            opening = _OPEN_TAG.fullmatch(s, m.start(), m.end())
            if opening or _CLOSE_TAG.fullmatch(s, m.start(), m.end()):
                tags.append((m.start(), m.end()))
            if opening:
                ids.extend(_identifiers(opening.group(1)))
            i = m.end()
        elif c == "!" and s[i + 1 : i + 2] == "[":
            stack.append([i, True, True])
            i += 2
        elif c == "[":
            stack.append([i, False, True])
            i += 1
        elif c == "]" and stack:
            start, image, active = stack.pop()
            tail = _inline_tail(s, i + 2) if active and s[i + 1 : i + 2] == "(" else None
            if tail is None:
                i += 1
                continue
            links.append(Link(start, tail[0], tail[1], tail[2], i, image))
            if not image:
                for opener in stack:
                    if not opener[1]:
                        opener[2] = False
            i = tail[0]
        else:
            i += 1
    return Inlines(links, tags, ids)


def _identifiers(attrs: str) -> list[str]:
    """The values of the `id` and `name` attributes among `attrs`."""
    out = []
    for m in _ONE_ATTR.finditer(attrs):
        value = m.group(2)
        if value is not None and m.group(1).lower() in ("id", "name"):
            out.append(value[1:-1] if value[0] in "'\"" else value)
    return out


def _closing_run(s: str, i: int, length: int) -> int | None:
    n = len(s)
    while i < n:
        if s[i] == "`":
            j = i
            while j < n and s[j] == "`":
                j += 1
            if j - i == length:
                return j
            i = j
        else:
            i += 1
    return None
