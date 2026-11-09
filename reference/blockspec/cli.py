# SPDX-License-Identifier: Apache-2.0 OR MIT
"""`blockspec check`: read documents and report each one the profile refuses.

Exit codes follow kindkit's, because "nothing was checked" must never look
like "nothing was wrong":

    0   every document read
    1   at least one document refused
    2   no verdict: a path does not exist, there were no documents to read,
        or a document could not be read and none was refused
"""

from __future__ import annotations

import argparse
import io
import os
import sys
from collections.abc import Iterable

from blockspec.document import Refusal, parse

#: Never documents. A `*.notes` directory is read: a record is a document
#: (SPEC.md §11.1).
SKIP_DIRS = {".git", ".hg", ".svn", ".venv", "node_modules", "__pycache__"}
SUFFIX = ".md"
EXIT_OK, EXIT_REFUSED, EXIT_NO_VERDICT = 0, 1, 2


def collect(targets: Iterable[str]) -> list[str]:
    """Every document under `targets`. A file named directly is read whatever
    its name; a directory contributes its `.md` files."""
    files: list[str] = []
    for target in targets:
        if not os.path.isdir(target):
            files.append(target)
            continue
        for directory, subdirs, names in os.walk(target):
            subdirs[:] = sorted(d for d in subdirs if d not in SKIP_DIRS)
            files += [os.path.join(directory, n) for n in names if n.lower().endswith(SUFFIX)]
    return sorted({os.path.normpath(f) for f in files})


class Unreadable(Exception):
    """The file holds no answer either way: nothing was checked."""


def check_file(path: str) -> tuple[str | None, str] | None:
    """None when the document reads; otherwise its refusal code, which is None
    for a file no refusal code covers, and a message."""
    if not os.path.isfile(path):
        raise Unreadable("is not a regular file that exists")
    try:
        with open(path, "rb") as handle:
            data = handle.read()
    except OSError as exc:
        raise Unreadable(f"cannot be read: {exc.strerror or exc}") from exc
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return None, "is not UTF-8"
    try:
        parse(text, record=os.path.basename(os.path.dirname(path)).endswith(".notes"))
    except Refusal as refusal:
        return refusal.code, refusal.message
    except RecursionError as exc:
        raise Unreadable("is nested too deeply to read") from exc
    return None


def _data(text: str) -> str:
    """A workflow command's message, escaped as GitHub requires."""
    return text.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def _prop(text: str) -> str:
    """A workflow command's property value, such as `file=`."""
    return _data(text).replace(":", "%3A").replace(",", "%2C")


def _report(path: str, code: str | None, message: str, fmt: str) -> None:
    suffix = f" [{code}]" if code else ""
    if fmt == "github":
        print(f"::error file={_prop(path)},title={_prop('blockspec' + suffix)}::{_data(message)}")
    else:
        print(f"{path}: {message}{suffix}")


def check(paths: list[str], fmt: str = "plain") -> int:
    missing = [p for p in paths if not os.path.exists(p)]
    if missing:
        for path in missing:
            print(f"{path}: no such file or directory", file=sys.stderr)
        return EXIT_NO_VERDICT
    files = collect(paths)
    if not files:
        print(f"no documents under {' '.join(paths)}", file=sys.stderr)
        return EXIT_NO_VERDICT
    refused = unread = 0
    for path in files:
        try:
            problem = check_file(path)
        except Unreadable as exc:
            unread += 1
            print(f"{path}: {exc}", file=sys.stderr)
            continue
        if problem is not None:
            refused += 1
            _report(path, problem[0], problem[1], fmt)
    print(f"{len(files) - unread} file(s) checked, {refused} refused, {unread} unreadable")
    if refused:
        return EXIT_REFUSED
    return EXIT_NO_VERDICT if unread else EXIT_OK


def main(argv: list[str] | None = None) -> int:
    # A file's name can hold bytes the terminal's encoding cannot print.
    for stream in (sys.stdout, sys.stderr):
        if isinstance(stream, io.TextIOWrapper):
            stream.reconfigure(errors="backslashreplace")
    parser = argparse.ArgumentParser(prog="blockspec")
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("check", help="report every document the profile refuses")
    run.add_argument("paths", nargs="+", help="files or directories")
    run.add_argument("--format", choices=["plain", "github"], default="plain")
    args = parser.parse_args(argv)
    return check(args.paths, args.format)
