<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# blockspec#3: the case for djot

This case argues **for djot**. It cites the same evidence as the case for
markdown, and concedes where markdown is right. Paths cite
kindspec/research at `d02c196`, blockspec at `1a969d0`, and upstream clones made
on 2026-10-14 (`jgm/djot` `d77f8a0`, `jgm/djot.js` `9790d4d`, `jgm/djot.lua`
`cbd3485`, `hellux/jotdown` `13f17f6`, `commonmark/commonmark.js` `8988869`,
`commonmark/commonmark-spec` `8a5f764`). The probes ran `@djot/djot` 0.3.2 from
`npm pack`, and pandoc 3.1.11.1 for CommonMark.

## The claim

Choose djot as a **pinned subset**. The reference implementation holds its own
stdlib-only parser for the block and attribute layer, and blockspec's conformance
cases own that subset. That is a *specification* dependency, not a code
dependency, and markdown carries a specification dependency of its own.

## 1. Attributes as anchors: markdown has no answer that is not a dialect

The brief has already decided the model: "an attribute triple on every node"
(DESIGN-BRIEF §1). Djot is the only candidate whose grammar carries that triple
natively. Probe:

    {#scram-threshold}                    ->  para ATTR={"id":"scram-threshold"}
    The reactor scram threshold is ...

Under CommonMark the same bytes give `<p>{#scram-threshold} The reactor…</p>`,
and `## Scram {#scram-threshold}` gives `<h2>Scram {#scram-threshold}</h2>`.

D8 §7.2 rejects `{#id}` for that reason only: CommonMark renders it "literally
as visible garbage". It picks `<!-- #name -->` instead, and lists what the
carrier must do: be invisible when rendered, be a name the author typed, sit on
its own line so that writing it is not a write to the prose. A djot block
attribute meets all three. It also lands **in the AST, on the node it names**.
An HTML comment is opaque raw HTML to every CommonMark parser, and "the target
is the block after the marker" is a rule blockspec would have to write itself.
That rule is a dialect, just one that happens to render cleanly. RFC 7764 §2,
quoted in D5 §1.3, says a markdown file cannot declare in-band which dialect it
is written in.

## 2. The spike's FOUND points at markdown's own naming mechanism

LOG.md §35 reports FOUND: 432 qualifying distinct units across 35 FOUND cells.
Split by mechanism:

    sed -n '2610,$p' LOG.md | grep '^| [a-z].* [QR] |' | awk -F'|' ...
    Q qualifying 167   on DELETED 0
    R qualifying 265   on DELETED 171

The R mechanism counts **region markers and heading slugs** (PRE-REGISTRATION-2
§3; the spike says `{#id}` "is not used"). Counting the record types in
`results/prereg3/run2/reproduction.md` (`grep -o 'block type \`R:[a-z]*\`' | sort | uniq -c`)
gives **270 `R:slug`, 0 region**. So most of the silent mis-resolutions found in
real history, 265 of 432 units, come from the **one naming mechanism markdown
has natively**: a name derived from heading text. In 171 of those 265 units the
oracle says the target was deleted, and the derived name still resolved, without
any error, to a different section.

An authored id does not depend on the heading text, so editing the heading
cannot move it. If the block it sits on is deleted, the id goes with it, and the
resolver reports a loud `#REF!`. **I concede the limit of this.** The spike never
measured authored ids, because every corpus is markdown. My claim is narrower:
the measured silent-wrong is concentrated in the derived-name mechanism, the
untested remedy is an authored name, and only djot carries an authored name
inside its grammar. The 167 Q units are quote anchors, and the choice of syntax
does nothing for them.

## 3. What a parser dependency costs an independent implementation

rowspec's rule is that "a dependency there is a dependency every independent
implementation inherits" (rowspec AGENTS.md). Here is the measured cost.

| | djot | CommonMark |
|---|---|---|
| spec (`wc -lw`) | `doc/syntax.md`: 834 lines, 4,025 words | `spec.txt`: 9,814 lines, 25,583 words |
| executable examples | per implementation, and they have diverged: djot.js 318, djot.lua 255, with the same files differing (`diff -rq`) | 655 in the spec itself |
| implementations | 7, in JS, Lua, Prolog, PHP, Rust, Go and Haskell (djot README §Implementations) | ~45 across 25+ languages (DESIGN.md §3c) |
| reference parser LOC | djot.js attributes+block+inline+parse+ast: 4,583, **zero deps**; djot.lua attributes+block+inline: 1,780 | commonmark.js blocks+inlines+common+node: 2,636, **plus `entities` and `mdurl`** |
| license | MIT (djot, djot.js, djot.lua, jotdown) | BSD-2 (commonmark.js); spec CC-BY-SA |
| age | first commit 2022-07-11; last push 2026-10-10 (djot.js) | first commit 2014-08-13; still 0.31.2 |
| Python implementation | none | several, none of them stdlib |

The point that decides this row: **neither format is in Python's standard
library.** `sys.stdlib_module_names` has no markdown or djot module. So
"stdlib-only" does not separate the two. Either `reference/` contains its own
parser, or it parses nothing and splits blocks by lines. If blockspec parses
nothing, it has no attribute triple, and that contradicts §1 of the brief. If it
does parse, the question is which grammar is cheaper to implement from its spec
in a new language. Djot's spec is a sixth of CommonMark's in words. And
blockspec only needs the block layer, where djot guarantees that "the
contribution a line makes to block-level structure never depends on a future
line" (`syntax.md` line 358). CommonMark breaks that with setext headings and
lazy continuation lines. The next section shows that this is a correctness
issue as well as an effort issue.

**Conceded.** An implementer in Java, C#, Swift or Python finds no djot parser
to pick up. A CommonMark parser exists almost everywhere. But a CommonMark parser
still lacks the attribute convention, so that implementer writes a layer either
way. Djot's line counts are no smaller than commonmark.js's. The saving is in
spec ambiguity, not in code size.

## 4. Stock git's own output, under each grammar

DESIGN.md C6 shows that CommonMark *consumes* a conflict marker. Reproduced:

    pandoc -f commonmark: <h1>Intro paragraph. <<<<<<< HEAD The limit is 14 days.</h1>
                          ...seven nested <blockquote>, then <p>branch</p>
    djot:                 one para; "<<<<<<< HEAD", "=======", ">>>>>>> branch"
                          kept as literal text

Djot has no setext headings, and its block quote marker needs a space after `>`,
so all three marker lines survive and are visible. That is not a parse error:
djot is not loud here, but it is not deceptive either. Under the
correctness-may-not-depend-on-a-hook rule (org AGENTS.md §5), a grammar that
shows git's markers as they are beats one that turns them into headings.

## 5. Where markdown is right

- **Ecosystem.** D5 §3.3 measured `@djot/djot` at 1,332 npm downloads a week
  against remark's 50.9 million. `npm view @djot/djot time.modified` still
  returns 2024-12-19.
- **GitHub does not render djot.** The github/markup README lists `.md`, `.rst`
  and `.adoc`, and does not list `.dj`.
- **Djot is unstable and has no spec-owned suite.** djot.net says "Djot isn't
  completely stable yet". The two jgm suites diverge. Whatever subset blockspec
  pins, it becomes that subset's conformance authority.
- **Djot has silent failure modes of its own.** In D5 §3.2(b), `# Heading {#intro}`
  silently drops the id. My probe shows a duplicate `{#scram-threshold}` parses
  with **no warning**. So the resolver must still apply D8's rule that zero
  matches or more than one is `#REF!`, and a lint must flag the trailing-attribute
  shapes.
- Every corpus blockspec has measured is markdown. The existing evidence
  transfers to djot by argument, not by measurement.

## 6. The cost of reversing after draft 0

Each direction costs the same mechanical work. Every fixture changes bytes
(fixtures are exact bytes, org AGENTS.md §5). Every stored quote anchor's
`base` blob changes. And conversion has to go through the AST, because `*x*`
means strong in djot and emphasis in markdown. djot.js exports `toPandoc` and
`fromPandoc` (D5 §3.4), so the tooling exists both ways.

The asymmetry is in what each choice locks in.

- **Djot to markdown.** Ids drop down to D8's HTML-comment convention. That is
  lossy only for inline attributes, and blockspec does not need those to anchor
  blocks. Users' files are djot written for blockspec, so their number is
  bounded by blockspec's own adoption.
- **Markdown to djot.** Draft 0 will have specified a convention: comment
  markers, a "block after the marker" rule, and a slug algorithm, which is the
  mechanism §2 found silently wrong. That convention is the legacy dialect you
  would be migrating away from. Markdown would also attract adopters faster,
  so a reversal later strands more files. **Reversal cost grows with
  adoption, and adoption grows faster on markdown.** That argues for settling
  the attribute carrier before draft 0, not after.

## Recommendation, and what would change it

**Djot**, under three conditions:

1. Pin `syntax.md` by commit, and specify a subset: block structure and block
   attributes only.
2. Put a stdlib-only parser in `reference/`. It is a vendored grammar, not an
   import, so the escalation for "a new runtime dependency" in org AGENTS.md §7
   does not fire, and blockspec owns it.
3. Make the conformance cases own the subset, including the silent-drop and
   duplicate-id shapes.

**What would reverse this.** If blockspec#4 ("what is a block") or the anchor
design drops authored names entirely, and anchoring becomes quote-only, then
nothing needs attributes and markdown's line-level block splitting is enough.
§2's evidence cuts the other way, though. If the owner ranks GitHub rendering
above an in-grammar anchor carrier, that is a preference, and it would also
decide for markdown.
