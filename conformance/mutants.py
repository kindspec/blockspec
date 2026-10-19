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
`reference/blockspec/document.py` and `reference/blockspec/anchor.py`: a
table of mutants for each, and their probes. The resolver's probe runs its
mutated copy as `anchor.py` beside a copy of the reader, which loads
`anchor.py` from its own directory.

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
import shutil
import sys
import tempfile

from kindkit import GateError, MutantError, Verdict, apply_mutant, from_table, gate, probe_command
from kindkit.cli import EXIT_FAILURES, EXIT_NO_VERDICT, EXIT_OK

HERE = os.path.dirname(os.path.abspath(__file__))
IMPL = os.path.normpath(os.path.join(HERE, "..", "reference", "blockspec", "document.py"))
RUNNER = os.path.join(HERE, "run_cases.py")
ANCHOR = os.path.join(os.path.dirname(IMPL), "anchor.py")

#: Overwritten with each mutant and deleted at the end; gitignored. The runner
#: loads `--impl` by path under a module name of its own, so nothing on
#: `sys.path` can shadow it. It sits beside the reader, because the reader's
#: `resolve` loads `anchor.py` from its own directory.
SCRATCH = os.path.join(os.path.dirname(IMPL), "mutant_impl.py")

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
    "frontmatter-opening-line-may-carry-trailing-spaces": (
        'if len(lines) > 1 and lines[0] == "---" and not _blank(lines[1]):',
        'if len(lines) > 1 and lines[0].rstrip(" \\t") == "---" and not _blank(lines[1]):',
    ),
    "frontmatter-cannot-be-empty": (
        "        for at in range(1, len(lines)):",
        "        for at in range(2, len(lines)):",
    ),
    "frontmatter-ends-at-the-last-closing-line": (
        "        for at in range(1, len(lines)):",
        "        for at in reversed(range(1, len(lines))):",
    ),
    "frontmatter-closing-line-must-be-exactly-three-dashes": (
        '            if lines[at].rstrip(" \\t") == "---":',
        '            if lines[at] == "---":',
    ),
    "frontmatter-closing-line-may-carry-any-whitespace": (
        '            if lines[at].rstrip(" \\t") == "---":',
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
        '            if lines[at].rstrip(" \\t") == "---":',
        '            if lines[at].rstrip(" \\t") == "---" or at == len(lines) - 1:',
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
        'r"^[ \\t]*<!--[ \\t]*#([a-z0-9][a-z0-9-]*)(:begin|:end)?[ \\t]*-->[ \\t]*$"',
        'r"^[ \\t]*<!--[ \\t]*#?([^:]*?)(:begin|:end)?[ \\t]*-->[ \\t]*$"',
    ),
    "a-marker-may-have-text-after-it": (
        'r"^[ \\t]*<!--[ \\t]*#([a-z0-9][a-z0-9-]*)(:begin|:end)?[ \\t]*-->[ \\t]*$"',
        'r"^[ \\t]*<!--[ \\t]*#([a-z0-9][a-z0-9-]*)(:begin|:end)?[ \\t]*-->"',
    ),
    "a-marker-needs-exactly-one-space-inside": (
        'r"^[ \\t]*<!--[ \\t]*#([a-z0-9][a-z0-9-]*)(:begin|:end)?[ \\t]*-->[ \\t]*$"',
        'r"^[ \\t]*<!-- #([a-z0-9][a-z0-9-]*)(:begin|:end)? -->[ \\t]*$"',
    ),
    "marker-spacing-is-any-whitespace": (
        'r"^[ \\t]*<!--[ \\t]*#([a-z0-9][a-z0-9-]*)(:begin|:end)?[ \\t]*-->[ \\t]*$"',
        'r"^\\s*<!--\\s*#([a-z0-9][a-z0-9-]*)(:begin|:end)?\\s*-->\\s*$"',
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
        '    return _SLUG_REMOVED.sub("", text.lower()).replace(" ", "-")',
        '    return _SLUG_REMOVED.sub("", text).replace(" ", "-")',
    ),
    "a-slug-keeps-punctuation": (
        '    return _SLUG_REMOVED.sub("", text.lower()).replace(" ", "-")',
        '    return text.lower().replace(" ", "-")',
    ),
    "a-slug-removes-by-unicode-category": (
        '    return _SLUG_REMOVED.sub("", text.lower()).replace(" ", "-")',
        '    return re.sub(r"[^\\w\\- ]", "", text.lower()).replace(" ", "-")',
    ),
    "a-heading-with-inline-markup-has-a-slug": (
        "    if _INLINE_MARKUP.intersection(text):\n        return None",
        "    if False:\n        return None",
    ),
    "a-heading-with-an-ampersand-has-a-slug": (
        '_INLINE_MARKUP = frozenset("*_`[<&")',
        '_INLINE_MARKUP = frozenset("*_`[<")',
    ),
    "a-slug-collapses-runs-of-spaces": (
        '    return _SLUG_REMOVED.sub("", text.lower()).replace(" ", "-")',
        '    return re.sub(" +", "-", _SLUG_REMOVED.sub("", text.lower()))',
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
    "an-empty-delimiter-row-makes-a-table": (
        "        if not delimiter or not all(_DELIMITER_CELL.match(cell) for cell in delimiter):",
        "        if not all(_DELIMITER_CELL.match(cell) for cell in delimiter):",
    ),
    "a-header-width-mismatch-is-a-table": (
        "        if len(header) != len(delimiter):",
        "        if False:",
    ),
    "a-table-only-github-reads-is-a-paragraph": (
        """            raise Refusal(
                "ambiguous-table",
                "a table to GitHub and a paragraph to pandoc and markdown-it",
            )""",
        "            return 0",
    ),
    "a-pipeless-header-row-is-a-table": (
        "_has_pipe(delimiter_text) and _has_pipe(header_raw)",
        "_has_pipe(delimiter_text)",
    ),
    "a-pipeless-delimiter-row-is-a-table": (
        "_has_pipe(delimiter_text) and _has_pipe(header_raw)",
        "_has_pipe(header_raw)",
    ),
    "form-feeds-are-not-refused": (
        '        if any(c in delimiter_text or c in header_raw for c in "\\f\\v"):',
        "        if False:",
    ),
    "vertical-tabs-are-not-refused": (
        '        if any(c in delimiter_text or c in header_raw for c in "\\f\\v"):',
        '        if any(c in delimiter_text or c in header_raw for c in "\\f"):',
    ),
    "only-a-form-feed-in-the-delimiter-row-is-refused": (
        '        if any(c in delimiter_text or c in header_raw for c in "\\f\\v"):',
        '        if any(c in delimiter_text for c in "\\f\\v"):',
    ),
    "a-form-feed-under-any-paragraph-line-is-refused": (
        "            if _FFVT_DELIMITER.match(delimiter_text):",
        "            if True:",
    ),
    "a-lazy-header-line-is-read-stripped": (
        "        header_raw = container.lazy.get(header_line, header_text)",
        "        header_raw = header_text",
    ),
    "a-lazy-header-line-keeps-no-empty-first-cell": (
        "        lazy = header_line in container.lazy",
        "        lazy = False",
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
        "            if self.blank or not _has_pipe(row) or not _split_row(row):",
        "            if self.blank or not _split_row(row):",
    ),
    "a-row-with-no-cells-continues-the-table": (
        "            if self.blank or not _has_pipe(row) or not _split_row(row):",
        "            if self.blank or not _has_pipe(row):",
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

# The resolver's mutants: the same gate over reference/blockspec/anchor.py,
# probed by the anchor cases. Mutants that only turn an UNDECIDED into a
# guess are left out, since no case can expect UNDECIDED, and so are the
# duplicate-id warning, which no case field asserts, and a notes
# directory's subfolder, which a case cannot name (cases/README.md).
ANCHOR_MUTANTS = {
    "escape set misses U+2028": (
        "0x2028, 0x2029",
        "0x2029",
    ),
    "escape set misses C1 controls": (
        "*range(0x7F, 0xA0)",
        "0x7F",
    ),
    "negative nth read": (
        'if leaf["nth"] < 0 or leaf["type"]',
        'if leaf["type"]',
    ),
    "replace not tied to kind": (
        'if (anchor.replace is not None) != (kind == "suggestion"):',
        "if False:",
    ),
    "canonical bytes not compared": (
        "return anchor if write_anchor(anchor) == value else None",
        "return anchor",
    ),
    "table pipe not escaped": (
        'cell.replace("|", "\\\\|")',
        "cell",
    ),
    "heading level dropped": (
        'f"h{_heading_level(self.lines[node.start - 1])}"',
        '"h1"',
    ),
    "text not normalised": (
        'text_ = unicodedata.normalize("NFC", text_)',
        "text_ = text_",
    ),
    "half compares strictly": (
        "return 4 * sim[0] >= sim[1]",
        "return 4 * sim[0] > sim[1]",
    ),
    "margin compares strictly": (
        "return 40 * l1 * t2 - 40 * l2 * t1 >= 3 * t1 * t2",
        "return 40 * l1 * t2 - 40 * l2 * t1 > 3 * t1 * t2",
    ),
    "margin in floating point": (
        "return 40 * l1 * t2 - 40 * l2 * t1 >= 3 * t1 * t2",
        "return 2 * l1 / t1 - 2 * l2 / t2 >= 0.15",
    ),
    "alignment skips the second first": (
        "elif suffix[i + 1][j] == suffix[i][j]:",
        "elif suffix[i][j + 1] != suffix[i][j]:",
    ),
    "chain is the rightmost": (
        "k = min(options, key=lambda k: pairs[k][1])",
        "k = max(options, key=lambda k: pairs[k][1])",
    ),
    "chain is not the longest": (
        "longest[k] = max(longest[k], longest[later] + 1)",
        "longest[k] = 1",
    ),
    "moved pairs dropped": (
        "            if (b, c) not in on_chain:\n                self.pair[b] = (c, MOVED)",
        "            if False:\n                self.pair[b] = (c, MOVED)",
    ),
    "moved leaves stay in gaps": (
        "if c not in moved_current]",
        "]",
    ),
    "no lcs in gaps": (
        "for i, j in lcs_alignment(keys_b, keys_c).items():",
        "for i, j in {}.items():",
    ),
    "edit needs no half": (
        "        if not at_least_half(sim):\n            return False",
        "        if False:\n            return False",
    ),
    "edit needs no lead over other current": (
        "for o in left_current if o != c):",
        "for o in [] if o != c):",
    ),
    "edit needs no lead over other base": (
        "for o in left_base if o != b)",
        "for o in [] if o != b)",
    ),
    "no unaccounted-copy": (
        '        if copies:\n            raise _Refused("unaccounted-copy")',
        '        if False:\n            raise _Refused("unaccounted-copy")',
    ),
    "repeat only when base repeats": (
        "if len(base_copies) > 1 or len(copies) > 1:",
        "if len(base_copies) > 1:",
    ),
    "repeat only when current repeats": (
        "if len(base_copies) > 1 or len(copies) > 1:",
        "if len(copies) > 1:",
    ),
    "exact near-copy off": (
        "corr.current[u].key != leaf.key and at_least_half(corr.word_similarity(k, u))",
        "False",
    ),
    "exact near-copy counts exact copies": (
        "corr.current[u].key != leaf.key and at_least_half(corr.word_similarity(k, u))",
        "at_least_half(corr.word_similarity(k, u))",
    ),
    "exact near-copy by code points": (
        "corr.current[u].key != leaf.key and at_least_half(corr.word_similarity(k, u))",
        "corr.current[u].key != leaf.key and at_least_half(corr.similarity(k, u))",
    ),
    "exact near-copy below half": (
        "corr.current[u].key != leaf.key and at_least_half(corr.word_similarity(k, u))",
        "corr.current[u].key != leaf.key and corr.word_similarity(k, u)[0] > 0",
    ),
    "words split on any whitespace": (
        '_SPACE = re.compile(r"[\\t\\n\\r ]+")',
        '_SPACE = re.compile(r"\\s+")',
    ),
    "words split at punctuation": (
        '_SPACE = re.compile(r"[\\t\\n\\r ]+")',
        '_SPACE = re.compile(r"\\W+")',
    ),
    "words carry the type": (
        "return [w for w in _SPACE.split(leaf.text) if w]",
        "return [leaf.type] + [w for w in _SPACE.split(leaf.text) if w]",
    ),
    "a leaf with no words scores one": (
        "return 0, 2",
        "return (2, 2) if not wa and not wb else (0, 2)",
    ),
    "near-copy below half": (
        "return any(at_least_half(corr.similarity(k, u)) for u in unmatched)",
        "return any(corr.similarity(k, u)[0] > 0 for u in unmatched)",
    ),
    "moved and edited near-copy by words": (
        "return any(at_least_half(corr.similarity(k, u)) for u in unmatched)",
        "return any(at_least_half(corr.word_similarity(k, u)) for u in unmatched)",
    ),
    "moved near-copy off": (
        "    elif kind == MOVED:\n        if near():",
        "    elif kind == MOVED:\n        if False:",
    ),
    "refilled gap off": (
        (
            "        if any(u in gap_current for u in unmatched):\n"
            '            raise _Refused("refilled-gap")'
        ),
        '        if False:\n            raise _Refused("refilled-gap")',
    ),
    "exact-copy off": (
        "if any(u in copies for u in unmatched):",
        "if False:",
    ),
    "exact-copy counts paired copies": (
        "if any(u in copies for u in unmatched):",
        "if len(copies) > 0:",
    ),
    "crowded gap off": (
        (
            "        if any(u in gap_current for u in unmatched):\n"
            '            raise _Refused("crowded-gap")'
        ),
        '        if False:\n            raise _Refused("crowded-gap")',
    ),
    "edited near-copy off": (
        (
            "    else:\n"
            "        if any(u in copies for u in unmatched):\n"
            '            raise _Refused("exact-copy")\n'
            "        if any(u in gap_current for u in unmatched):\n"
            '            raise _Refused("crowded-gap")\n'
            "        if near():"
        ),
        (
            "    else:\n"
            "        if any(u in copies for u in unmatched):\n"
            '            raise _Refused("exact-copy")\n'
            "        if any(u in gap_current for u in unmatched):\n"
            '            raise _Refused("crowded-gap")\n'
            "        if False:"
        ),
    ),
    "empty span allowed": (
        '    if not anchor.span:\n        raise _Refused("record-inconsistent")',
        '    if False:\n        raise _Refused("record-inconsistent")',
    ),
    "triple may occur twice": (
        "if len(found) != 1:",
        "if not found:",
    ),
    "short prefix anywhere": (
        "if len(anchor.prefix) < CONTEXT and at > 0:",
        "if False:",
    ),
    "short suffix anywhere": (
        "if len(anchor.suffix) < CONTEXT and end < len(text):",
        "if False:",
    ),
    "occurrences skip overlaps": (
        "at = text.find(part, at + 1)",
        "at = text.find(part, at + len(part))",
    ),
    "no prefix edge rule": (
        "prefix_holds = before == spaced(prefix)",
        "prefix_holds = before.endswith(spaced(prefix))",
    ),
    "no suffix edge rule": (
        "suffix_holds = after == spaced(suffix)",
        "suffix_holds = after.startswith(spaced(suffix))",
    ),
    "short prefix counted after collapse": (
        "        if len(prefix) < CONTEXT:\n            prefix_holds",
        "        if len(spaced(prefix)) < CONTEXT:\n            prefix_holds",
    ),
    "short suffix counted after collapse": (
        "        if len(suffix) < CONTEXT:\n            suffix_holds",
        "        if len(spaced(suffix)) < CONTEXT:\n            suffix_holds",
    ),
    "neighbours unchecked": (
        (
            "if _neighbour(text, at - 1) != before_was or "
            "_neighbour(text, at + len(span)) != after_was:"
        ),
        "if False:",
    ),
    "neighbour before unchecked": (
        (
            "if _neighbour(text, at - 1) != before_was or "
            "_neighbour(text, at + len(span)) != after_was:"
        ),
        "if _neighbour(text, at + len(span)) != after_was:",
    ),
    "neighbour after unchecked": (
        (
            "if _neighbour(text, at - 1) != before_was or "
            "_neighbour(text, at + len(span)) != after_was:"
        ),
        "if _neighbour(text, at - 1) != before_was:",
    ),
    "neighbour whitespace compared exactly": (
        'return " " if text[at] in "\\t\\n\\r " else text[at]',
        "return text[at]",
    ),
    "neighbour edge matches a space": (
        'if at < 0 or at >= len(text):\n        return ""',
        'if at < 0 or at >= len(text):\n        return " "',
    ),
    "prose context compared exactly": (
        "spaced = (lambda t: t) if exact else _spaced",
        "spaced = lambda t: t",
    ),
    "code and table context collapsed": (
        "spaced = (lambda t: t) if exact else _spaced",
        "spaced = _spaced",
    ),
    "text before the hit not collapsed": (
        "before, after = spaced(text[:at]), spaced(text[at + len(span) :])",
        "before, after = text[:at], spaced(text[at + len(span) :])",
    ),
    "text after the hit not collapsed": (
        "before, after = spaced(text[:at]), spaced(text[at + len(span) :])",
        "before, after = spaced(text[:at]), text[at + len(span) :]",
    ),
    "stored prefix not collapsed": (
        "prefix_holds = before.endswith(spaced(prefix))",
        "prefix_holds = before.endswith(prefix)",
    ),
    "stored suffix not collapsed": (
        "suffix_holds = after.startswith(spaced(suffix))",
        "suffix_holds = after.startswith(suffix)",
    ),
    "only the anchored leaf's type decides": (
        'exact = base.type in ("code", "table") or current.type in ("code", "table")',
        'exact = base.type in ("code", "table")',
    ),
    "only the paired leaf's type decides": (
        'exact = base.type in ("code", "table") or current.type in ("code", "table")',
        'exact = current.type in ("code", "table")',
    ),
    "code and table take one side": (
        "if both_sides or exact or not (prefix or suffix):",
        "if both_sides or not (prefix or suffix):",
    ),
    "a suggestion takes one side": (
        "if both_sides or exact or not (prefix or suffix):",
        "if exact or not (prefix or suffix):",
    ),
    "a comment needs both sides": (
        "if both_sides or exact or not (prefix or suffix):",
        "if True:",
    ),
    "an empty prefix counts": (
        '(prefix_holds and prefix != "")',
        "prefix_holds",
    ),
    "an empty suffix counts": (
        '(suffix_holds and suffix != "")',
        "suffix_holds",
    ),
    "two hits not ambiguous": (
        "if len(hits) > 1:",
        "if False:",
    ),
    "no alignment check": (
        "if any(paired.get(start + d) != hit + d for d in range(len(span))):",
        "if False:",
    ),
    "gate ignores status": (
        'if record.status != "open" or status not in ("RESOLVED", "EDITED"):',
        'if status not in ("RESOLVED", "EDITED"):',
    ),
    "gate applies on moved": (
        'if record.status != "open" or status not in ("RESOLVED", "EDITED"):',
        'if record.status != "open" or status not in ("RESOLVED", "EDITED", "MOVED"):',
    ),
    "break written as LF": (
        'replace = replace.replace("\\n", ending + prefix)',
        'replace = replace.replace("\\n", "\\n" + prefix)',
    ),
    "break written with no prefix": (
        'replace = replace.replace("\\n", ending + prefix)',
        'replace = replace.replace("\\n", ending)',
    ),
    "synthetic spaces mapped": (
        '            if k and raw[len(raw) - len(tail) - 1] != "\\t":\n                continue',
        "            if k:\n                continue",
    ),
    "absolute path allowed": (
        'if path.startswith("/") or ":" in segments[0]:',
        'if path.startswith("/"):',
    ),
    "scheme path allowed": (
        'if path.startswith("/") or ":" in segments[0]:',
        'if ":" in segments[0]:',
    ),
    "above the root allowed": (
        (
            "            if not out:\n"
            '                raise _Refused("unresolvable-path")\n'
            "            out.pop()"
        ),
        "            if out:\n                out.pop()",
    ),
    "pins order unchecked": (
        'if pins and got["path"] <= list(pins)[-1]:',
        "if False:",
    ),
    "pins after a blank line read": (
        'not line.strip(" \\t") or line.startswith((" ", "#")) for line in lines[at:later]',
        "False for line in lines[at:later]",
    ),
    "name ref skipped": (
        "    if binding is None:\n        return",
        "    if False:\n        return",
    ),
    "rebound unchecked": (
        "if any(c not in inside for c in pairs):",
        "if False:",
    ),
    "reply-to not canonical": (
        "if not isinstance(got, str) or canonical_string(got) != value:",
        "if not isinstance(got, str):",
    ),
    "pin not canonical": (
        "        if written != value:\n            return None",
        "        if False:\n            return None",
    ),
    "pins line with trailing text": (
        'if len(heads) > 1 or lines[heads[0]] != "pins:":',
        "if len(heads) > 1:",
    ),
    "dot segment kept": (
        '        if segment == ".":\n            continue',
        "        if False:\n            continue",
    ),
    "synthetic char inside span mapped": (
        "if any(p is None for p in positions[a:b]) or a == b:",
        "if a == b:",
    ),
    "repeat ignores counts": (
        '            if in_base != in_current:\n                raise _Refused("repeat")',
        '            if False:\n                raise _Refused("repeat")',
    ),
    "over-long context read": (
        "if len(anchor.prefix) > CONTEXT or len(anchor.suffix) > CONTEXT:",
        "if False:",
    ),
    "reply-to any string": (
        "if parent is None or not _ULID.fullmatch(parent):",
        "if parent is None:",
    ),
    "lowercase ulid read": (
        'if not name.endswith(".md") or not _ULID.fullmatch(name[: -len(".md")]):',
        'if not name.endswith(".md") or not _ULID.fullmatch(name[: -len(".md")].upper()):',
    ),
    "reply parent never found": (
        'found = f"{directory}/{record.reply_to}.md" in tree',
        "found = False",
    ),
    "base checked before record-only checks": (
        (
            "        start = span_in_base(anchor)  # step 1: the checks"
            " that read only the record\n"
            "        current, base, k = _record_inputs(reader, repo, do"
            "cument, anchor)"
        ),
        (
            "        current, base, k = _record_inputs(reader, repo, do"
            "cument, anchor)\n"
            "        start = span_in_base(anchor)  # step 1: the checks"
            " that read only the record"
        ),
    ),
    "record body not checked": (
        "try:\n        reader.parse(text)",
        "try:\n        pass",
    ),
    "document missing ignored for records": (
        '    if document not in repo["tree"]:\n        raise _Refused("document-missing")',
        '    if False:\n        raise _Refused("document-missing")',
    ),
    "base read before the document": (
        (
            '    current = _read(reader, repo["tree"][document])\n'
            '    if anchor.base not in repo["blobs"]:\n'
            '        raise _Refused("base-unavailable")\n'
            '    base = _read(reader, repo["blobs"][anchor.base])'
        ),
        (
            '    if anchor.base not in repo["blobs"]:\n'
            '        raise _Refused("base-unavailable")\n'
            '    base = _read(reader, repo["blobs"][anchor.base])\n'
            '    current = _read(reader, repo["tree"][document])'
        ),
    ),
    "lazy bq line repeats a shorter prefix": (
        'if j >= len(raw_line) or raw_line[j] != ">":\n                raise _Unmappable()',
        'if j >= len(raw_line) or raw_line[j] != ">":\n                break',
    ),
    "lazy list line repeats a shorter prefix": (
        (
            '            if part != " " * width:\n'
            "                raise _Unmappable()  # a lazy line, which "
            "has no prefix to repeat"
        ),
        '            if part != " " * width:\n                break',
    ),
    "tab after a quote marker repeated": (
        (
            '            if j < len(raw_line) and raw_line[j] == "\\t":'
            "\n"
            "                raise _Unmappable()  # a tab in the contai"
            "ner prefix"
        ),
        (
            "            if False:\n"
            "                raise _Unmappable()  # a tab in the contai"
            "ner prefix"
        ),
    ),
    "item first line repeated": (
        "if node.start == number:\n                raise _Unmappable()",
        "if False:\n                raise _Unmappable()",
    ),
    "break with no ending written": (
        "if not ending:\n            raise _Unmappable()",
        "if False:\n            raise _Unmappable()",
    ),
    "refused referrer enumerated": (
        '        return "REFUSED(not-in-profile)"',
        "        return []",
    ),
    "pins before the path": (
        "    target = resolve_path(referrer, one.path)  # 1.1",
        (
            "    if pins is None:\n"
            '        raise _Refused("record-inconsistent")\n'
            "    target = resolve_path(referrer, one.path)  # 1.1"
        ),
    ),
    "broken pins ignored": (
        '    if pins is None:  # 1.2\n        raise _Refused("record-inconsistent")',
        "    if pins is None:  # 1.2\n        pins = {}",
    ),
    "missing target after the pin": (
        '    if target not in tree:  # 1.3\n        raise _Refused("document-missing")',
        (
            "    if target not in tree and one.path in pins and pins[on"
            "e.path] in blobs:  # 1.3\n"
            '        raise _Refused("document-missing")'
        ),
    ),
    "slug-only name not checked early": (
        "    if _slug_only(reader, current, one.name):  # 1.5",
        "    if False:  # 1.5",
    ),
    "slug match ignored": (
        "reader.slug(node.text) == name for node",
        "False for node",
    ),
    "marker name taken for slug-only": (
        "    if name in current.doc.names:\n        return False",
        "    if False:\n        return False",
    ),
    "pinned blob not required": (
        '    if pins[one.path] not in blobs:  # 1.6\n        raise _Refused("base-unavailable")',
        (
            "    if pins[one.path] not in blobs:  # 1.6\n"
            '        return {"status": "RESOLVED", "unit": None}'
        ),
    ),
    "pinned name unchecked": (
        (
            "    if one.name not in pinned.doc.names:  # 1.8\n"
            '        raise _Refused("record-inconsistent")'
        ),
        '    if False:  # 1.8\n        raise _Refused("record-inconsistent")',
    ),
    "orphaned pinned leaf passes": (
        '            raise _Refused("pinned-orphaned")',
        "            continue",
    ),
    "last pinned leaf decides": (
        "    for leaf in _bound_leaves(pinned, pinned.doc.names[one.name]):",
        "    for leaf in reversed(_bound_leaves(pinned, pinned.doc.names[one.name])):",
    ),
    "anchor array taken for an object": (
        "    if not isinstance(pairs, _Object):\n        return None\n    keys",
        "    if not isinstance(pairs, list):\n        return None\n    keys",
    ),
    "inner link ignored": (
        "                    raise _NotALink()",
        "                    pass",
    ),
    "entity without semicolon decoded": (
        '    return _ENTITY.sub(lambda m: html.unescape(m.group()), inner) == "transclude"',
        '    return html.unescape(inner) == "transclude"',
    ),
    "image read as a link": (
        'if content.startswith("![") and _link_destination(content[1:]) is not None:',
        "if False:",
    ),
    "prose with a title read as a link": (
        '    if "](" not in content:\n        return None  # no inline link at all',
        "    if False:\n        return None  # no inline link at all",
    ),
    "line ending after the title refused": (
        "r'(?:[ \\t]+(?:\\n[ \\t]*)?|\\n[ \\t]*)\"transclude\"[ \\t]*(?:\\n[ \\t]*)?\\)'",
        "r'(?:[ \\t]+(?:\\n[ \\t]*)?|\\n[ \\t]*)\"transclude\"[ \\t]*\\)'",
    ),
    "code block's final line ending written": (
        'if leaf.node.type == "code_block" and b == len(content):',
        "if False:",
    ),
    "reply's document unchecked": (
        (
            "            if document not in tree:\n"
            '                raise _Refused("document-missing")\n'
            "            _read(reader, tree[document])"
        ),
        "            pass",
    ),
}

ANCHOR_EQUIVALENT = {
    "item first line repeated": (
        "a list item's first line holds its marker in the prefix region, so the "
        "lazy-line check refuses the break anyway"
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


def make_anchor_probe(origin: str, impl: str):
    """The probe for the resolver's mutants. The reader loads `anchor.py`
    from its own directory, so the scratch file is `anchor.py` in a
    directory of its own, beside `impl`, a copy of the unmutated reader."""
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
            [sys.executable, RUNNER, "--impl", impl], cwd=HERE, env=env, timeout=PROBE_TIMEOUT
        )

    return probe


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
        with open(ANCHOR, encoding="utf-8", newline="") as handle:
            anchor = handle.read()
        problems = preflight(source) + preflight(anchor, ANCHOR_MUTANTS)
        if problems:
            for problem in problems:
                print(f"  {problem}")
            return EXIT_FAILURES
        print("--- the reader, reference/blockspec/document.py")
        report = gate(
            source=IMPL,
            mutants=from_table(MUTANTS),
            probe=make_probe(_sha(source)),
            scratch=SCRATCH,
        )
        print("\n--- the resolver, reference/blockspec/anchor.py")
        workdir = tempfile.mkdtemp(prefix="blockspec-anchor-gate-")
        try:
            impl = os.path.join(workdir, "document.py")
            shutil.copyfile(IMPL, impl)
            anchor_report = gate(
                source=ANCHOR,
                mutants=from_table(ANCHOR_MUTANTS, ANCHOR_EQUIVALENT),
                probe=make_anchor_probe(_sha(anchor), impl),
                scratch=os.path.join(workdir, "anchor.py"),
            )
        finally:
            shutil.rmtree(workdir, ignore_errors=True)
    except GateError as exc:
        print(f"\nHARD FAILURE: {exc}", file=sys.stderr)
        return EXIT_NO_VERDICT
    return EXIT_OK if report.ok and anchor_report.ok else EXIT_FAILURES


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
