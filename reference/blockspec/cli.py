# SPDX-License-Identifier: Apache-2.0 OR MIT
"""`blockspec check`: read documents and report each one the profile refuses.

Exit codes follow kindkit's, because "nothing was checked" must never look
like "nothing was wrong":

    0   every document read
    1   at least one document refused
    2   no verdict: a path does not exist, or there were no documents to read
"""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Iterable

from blockspec.document import Refusal, parse

#: Never documents. `*.notes` directories hold comment records (SPEC.md §11.1),
#: which are not documents of the profile.
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
            subdirs[:] = sorted(
                d for d in subdirs if d not in SKIP_DIRS and not d.endswith(".notes")
            )
            files += [os.path.join(directory, n) for n in names if n.lower().endswith(SUFFIX)]
    return sorted(files)


def check_file(path: str) -> tuple[str | None, str] | None:
    """None when the document reads; otherwise its refusal code, which is None
    for a file no refusal code covers, and a message."""
    try:
        with open(path, "rb") as handle:
            data = handle.read()
    except OSError as exc:
        return None, f"cannot be read: {exc.strerror or exc}"
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return None, "is not UTF-8"
    try:
        parse(text)
    except Refusal as refusal:
        return refusal.code, refusal.message
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
    refused = 0
    for path in files:
        problem = check_file(path)
        if problem is not None:
            refused += 1
            _report(path, problem[0], problem[1], fmt)
    print(f"{len(files)} file(s) checked, {refused} refused")
    return EXIT_REFUSED if refused else EXIT_OK


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="blockspec")
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("check", help="report every document the profile refuses")
    run.add_argument("paths", nargs="+", help="files or directories")
    run.add_argument("--format", choices=["plain", "github"], default="plain")
    args = parser.parse_args(argv)
    return check(args.paths, args.format)
