<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Adjudication 0001: djot or markdown

blockspec#3. The brief (`DESIGN-BRIEF.md` §2) listed the question as open: the
research says djot, *"but only if you own a parser dependency you are willing to
maintain"* (kindspec/research `design-findings/D5-document-models.md` §0 item
3). The question is not settled by measurement, so the org contract
(kindspec/.github `AGENTS.md` §4, "When measurement cannot settle it") has one
case argued for each side from the same evidence, and an adjudication written
here. The format follows kindspec/research `design-findings/ADJUDICATION.md`.

The two positions, each committed verbatim apart from an SPDX header and one
reworded opening sentence:

- **djot** ([`0001-syntax/djot-case.md`](0001-syntax/djot-case.md)): a pinned
  subset of djot (block structure and block attributes), with a
  standard-library-only parser in `reference/`. Its main argument is that only
  djot carries an authored identifier inside its grammar.
- **markdown** ([`0001-syntax/markdown-case.md`](0001-syntax/markdown-case.md)):
  a strict block-level profile of CommonMark 0.31.2, with the region marker
  `<!-- #name -->` from D8 §7.2 as the only convention and inline content kept
  opaque. Its main argument is that the reason markdown was disqualified has
  since been overturned.

Pins: blockspec `1a969d0`; kindspec/research `d02c196`. Upstream clones made
on 2026-10-14: `jgm/djot` `d77f8a0`, `jgm/djot.js` `9790d4d`, `jgm/djot.lua`
`cbd3485`, `commonmark/commonmark.js` `8988869`, `commonmark/commonmark-spec`
`8a5f764` (and its tag `0.31.2`). Probes used `@djot/djot` 0.3.2 (`npm pack`),
pandoc 3.1.11.1 (`-f commonmark`) and markdown-it-py 3.0.0 (`commonmark`
preset).

## Decision

**Decided, 2026-10-14: markdown, as a pinned CommonMark 0.31.2 block-level
profile.**

The evidence below leaned this way, but one input was an owner preference
that no measurement can supply: whether a blockspec document must render and
edit correctly in today's markdown tools. The owner answered **yes** (see *The
owner's answer*), and that answer decides it. The brief's §1 sentence that
called markdown disqualified is amended to point here.

The decision is conditional on blockspec#4 ("what is a block?") in one
specific way, stated under *What would reverse it*. #4's measurement,
kindspec/research PR #17 (`experiments/D8-block-definitions/`, head
`8b9c33c`), parses every file as CommonMark (markdown-it-py 3.0.0, preset
`commonmark`). Most of its candidate definitions are CommonMark tree nodes, but
not all: `e` and `e2` (sections) are ranges between headings, and `a0` and `f0`
are D8's blank-line chunks. Neither kind adds syntax; a section is derived
from heading ranks the CommonMark tree already carries. The measurement also
enables GFM tables, which CommonMark 0.31.2 does not
have; whether the profile admits pipe tables or leaves them as paragraphs is
left to #4 and the profile's specification.

## The factual disputes, settled

The two cases disagreed on several facts. Each was re-measured.

| claim | [djot case](0001-syntax/djot-case.md) | [markdown case](0001-syntax/markdown-case.md) | measured | command |
|---|---|---|---|---|
| CommonMark implementations | ~45 (quoting research `DESIGN.md` §3c) | 41 under 30 language headings | **54** entries under "Recently maintained", across 30 language headings; 63 in the whole list. 15 match the wrapper grep; by entry text at least 18 wrap, bind or compile another library (the grep misses lcmark, the PECL cmark extension and cmark-emscripten, and counts DefinitelyTyped, which is type bindings rather than a parser), so **at most 36** parse on their own. The count of 41 missed 13 entries indented with leading spaces. | `curl -s https://raw.githubusercontent.com/wiki/commonmark/commonmark-spec/List-of-CommonMark-Implementations.md`, then count `^[ \t]*[-*] \[` per `## ` section, and `grep -ciE 'wraps\|wrapper\|binding'` inside the first section |
| djot implementations | 7 | 7, none in Python | **7** (JS, Lua, Prolog, PHP, Rust, Go, Haskell); none in Python | `jgm/djot` README, "Implementations" |
| CommonMark spec size | 9,814 lines, 25,583 words, 655 examples | 25,411 words, 652 examples | **Both right, at different commits.** Tag `0.31.2`: 25,411 words, 652 examples. Tip `8a5f764` (17 commits later): 25,583 words, 655 examples. The 0.31.2 release is the right pin. | `git show 0.31.2:spec.txt \| wc -w`; count the lines opening an example fence (a run of backticks followed by `example`) |
| inline vs block examples (0.31.2) | — | 357 inline, 295 block | **357 / 295**, counting the one-example "Inlines" and "Precedence" sections as inline; 132 are emphasis | `spec.json` grouped by `section` |
| djot spec size | 834 lines, 4,025 words | 4,025 words | **834 lines, 4,025 words** | `wc -lw doc/syntax.md` |
| djot examples | djot.js 318, djot.lua 255, diverged | ~318 | **318 and 255**; 22 differing or one-sided entries between the two `test/` directories | `cat test/*.test \| grep -c '^\.$'`; `diff -rq` |
| parser size | djot.js 4,583 (zero deps); djot.lua 1,780; commonmark.js 2,636 plus `entities`, `mdurl` | — | djot.js `attributes+block+inline+parse+ast` = **4,501**, `"dependencies": {}`; djot.lua `attributes+block+inline` = **1,780**; commonmark.js `blocks+inlines+common+node` = **2,571**, depends on `entities`, `mdurl`, `minimist`. Both djot.js figures and the commonmark.js figure in the djot case are slightly off; the direction is unchanged. The block layers alone: djot.js 1,540, djot.lua 1,101, commonmark.js 1,045 (+114 `common.js`). Both block layers import their inline parser. | `wc -l` at the pins above |
| djot stability | "isn't completely stable yet" (djot.net) | same quote, attributed to the README | The quote is on **djot.net**; the `jgm/djot` README does not contain "stable". `@djot/djot` 0.3.2, `time.modified` 2024-12-19. | `curl -sL https://djot.net/ \| grep -i 'completely stable'`; `npm view @djot/djot time.modified` |
| spike FOUND units | 167 Q units, 270 `R:slug`, 265 R units, 171 R on DELETED | 143 Q, 270 R, all `R:slug` | **Both right; they count different things.** `verdict.json` FOUND cells: **432 distinct units, 167 Q and 265 R**; `wrong_on_deleted` is **0 Q and 171 R**. `reproduction.md` records **413 packets: 143 Q and 270 R**. Every R record is `R:slug`; none is a region marker. Block types of the 143 Q records: 76 heading, 64 prose, 3 list. | `spike/results/prereg3/run2/verdict.json`, summing `qualifying_distinct` and `wrong_on_deleted` over cells whose `verdict` is `FOUND`, keyed by the cell's last field; `grep -o 'mechanism [QR], unit' reproduction.md \| sort \| uniq -c`; the same tally of each record's `block type` field |
| region markers in the corpora | — | "no author-chosen name failed" | **0** lines matching D8's `REGION` pattern in the 1,564 `.md` files of the 488 exported prereg 3 packets. The corpora contain no authored names, so the spike measured none. | `grep -rlP '^\s*<!--\s*#[a-z0-9][a-z0-9-]*\s*-->\s*$' --include=*.md spike/results/prereg3/export/packets` (the pattern of research `experiments/D8-identity/e6_transclude.py` at `d51ce09`), with a positive control on `<!-- #scram-threshold -->`, which matches |
| conflict markers | CommonMark consumes them; djot keeps them | CommonMark turns `=======` into a setext heading | **Both right.** A real `git merge` conflict (exit 1) under CommonMark (pandoc and markdown-it agree): `<<<<<<< HEAD` plus the first side become one `<h1>`, `=======` disappears into it, and `>>>>>>> br` becomes seven nested `<blockquote>`s. Under djot 0.3.2: one paragraph, all three marker lines kept as literal text, no warning. Neither parser fails. | a two-branch repository that edits the same line; `pandoc -f commonmark -t html`, markdown-it `commonmark`, `djot.parse` |
| `{#id}` silent failures in djot | duplicate ids pass silently; trailing heading attribute dropped | — | **Duplicate `{#x}` on two blocks: both get `id="x"`, no warning.** `# Heading {#intro}`: id dropped, and the `warn` callback reports "Ignoring unattached attribute"; the HTML output is silent about it. | `djot.parse(src, {warn})` |

### Is `<!-- #name -->` plus "the block after the marker" a dialect?

**No, but the djot case is right that blockspec must specify the binding.**

A dialect, in the sense RFC 7764 §2 worries about, is text that conforming
parsers turn into different trees. The marker does not do that. markdown-it's
CommonMark mode gives `html_block` followed by the next block's opening token in
every probe:

    marker, then paragraph                -> html_block, paragraph
    marker, blank line, paragraph         -> html_block, paragraph
    paragraph, marker, paragraph          -> paragraph, html_block, paragraph
    marker inside a list item             -> ... paragraph, html_block, paragraph
    marker, then list                     -> html_block, bullet_list
    marker, then ATX heading              -> html_block, heading

The third row matters: an HTML comment interrupts a paragraph (block
type 2 may), so a marker written on the line after a paragraph still names the
next block. The same placement in djot (`{#a}` on the line after a paragraph)
becomes an *inline* attribute on a soft break: djot 0.3.2 parses
`One.\n{#a}\nTwo.` as a single paragraph, and no block gets the id, with no
warning.

What the marker convention adds is a **meaning** over an unchanged tree: "the
name binds to the next sibling". That rule is blockspec's to write. It is a
profile convention, not a dialect. But djot needs blockspec-specific binding
rules too. A `{#a}` placed before a heading gives the id to the implicit
`section`, not to the heading. And a marker indented four spaces is an
indented code block in CommonMark and a block attribute in djot. Both formats
leave blockspec with binding rules to specify and test. Djot defines more of
them in its own grammar; CommonMark leaves more to the profile.

## 1. "Attributes are non-negotiable, which is why markdown is disqualified"

**Answered by the markdown case, and this is the point that decides the
question.**

The brief's sentence (§1, "The tree is not sufficient") reads: anything spanning
structure must live in standoff with stable anchors, *"which is the real reason
attributes are non-negotiable, and the real reason markdown is disqualified"*.
That derives from research D5 §0 item 5 and §5.4 item 3 (bold removed):
*"Therefore stable per-block identity in the canonical text is mandatory, not
optional. A standoff layer needs something to point at. Markdown cannot provide
it (§1.1). Djot can (`{#id}`), org can (`:ID:`), TEI does (`@xml:id`), Portable
Text does (`_key`)."*

D8 measured that premise and replaced it. Its §6 table, at 25 commits of real
editing: a stored `^id` under stock git is correct 80.0% of the time, a
two-stage quote anchor 92.9% with 0.00% silent-wrong. Its §7.3 puts anchors in
the referrer, and its invariant I7 says a reference *"may write nothing into the
artifact it refers to"*. The brief adopted that: *"A prose block gets NO minted
id."*

So standoff anchoring no longer needs an attribute in the file. What remains in
the file is **a name an author chose**, rarely (D8 §7.2 puts the density at
0.34% of blocks in Obsidian's own vault). D8 §7.2 picked the HTML comment as the
carrier for that name, because it is invisible in every renderer including
GitHub's, while `{#custom-id}` renders as visible text under CommonMark.

The in-memory attribute triple of the brief's §1 is unaffected. It is a model
property, "derived and disposable", and a CommonMark tree can be lifted into a
Pandoc-shaped AST with empty attributes plus the names the markers supply.

**What the djot case gets right here:** djot's `{#id}` lands in the AST on the
node it names, with the binding defined by djot rather than by blockspec. That
is real, and it is worth less than it looks, because blockspec has to pin and
test the binding rules either way (see the probe above).

**What would change this:** a draft-0 requirement for *typed* attributes
(`classes` or `key=value`) written in the file, on blocks or inlines. CommonMark
has no carrier for those short of raw HTML. Both cases agree on this.

## 2. "The spike's FOUND points at markdown's naming mechanism"

**Partly conceded; it does not separate the two formats.**

The figures are settled above: 432 qualifying units in the FOUND cells,
167 Q and 265 R. Every R record in `reproduction.md` is a heading slug. The
djot case is right that the silent mis-resolutions concentrate in derived names,
and that in 171 of 265 R units the oracle says the target was deleted and the
slug resolved to something else.

But djot derives heading slugs too. `doc/syntax.md` line 781: *"Identifiers are
added automatically to any headings that do not have explicit identifiers"*,
with a numerical suffix for uniqueness. The remedy the evidence points at is
**do not treat derived names as durable references**. That rule is available in
both formats. The 167 Q units are quote anchors, which write nothing into the
target and behave the same under either syntax.

The markdown case's line "no author-chosen name failed" is true and empty:
the exported packets contain zero region markers, so no authored name was ever
measured. The spike gives no evidence about authored names in either carrier.

**Net: the FOUND says blockspec should be built (LOG §35) and that derived names
must not be durable. It gives no evidence for one syntax over the other.**

## 3. What a parser costs an independent implementation

**Both cases agree on the framing, and it is correct: Python's standard library
parses neither format.** `reference/` holds a hand-written parser either way,
so "stdlib-only" does not distinguish them. Neither choice adds a runtime
import, so the escalation in the org contract §7 ("a new runtime dependency in a
`reference/` tree") does not fire for either.

What separates them:

- **Grammar size favours djot.** About one sixth of CommonMark's prose
  (4,025 words against 25,411), and its block layer is line-local: *"The
  contribution a line makes to block-level structure never depends on a future
  line"* (`syntax.md` lines 358–360). CommonMark's lazy continuation lines and
  setext headings break that.
- **Code size does not separate them.** The block layers are 1,101–1,540 lines
  in the djot references and 1,159 in commonmark.js. The djot case concedes
  this.
- **The second opinion favours CommonMark.** The brief's §0 makes the first
  decision *how this format gets an adversary from day one*, and names "an
  existing document processor as the second opinion" as one answer. With
  CommonMark, an implementer in nearly any language can diff their block
  splitter against a mature parser (54 listed implementations under 30
  language headings, at most 36 of them not wrappers). With djot, that
  oracle exists in seven languages, and its two reference test suites
  disagree with each other.
- **Stability favours CommonMark.** 0.31.2 has been the release since
  2024-01-28; djot says minor syntax changes are expected, and its npm package
  has not been published since 2024-12-19. A pinned djot subset makes blockspec
  the conformance authority for that subset, which both cases accept.

A CommonMark *profile* narrows its side: the profile can refuse setext
headings, indented code, link reference definitions and raw HTML other than the
marker. Refusing still needs detecting, and detecting a setext underline needs
paragraph context. The profile shrinks the work; it does not remove it.

## 4. Conflict markers

**Conceded to djot, at a smaller weight than either case gives it.**

Re-measured above: CommonMark keeps `<<<<<<< HEAD` visible but as heading text,
hides `=======` (it becomes the setext underline), and turns `>>>>>>> br` into
seven nested block quotes; djot shows all three as literal text. Neither fails
loudly.

The weight is smaller because blockspec's own reader is not a CommonMark or djot
renderer. Git's markers are column-0 runs of seven `<`, `=`, `>` (and `|` for
diff3). blockspec's validator can refuse any file containing them, as a line
scan before any block parsing, in either format, and the case tree can pin that
behaviour. Where djot really wins is in **third-party renderers**: a conflicted
file shown in a forge or editor preview. Djot keeps all three marker lines
visible there as written; CommonMark shows the first as a heading, hides the
second and turns the third into block quotes. GitHub does not render djot at
all, which makes that advantage hypothetical on the largest forge today.

## 5. Ecosystem and rendering

**Markdown, by a wide margin, and this is where the owner's preference enters.**

D5 §3.3 measured `@djot/djot` at 1,332 weekly npm downloads against remark's
50.9 million. GitHub's markup list includes `.md` and not `.dj`. Every corpus
blockspec has measured is markdown, so markdown's evidence is measured and
djot's is argued from it. Whether rendering on GitHub and in existing editors
matters to blockspec's users is not a fact this document can look up.

## 6. The cost of reversing each choice after draft 0

Common to both directions, and the same size:

- every fixture changes bytes (org contract §5: fixtures are exact bytes);
- conversion goes through an AST, because `*x*` is strong in djot and emphasis
  in CommonMark; pandoc reads and writes both;
- every stored quote anchor whose quote spans markup breaks. **The anchor design
  should take quotes over parsed text, not raw bytes,** which removes this cost
  in both directions; the markdown case proposes this and it should go to the
  anchor work regardless of how #3 lands;
- the `reference/` parser is replaced, and every independent implementation
  replaces its own.

What differs:

- **Markdown, then djot.** The profile is a block-level subset. Block structure
  maps one to one, and `<!-- #name -->` maps to `{#name}`. The one hazard is
  placement: a marker directly after a paragraph line binds under CommonMark
  and turns inline under djot, so the conversion must insert a blank line.
  Mechanical.
- **Djot, then markdown.** Mechanical *if* draft 0 pinned only block structure
  and block ids: `{#name}` maps back to the marker. Lossy if draft 0 admitted
  inline attributes, spans, or insert/delete marks, which have no CommonMark
  carrier but raw HTML. The djot case's own proposed subset would keep this
  mechanical; the subset is the thing to watch.
- **Adoption.** The djot case argues that markdown attracts adopters faster, so
  a later move away from markdown strands more files. That is true, and it
  argues for settling the carrier before draft 0, which this document does. It
  does not change which choice is easier to undo: a subset that maps into djot
  is easier to leave than a subset that might not map back.

**Net: markdown is the more reversible choice, and the asymmetry is bounded by
what draft 0 admits.**

## What each side got right

**The djot case:**

- the binding of a marker to its block is blockspec's rule to write, not
  CommonMark's;
- the spike's silent-wrongs concentrate in derived names (265 of 432 units);
- djot's block grammar is smaller and line-local, and its spec is about a sixth
  the size;
- git's conflict markers survive djot and are consumed by CommonMark;
- djot's own silent failures (duplicate ids pass without warning; `{#a}` after a
  paragraph line turns inline) mean the resolver must apply D8's zero-or-many
  rule whichever format wins;
- an earlier research claim that djot "ships no conformance suite" is overstated
  (djot.js has 26 `.test` files). The markdown case concedes this too.

**The markdown case:**

- the brief's reason for disqualifying markdown rests on a premise D8 measured
  and replaced; the brief's own "no minted id" rule is the evidence;
- the spike FOUND is syntax-neutral: Q is the same under any syntax, and slugs
  exist in both formats;
- "stdlib-only" does not distinguish the two formats, since neither is in the
  standard library;
- CommonMark gives every implementer a mature second opinion, which is the
  brief's §0 process question;
- CommonMark is stable; djot says it is not;
- anchoring on parsed text removes the sidecar rewrite from either reversal.

**Both cases** were wrong on one fact each, neither of them decisive: the
markdown case's implementation count of 41 (54 listed, at most 36 not wrappers)
and its attribution of the stability quote to the README; the djot case's parser
line counts (4,501 and 2,571, not 4,583 and 2,636).

## What would reverse it

Either of 1–2 makes the answer djot; 3 reopens the question.

1. **blockspec#4, or the anchor design after it, needs typed attributes in the
   file**: `classes` or `key=value` on blocks (for example, typed semantic
   containers in the DITA-specialization sense of D5 §6.3). CommonMark has no
   carrier for those short of raw HTML, which would be a dialect.
2. **blockspec#4 defines a block that is not a node of CommonMark's tree.** The
   marker binds to the next sibling node. If the unit of identity needs a
   boundary the CommonMark tree does not draw (a `:::` fenced div is djot's tool
   for that; CommonMark has none), the profile has to add syntax, and at that
   point it is a dialect. Node outcomes of #4 (a top-level node, a node at any
   depth, list items, leaf blocks) are CommonMark tree nodes and do not trigger
   this. Neither does a **section** outcome (#17's `e` or `e2`): a section is
   not a single node, but it is derived from heading ranks with no added syntax,
   so the profile still adds nothing. Nor do D8's blank-line chunks (`a0`,
   `f0`), which are a line rule over the same bytes. This item fires only if the
   boundary needs new syntax in the file. Region spans that may *overlap* (D8
   §7.2's begin/end pair) need marker comments in djot as well, since djot's
   divs nest but cannot overlap; that case does not separate the formats.
3. **The owner's answer below changes to "no"**: forge and editor rendering no
   longer matter, and the stricter syntax is preferred. The decision then rests
   on grammar size and conflict-marker visibility (djot) against stability and
   the second opinion (CommonMark). That is closer, and still leans markdown on
   the brief's §0 grounds, but it becomes a preference rather than a finding.

The evidence that would *not* reverse it: anything about quote anchors (syntax-
neutral) or about heading slugs (both formats derive them).

## The owner's answer

The question put to the owner:

> **Should a blockspec document render and edit correctly in today's markdown
> tools (GitHub and other forge previews, Obsidian, ordinary editors), yes or
> no?**
>
> - **Yes**: blockspec is a CommonMark 0.31.2 block-level profile. Authored
>   names use `<!-- #name -->`. The brief's §1 sentence "the real reason
>   markdown is disqualified" is amended to cite this adjudication.
> - **No**: the decision is reopened on the narrower grounds in *What would
>   reverse it*, item 3, with djot as a pinned block-and-block-attribute subset.

**Answer, 2026-10-14: yes.** blockspec documents must render and edit
correctly in today's markdown tools.

## What draft 0 carries

- **CommonMark 0.31.2**, pinned by tag, as a block-level profile; inline
  content is opaque text.
- **One convention, the region marker of D8 §7.2**, in two forms:
  `<!-- #name -->` on its own line names the next sibling block, and the
  begin/end pair `<!-- #name:begin -->` / `<!-- #name:end -->` names a span,
  which may nest or overlap. A name that matches zero targets, or more than
  one, is `#REF!(name)`.
- **Refusals**, each a fixture: setext headings, indented code blocks, link
  reference definitions, raw HTML other than the markers, duplicate names, and
  git conflict-marker lines.
- **Heading slugs stay resolvable but are not durable.** Per D8 §7.2's order
  a name is tried against region markers first, then slugs; a slug is a
  convenience, not a reference blockspec promises to keep. The spike's 265 R
  units are the reason.
- **Proposed, not yet the answer to the brief's §0:** a second opinion in CI,
  an off-the-shelf CommonMark parser's block tree diffed against the
  reference's on the corpora. A test-time dependency only; `reference/` stays
  standard-library-only.

## Addendum, 2026-10-14: the marker line and heading slugs

The owner's decisions of 2026-10-14.

**The marker line.** A region marker is a line whose content, after any
container prefix, matches

    ^[ \t]*<!--[ \t]*#[a-z0-9][a-z0-9-]*(:begin|:end)?[ \t]*-->[ \t]*$

and is indented at most three spaces. Four or more spaces make the line an
indented code block, which this decision refuses. The only spacing allowed is
spaces and tabs, inside and around the comment, so `<!--#intro-->` and
`<!--  #intro  -->` are both markers. Other whitespace, such as a no-break
space, is not. Nothing else may share the line. An HTML comment that does not
match is raw HTML, and is refused as raw HTML.

**Heading slugs** follow GitHub's rule, character for character as
github-slugger 2.0.0 computes it. The heading's raw content is lower-cased,
every character in the character class of github-slugger 2.0.0's
`regex.js` is removed, and each space becomes `-`. That class is its own, not
a Unicode category rule: it removes `²`, and keeps `‿`, `Ⓐ`, `-` and `_`.
Every heading has a slug, at any depth, with one exception. A
heading whose raw content holds an inline-markup character, one of `*`, `_`,
`` ` ``, `[` or `<`, has **no slug**, because its raw content is not the text
GitHub slugs, and a reference to it is unresolved, `#REF!(name)`. No `-1`
suffix is added to tell duplicates apart, so two headings with one slug leave
that slug unresolved, as *What draft 0 carries* already says of any name that
matches more than one target.
