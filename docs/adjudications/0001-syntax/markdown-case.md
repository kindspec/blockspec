<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# blockspec#3: the case for markdown (a CommonMark profile)

**The position.** Draft 0 should be a strict *profile* of CommonMark 0.31.2. It
adds no syntax and removes nothing a CommonMark reader would mis-parse. It
carries one convention, the region marker `<!-- #name -->` from D8 §7.2. The
reference reads it with a block-level, standard-library-only parser, and inline
content stays opaque text. That is not a dialect: every conforming file is a
CommonMark document, and every CommonMark parser builds the same block tree
from it.

Citations: research at `d02c196`, blockspec at `1a969d0`. Commands were run
on 2026-10-14.

## 1. "Attributes are non-negotiable as standoff anchors"

**Answered. The premise was overturned by the research the brief cites.**

The claim in the brief is D5 §0 item 5, worded the same way, and it rests on
D5 §5.4: *"stable per-block identity in the canonical text is mandatory …
Markdown cannot provide it. Djot can (`{#id}`)."* D8 measured that premise and
rejected it:

- D8 §0: *"None of the three is a minted id in the file."* Two-stage quote
  anchoring gave *"92.9% correct, 7.1% loud refusal, 0.00% silent-wrong"*. A
  stored id under stock git *"survives only when the block's bytes did not
  change, which is precisely the case an exact-quote match already handles."*
- D8 invariant I7: a reference *"may write nothing into the artifact it refers
  to."* Anchors live in the referrer or in a sidecar (§7.3).
- The brief accepts this itself: *"A prose block gets NO minted id."*

So the only in-file identity left is **a name an author chose**. For that, D8
§7.2 chose the HTML comment over `{#id}`. D8 checked it with a CommonMark
parser: the comment is *"invisible in every renderer including GitHub's"*,
while `{#custom-id}` *"renders literally as visible garbage"*. I checked it
again: `markdown_it` in `commonmark` mode parses `<!-- #scram -->` followed by
a paragraph as `['html_block', 'paragraph_open', …]`. That is CommonMark
HTML-block type 2, a block of its own, with no extension.

A djot `{#name}` would sit in the same place, on the line before the block. So
it merges the same way, and D8 §11's open item 5 (a marker next to a
concurrent edit conflicts) applies to both formats equally. For the identity
the design allows, the two carriers do the same job.

**Conceded.** CommonMark has no carrier for *classes* or *key=value* on
arbitrary inlines or blocks (D5 §1.1, quoting jgm). If draft 0 needs typed
semantic containers, in the DITA-specialization sense of D5 §6.3, then
markdown needs a dialect and djot wins. But that is an extensibility need, and
the issue argues from anchors. Merged table cells (D5 §2) are rowspec's
problem: *"one MODEL, several grammars."*

## 2. What the spike's FOUND implies

LOG §35 reports **FOUND**: 432 qualifying distinct units in 35 cells, from
413 qualifying packets. Here is what failed, tallied from the write-up:

```
git show 1a969d0:spike/results/prereg3/run2/reproduction.md \
  | grep -o 'mechanism [QR], unit \[[^]]*\], block type `[^`]*`' ...
  143 Q  (76 heading, 64 prose, 3 list)
  270 R  — every one `R:slug`; zero on a region marker
```

Every silent mis-resolution was either a **quote anchor**, which writes nothing
into the target and so is the same under any syntax, or a **derived heading
slug**. No *author-chosen name* failed. Djot derives the same slugs: syntax.md
says *"Identifiers are added automatically to any headings that do not have
explicit identifiers … if necessary for uniqueness, adding a numerical
suffix."* That suffix is a re-pointing hazard of its own: insert a duplicate
heading above, and `-1` now names a different section. D8's rule turns that
case into a `#REF!`.

So the FOUND says blockspec should be built (§35: *"proceeds to blockspec#3,
#4 and #5"*). It also says what to fix:

- derived names should not count as durable references;
- Q needs hardening.

**Neither fix depends on the syntax.** The FOUND gives no evidence for djot
over markdown. Two cautions from §35 itself: 171 of the 432 units rest on the
weaker `DELETED` oracle verdict, and the tiering is *"a noisy instrument"*.

## 3. What a parser costs an independent implementation

**The framing "markdown means no dependency, djot means a dependency" is wrong
in both directions.** rowspec's rule is *"`reference/` is standard library
only"* (rowspec AGENTS.md), and the org contract §7 escalates any new runtime
dependency in `reference/`. Python's standard library parses neither format.
So under either choice the reference contains a hand-written parser, and the
real question is the one below.

**What must an implementer in another language write, and what can they check
it against?**

| | CommonMark 0.31.2 | djot |
|---|---|---|
| spec prose | 25,411 words (`wc -w spec.txt`) | 4,025 words (`wc -w doc/syntax.md`) |
| examples | 652 (`spec.json`): 295 block-level, 357 inline, 132 of them emphasis | ~318 (lone `.` separator lines in djot.js `test/*.test`, an approximation) |
| implementations | 41 entries under 30 language headings, "recently maintained" (commonmark-spec wiki, `awk` count) | 7 (djot README), **none in Python** |
| stability | unchanged since 2024-01-28 (D5 §1.2) | *"isn't completely stable yet, minor future changes to the syntax are expected"* (README); npm `@djot/djot` 0.3.2, last published 2024-12-19 |

**Conceded.** djot's grammar is about six times smaller in prose.

The profile shrinks markdown's side of that comparison. blockspec identifies
blocks and treats inlines as opaque, so all 357 inline examples, emphasis
included, are out of scope. That leaves the 295 block-level examples. The
profile can then *refuse* setext headings, indented code and raw HTML other
than the marker, instead of parsing them, and detecting a construct is cheaper
than parsing it.

**The decisive asymmetry is the oracle.** The brief's §0 asks how blockspec
gets an adversary from day one, and lists *"treating an existing document
processor as the second opinion."* With CommonMark, an implementer in almost
any language has a mature parser to diff their block splitter against. That is
a free adversary, and it works on the first day:

```
python3 -I cmp.py <D8-dir> research/design-findings/*.md research/DESIGN.md
files 70 equal top-level counts 29
```

D8's 25-line standard-library splitter (`anchor_eval.blocks`) disagrees with
`markdown_it` about top-level block count on **41 of 70** of the research
repo's own files.

**Conceded.** That disagreement shows a naive subset is not correct as it
stands; the profile has to be specified. But the check that found it took one
command. With djot there is no Python oracle, and the reference implementation
says it may still change.

## 4. The cost of reversing each choice after draft 0

**Markdown, then djot: mechanical.** A profile is a subset, and mapping a
smaller language into a larger one is lossless in principle:

- `<!-- #name -->` becomes `{#name}` on the same line;
- the block structure maps one to one.

**Djot, then markdown: lossy.** Once authors use inline attributes,
key=value, spans or insert/delete marks, CommonMark has nowhere to put them
except raw HTML, which is the dialect this choice avoided. D5 §3.4's
mitigation, that pandoc converts a djot corpus to markdown, only holds if
draft 0 never used what makes djot djot. Reversing also deletes a parser from
`reference/` that every independent implementation has already copied.

**Common to both:** quote anchors that capture raw markup bytes (`*x*` against
`_x_`) break when the syntax changes, so either reversal rewrites the sidecars.
Anchoring on the parsed text, not the raw bytes, removes that cost either way,
and blockspec should require it.

**The net:** markdown keeps the djot option open, and djot spends the markdown
option. Under uncertainty, the reversible choice should go first.

## 5. Where the djot side is right

- **Conflict markers.** `=======` is a setext underline, so a real conflict
  becomes an invisible heading (DESIGN.md C6, *"four engines … all exit 0"*).
  Djot has no setext headings. A profile that refuses setext headings makes
  blockspec's own validator loud about it, but third-party renderers stay
  silent. This is a real point for djot.
- **Scattered namespaces.** DESIGN.md calls duplicate link labels, footnote
  labels and heading anchors *"the strongest argument for a stricter syntax."*
  The profile can refuse reference definitions and footnotes, but it is a
  restriction placed on markdown, not something markdown provides.
- **The author.** jgm wrote both formats and prefers djot (D5 §1.1).
- **A correction in djot's favour.** DESIGN.md §3(c) says djot *"ships no
  conformance suite"*. djot.js has 26 `.test` files, so that claim is
  overstated and should not be used against djot.

## Recommendation

**Choose markdown, as a pinned CommonMark 0.31.2 block-level profile:**

- region markers for author names;
- quote anchors in the referrer, taken on parsed text;
- the validator refuses setext headings, indented code, raw HTML other than
  the marker, and duplicate names;
- the reference parser is standard library only;
- every implementation is diff-tested against an off-the-shelf CommonMark
  parser on the corpora.

**What would change this:** a draft-0 requirement for typed attributes
(classes or key=value) on blocks or inlines. If one exists, choose djot, own
the parser, and accept the reversal cost in §4.
