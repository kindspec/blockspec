#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""The mutation gate: break the reference implementation, and require the
conformance tree to notice.

    python conformance/mutants.py

Each mutant below is a plausible implementation bug: a rule from
`docs/adjudications/` or a CommonMark 0.31.2 rule the profile builds on,
applied wrongly. Every one MUST fail at least one case that the unmutated
reference passes. A mutant that SURVIVES is a hole in the suite, not in the
implementation, and is reported as one.

The machinery is kindkit's (`kindkit.gate`): patterns are matched on a
normalised token stream, a pattern that no longer matches is STALE, and a run
that reaches no verdict is BROKEN. What is here is what knows about
`reference/blockspec/document.py`: the mutants, and the probe.

Two more checks than the kit makes, both by hashing:

* before the run, each mutant's spliced source is hashed against the
  unmutated source and against every other mutant's. A mutant that changes
  nothing, or one that is another mutant spelled differently, is refused
  before anything is probed;
* during the run, the probe hashes the file it is handed. Apart from the
  baseline, which is the unmutated source by design, a file whose hash is the
  unmutated source's is reported as no verdict, which the kit scores BROKEN.
  A mutation that did not land can then never read as a kill.

Exit codes are the runner's: 0 every mutant killed, 1 a mutant survived or
went stale or broken, 2 no verdict (the gate itself could not run).
"""

from __future__ import annotations

import hashlib
import os
import sys

from kindkit import GateError, MutantError, Verdict, apply_mutant, from_table, gate, probe_command
from kindkit.cli import EXIT_FAILURES, EXIT_NO_VERDICT, EXIT_OK

HERE = os.path.dirname(os.path.abspath(__file__))
IMPL = os.path.normpath(os.path.join(HERE, "..", "reference", "blockspec", "document.py"))
RUNNER = os.path.join(HERE, "run_cases.py")

#: Overwritten with each mutant and deleted at the end; gitignored. The runner
#: loads `--impl` by path under a module name of its own, so nothing on
#: `sys.path` can shadow it.
SCRATCH = os.path.join(HERE, "mutant_impl.py")

#: Seconds one probe may take. The whole tree runs in well under one, so only
#: a mutant that made the reader loop can reach this.
PROBE_TIMEOUT = 120

# name -> (old, new). Grouped by the rule each one breaks.
MUTANTS = {
    # --- conflict markers: 0001 section 4, README reading 14 ---------------
    "conflict-scan-skipped": (
        "        if _CONFLICT.match(line):",
        "        if False:",
    ),
    "conflict-marker-off-column-zero-is-refused": (
        'r"^(?:(?:<{7,}|>{7,}|\\|{7,})(?: |$)|={7,}$)"',
        'r"^[ \\t]*(?:(?:<{7,}|>{7,}|\\|{7,})(?: |$)|={7,}$)"',
    ),
    "conflict-run-of-six-is-a-marker": (
        'r"^(?:(?:<{7,}|>{7,}|\\|{7,})(?: |$)|={7,}$)"',
        'r"^(?:(?:<{6,}|>{6,}|\\|{6,})(?: |$)|={6,}$)"',
    ),
    "conflict-run-of-exactly-seven-only": (
        'r"^(?:(?:<{7,}|>{7,}|\\|{7,})(?: |$)|={7,}$)"',
        'r"^(?:(?:<{7}|>{7}|\\|{7})(?: |$)|={7}$)"',
    ),
    "conflict-separator-with-trailing-text-is-a-marker": (
        'r"^(?:(?:<{7,}|>{7,}|\\|{7,})(?: |$)|={7,}$)"',
        'r"^(?:(?:<{7,}|>{7,}|\\|{7,})(?: |$)|={7,})"',
    ),
    "conflict-diff3-base-line-is-text": (
        'r"^(?:(?:<{7,}|>{7,}|\\|{7,})(?: |$)|={7,}$)"',
        'r"^(?:(?:<{7,}|>{7,})(?: |$)|={7,}$)"',
    ),
    # --- frontmatter: 0002 addendum, README readings 9-13 ------------------
    "frontmatter-line-two-may-be-blank": (
        'if len(lines) > 1 and lines[0] == "---" and not _blank(lines[1]):',
        'if len(lines) > 1 and lines[0] == "---":',
    ),
    "frontmatter-cannot-be-empty": (
        "        for at in range(1, len(lines)):",
        "        for at in range(2, len(lines)):",
    ),
    "frontmatter-ends-at-the-last-closing-line": (
        "        for at in range(1, len(lines)):",
        "        for at in reversed(range(1, len(lines))):",
    ),
    "frontmatter-closing-line-may-carry-trailing-spaces": (
        '            if lines[at] == "---":',
        '            if lines[at].rstrip() == "---":',
    ),
    "frontmatter-range-is-one-short": (
        "                frontmatter = [1, at + 1]",
        "                frontmatter = [1, at]",
    ),
    "frontmatter-lines-are-parsed-as-blocks": (
        "                first = at + 1",
        "                first = 0",
    ),
    "frontmatter-unclosed-runs-to-the-end": (
        '            if lines[at] == "---":',
        '            if lines[at] == "---" or at == len(lines) - 1:',
    ),
    # --- the partition: 0002 section 1 -------------------------------------
    "block-range-keeps-trailing-blank-lines": (
        "            while end > node.start and _blank(lines[end - 1]):",
        "            while False:",
    ),
    "a-bullet-change-does-not-split-a-list": (
        'for key in ("kind", "bullet", "delimiter")',
        'for key in ("kind", "delimiter")',
    ),
    "a-delimiter-change-does-not-split-a-list": (
        'for key in ("kind", "bullet", "delimiter")',
        'for key in ("kind", "bullet")',
    ),
    "no-lazy-continuation": (
        'if not self.all_closed and not self.blank and self.tip.type == "paragraph":',
        "if False:",
    ),
    "list-item-before-thematic-break": (
        "            self.thematic_break,\n            self.list_item,",
        "            self.list_item,\n            self.thematic_break,",
    ),
    "a-blank-line-ends-a-list-item": (
        "                if not node.children:\n                    return 1",
        "                if True:\n                    return 1",
    ),
    "item-padding-ignores-spaces-after-the-marker": (
        'data["padding"] = width + spaces',
        'data["padding"] = width + 1',
    ),
    "a-list-marker-needs-no-space-after-it": (
        'if self.peek(self.next_nonspace + width) not in ("", " ", "\\t"):',
        "if False:",
    ),
    "any-ordered-number-interrupts-a-paragraph": (
        "int(ordered.group(1)) == 1",
        "True",
    ),
    "an-empty-item-interrupts-a-paragraph": (
        'if container.type == "paragraph" and _blank(self.line[self.next_nonspace + width :]):',
        "if False:",
    ),
    "a-tab-is-one-column": (
        "                to_tab = 4 - self.column % 4",
        "                to_tab = 1",
    ),
    "block-quote-keeps-the-space-after-its-marker": (
        """        self.advance_next_nonspace()
        self.advance_offset(1, False)
        if self.peek(self.offset) in (" ", "\\t"):
            self.advance_offset(1, True)
        self.close_unmatched()""",
        """        self.advance_next_nonspace()
        self.advance_offset(1, False)
        self.close_unmatched()""",
    ),
    # --- leaves and their content: README "Leaves and their content" -------
    "paragraph-keeps-trailing-spaces": (
        'return "\\n".join(text for _, text in self.lines).rstrip(" \\t")',
        'return "\\n".join(text for _, text in self.lines)',
    ),
    "paragraph-lines-keep-their-indentation": (
        """            else:
                self.advance_next_nonspace()
                break""",
        """            else:
                break""",
    ),
    "heading-keeps-its-closing-sequence": (
        'node.text = re.sub(r"[ \\t]+#+[ \\t]*$", "", text).strip(" \\t")',
        'node.text = text.strip(" \\t")',
    ),
    "heading-keeps-trailing-spaces": (
        'node.text = re.sub(r"[ \\t]+#+[ \\t]*$", "", text).strip(" \\t")',
        'node.text = re.sub(r"[ \\t]+#+[ \\t]*$", "", text)',
    ),
    "a-lone-hash-is-not-a-heading": (
        '_ATX = re.compile(r"^#{1,6}(?:[ \\t]+|$)")',
        '_ATX = re.compile(r"^#{1,6}[ \\t]+")',
    ),
    "code-lines-lose-their-line-ending": (
        'return "".join(text + "\\n" for _, text in self.lines)',
        'return "".join(text for _, text in self.lines)',
    ),
    "the-info-string-is-content": (
        "        node.fence = (match.group()[0], len(match.group()), self.indent)\n"
        "        return 3",
        "        node.fence = (match.group()[0], len(match.group()), self.indent)\n"
        "        info = self.line[self.next_nonspace + len(match.group()) :]\n"
        "        node.lines.append((self.line_no, info))\n"
        "        return 3",
    ),
    "code-keeps-the-fence-indentation": (
        '            while indent > 0 and self.peek(self.offset) in (" ", "\\t"):',
        "            while False:",
    ),
    "a-shorter-fence-closes-the-block": (
        "            if match and len(match.group()) >= length:",
        "            if match:",
    ),
    "either-fence-character-closes-the-block": (
        "closing = self.indent <= 3 and self.peek(self.next_nonspace) == char",
        'closing = self.indent <= 3 and self.peek(self.next_nonspace) in "`~"',
    ),
    "html-content-loses-its-line-ending": (
        '            return self.text + "\\n"',
        "            return self.text",
    ),
    # --- refusals: 0001 and 0002 -------------------------------------------
    "setext-heading-accepted": (
        '        raise Refusal("setext-heading", "a setext heading")',
        "        return 0",
    ),
    "indented-code-accepted": (
        '            raise Refusal("indented-code", "an indented code block")',
        "            pass",
    ),
    "indented-line-interrupts-a-paragraph": (
        'if self.indented and self.tip.type != "paragraph" and not self.blank:',
        "if self.indented and not self.blank:",
    ),
    "link-reference-definition-accepted": (
        'if node.type == "paragraph" and _link_reference_definition(node.content()):',
        "if False:",
    ),
    "link-reference-definition-found-on-any-line": (
        'if node.type == "paragraph" and _link_reference_definition(node.content()):',
        'if node.type == "paragraph" and any('
        "_link_reference_definition(text) for _, text in node.lines):",
    ),
    "link-reference-definition-ignores-trailing-text": (
        "    return destination_ends_its_line",
        "    return True",
    ),
    "raw-html-accepted-as-a-paragraph": (
        '                raise Refusal("raw-html", "an HTML block that is not a region marker")',
        "                return 0",
    ),
    "a-type-7-tag-line-interrupts-a-paragraph": (
        """            if kind == 7 and (
                container.type == "paragraph"
                or (not self.all_closed and not self.blank and self.tip.type == "paragraph")
            ):""",
        "            if False:",
    ),
    "any-comment-is-a-marker": (
        'r"^\\s*<!--\\s*#([a-z0-9][a-z0-9-]*)(:begin|:end)?\\s*-->\\s*$"',
        'r"^\\s*<!--\\s*#?([^:]*?)(:begin|:end)?\\s*-->\\s*$"',
    ),
    "a-marker-may-have-text-after-it": (
        'r"^\\s*<!--\\s*#([a-z0-9][a-z0-9-]*)(:begin|:end)?\\s*-->\\s*$"',
        'r"^\\s*<!--\\s*#([a-z0-9][a-z0-9-]*)(:begin|:end)?\\s*-->"',
    ),
    "a-marker-needs-exactly-one-space-inside": (
        'r"^\\s*<!--\\s*#([a-z0-9][a-z0-9-]*)(:begin|:end)?\\s*-->\\s*$"',
        'r"^\\s*<!-- #([a-z0-9][a-z0-9-]*)(:begin|:end)? -->\\s*$"',
    ),
    # --- names and regions: 0001, 0002 section 3 ---------------------------
    "dangling-marker-accepted": (
        "        if dangling:",
        "        if False:",
    ),
    "a-marker-may-name-a-marker": (
        "if target is None or target.marker is not None:",
        "if target is None:",
    ),
    "an-empty-region-is-accepted": (
        "                    if not region:",
        "                    if False:",
    ),
    "a-marker-names-the-previous-sibling": (
        "target = siblings[i + 1] if i + 1 < len(siblings) else None",
        "target = siblings[i - 1] if i + 1 < len(siblings) else None",
    ),
    "a-region-leaves-out-markers": (
        "region = [n.ref() for n in siblings[first + 1 : i]]",
        "region = [n.ref() for n in siblings[first + 1 : i] if n.marker is None]",
    ),
    "an-end-with-no-begin-is-ignored": (
        '                    unpaired.append(f"#{name}:end has no :begin beside it")',
        "                    pass",
    ),
    "a-begin-with-no-end-is-ignored": (
        '            unpaired += [f"#{name}:begin has no :end beside it" for name in begun]',
        "            pass",
    ),
    "duplicate-names-accepted": (
        "            if len(targets) > 1:",
        "            if False:",
    ),
    "unpaired-region-before-duplicate-name": (
        """        for name, targets in declared.items():
            if len(targets) > 1:
                raise Refusal("duplicate-name", f"#{name} is declared twice")
        if unpaired:
            raise Refusal("unpaired-region", unpaired[0])""",
        """        if unpaired:
            raise Refusal("unpaired-region", unpaired[0])
        for name, targets in declared.items():
            if len(targets) > 1:
                raise Refusal("duplicate-name", f"#{name} is declared twice")""",
    ),
    # --- resolution: 0001, D8 section 7.2's order --------------------------
    "slugs-before-markers": (
        "        if name in self.names:\n            return self.names[name]",
        "        if name in self.names and not any("
        '_slug(n.text) == name for n in self.nodes if n.type == "heading"):\n'
        "            return self.names[name]",
    ),
    "the-first-of-several-slugs-wins": (
        "        if len(headings) == 1:",
        "        if headings:",
    ),
    "only-top-level-headings-have-slugs": (
        'if n.type == "heading" and _slug(n.text) == name',
        'if n.type == "heading" and len(n.path) == 1 and _slug(n.text) == name',
    ),
    "a-slug-keeps-its-case": (
        "        for c in text.lower()",
        "        for c in text",
    ),
    "a-slug-keeps-punctuation": (
        'if c in " -_" or unicodedata.category(c)[0] in "LMN"',
        "if True",
    ),
    "a-slug-drops-underscores": (
        'if c in " -_" or unicodedata.category(c)[0] in "LMN"',
        'if c in " -" or unicodedata.category(c)[0] in "LMN"',
    ),
    "a-slug-collapses-runs-of-spaces": (
        '    return "".join(kept).replace(" ", "-")',
        '    return re.sub(" +", "-", "".join(kept))',
    ),
    "an-unknown-name-resolves-to-nothing": (
        '        return f"#REF!({name})"',
        "        return None",
    ),
    # --- tables: 0002 section 6, README reading 2 --------------------------
    "tables-not-recognised": (
        "        if not delimiter or not all(_DELIMITER_CELL.match(cell) for cell in delimiter):",
        "        if True:",
    ),
    "a-header-width-mismatch-is-a-table": (
        "        if len(header) != len(delimiter):",
        "        if False:",
    ),
    "a-pipeless-header-row-is-a-paragraph": (
        "            if len(delimiter) == 1:",
        "            if False:",
    ),
    "a-pipeless-header-row-is-a-table": (
        "        if header is None:",
        "        if header is None and len(delimiter) == 1:\n"
        '            header = [header_text.strip(" \\t")]\n'
        "        if header is None:",
    ),
    "the-table-start-runs-before-list-items": (
        """            self.setext_heading,
            self.thematic_break,
            self.list_item,
            self.indented_code,
            self.table""",
        """            self.setext_heading,
            self.table,
            self.thematic_break,
            self.list_item,
            self.indented_code""",
    ),
    "a-paragraph-line-above-a-table-accepted": (
        "        if len(container.lines) > 1:",
        "        if False:",
    ),
    "a-non-paragraph-line-above-a-table-accepted": (
        "        if at and parent.children[at - 1].last_content == header_line - 1:",
        "        if False:",
    ),
    "a-line-below-a-table-accepted": (
        "        if at + 1 < len(siblings) and siblings[at + 1].start == node.end + 1:",
        "        if False:",
    ),
    "a-row-needs-no-pipe": (
        "            if self.blank or not _split_row(self.line[self.next_nonspace :]):",
        "            if self.blank:",
    ),
    "a-row-with-no-cells-continues-the-table": (
        "            if self.blank or not _split_row(self.line[self.next_nonspace :]):",
        "            if self.blank or _split_row(self.line[self.next_nonspace :]) is None:",
    ),
    "an-escaped-pipe-splits-a-cell": (
        '        if c == "\\\\" and i + 1 < len(row):',
        "        if False:",
    ),
    "a-leading-pipe-makes-an-empty-cell": (
        '    if row.startswith("|"):\n        cells.pop(0)',
        "",
    ),
    "short-rows-are-not-padded": (
        'return [self.rows[0]] + [(row + [""] * width)[:width] for row in self.rows[1:]]',
        "return self.rows",
    ),
    "the-delimiter-row-is-content": (
        "        node.rows = [header]",
        "        node.rows = [header, delimiter]",
    ),
}


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def preflight(source: str, mutants=MUTANTS) -> list[str]:
    """Each mutant's spliced source, hashed: a mutation that changes nothing,
    or that is another mutant spelled differently, is refused before the run.
    A pattern that does not apply is left to the gate, which scores it STALE."""
    origin = _sha(source)
    seen: dict[str, str] = {}
    problems = []
    for name, (old, new) in mutants.items():
        try:
            digest = _sha(apply_mutant(source, old, new))
        except MutantError:
            continue
        if digest == origin:
            problems.append(f"BROKEN   {name}: the mutated source is the unmutated source")
        elif digest in seen:
            problems.append(f"BROKEN   {name}: the same mutated source as {seen[digest]}")
        else:
            seen[digest] = name
    return problems


def make_probe(origin: str):
    """The probe kindkit's gate calls with the scratch file's path."""
    calls = 0

    def probe(path: str) -> Verdict:
        nonlocal calls
        calls += 1
        with open(path, encoding="utf-8", newline="") as handle:
            if calls > 1 and _sha(handle.read()) == origin:
                print(f"  NO VERDICT  {path} holds the unmutated source", file=sys.stderr)
                return Verdict.none()
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        return probe_command(
            [sys.executable, RUNNER, "--impl", path], cwd=HERE, env=env, timeout=PROBE_TIMEOUT
        )

    return probe


def main(argv: list[str]) -> int:
    if argv:
        print("usage: mutants.py", file=sys.stderr)
        return EXIT_NO_VERDICT
    try:
        if os.path.lexists(SCRATCH):
            raise GateError(
                f"{SCRATCH} is left over from a gate run that was interrupted, and may "
                "hold a mutant: inspect it, delete it, and run the gate again"
            )
        with open(IMPL, encoding="utf-8", newline="") as handle:
            source = handle.read()
        problems = preflight(source)
        if problems:
            for problem in problems:
                print(f"  {problem}")
            return EXIT_FAILURES
        report = gate(
            source=IMPL,
            mutants=from_table(MUTANTS),
            probe=make_probe(_sha(source)),
            scratch=SCRATCH,
        )
    except GateError as exc:
        print(f"\nHARD FAILURE: {exc}", file=sys.stderr)
        return EXIT_NO_VERDICT
    return EXIT_OK if report.ok else EXIT_FAILURES


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
