<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Adjudication 0003: anchors and transclusion

The brief (`DESIGN-BRIEF.md` §2) lists quote-anchoring's failure modes as
open. 0002 settled where stage 1 of an anchor lands (the leaf) and left three
things to the anchor work: how an anchor carries a disambiguator for a leaf
that was already repeated when it was made (§2), how a selection that crosses
leaves is written (§2), and how a transclusion is written down: 0002 §4
decides what a transclusion addresses, and neither adjudication gives a
syntax for one. 0001 §6 asked that anchors quote parsed text, not
raw bytes.

The question this document decides:

> How do comments, suggestions and transclusions anchor to text in a
> blockspec document, so that after edits, and after a stock `git merge` of
> two branches, an anchor either lands on the right text or is refused
> loudly, and never lands silently on the wrong text?

Unlike 0001 and 0002, this question was not argued as two opposing cases. A
single design was put to the owner as thirteen questions, each with a
recommended answer and the alternatives it was weighed against, and the
owner decided all thirteen on 2026-10-16. This document records each
decision with its reasoning, the rules that follow, and what the design does
not prevent.

**What the evidence is.** Each rule below is argued from the edit shape it
exists for, and the sources cited are public. The conformance cases that
follow this document are where each shape becomes a case that can fail, and
they will be written by an author who has not read the resolver. **No figure
in this document measures these rules on real history.** That measurement is
the first item under *What would reverse it*.

Pins: blockspec `26e00f2` with `SPEC.md` from kindspec/blockspec#40;
kindspec/research `244dff0`.

**Amended by 0004** (2026-10-18), after the replay §12 asks for: §4's
near-copy check on an unchanged leaf compares words, and §5's context filter
needs, for a comment on a paragraph or heading, one side of the context and
the span's neighbouring code points; a suggestion needs both sides,
compared on prose with whitespace runs as one space, and any record on a
code block or table, before or after the edit, needs both sides exactly. §9's R2 and R3 widen with them
(`0004-anchor-refusals.md`; `SPEC.md` §11.12).

## Decision

**Decided, 2026-10-16.**

| | question | decided |
|---|---|---|
| Q1 | where comment and suggestion records live | one file per record, in `<doc>.notes/` beside the document. The directory says which document a record belongs to |
| Q2 | whether a comment follows a moved paragraph | yes, marked `MOVED`. A suggestion never applies to a moved leaf |
| Q3 | where `base` comes from under squash and rebase | the format refuses an anchor whose `base` is unreachable, as `base-unavailable`. Before landing, while `base` is still reachable, a tool MAY re-base each record that resolves onto the branch head, and MAY check in CI that it did. A record that does not resolve keeps its `base` and is reported, and does not fail the landing |
| Q4 | a target's author moves a name to other content | the transclusion is refused until the referrer re-pins |
| Q5 | how a transclusion is written | a paragraph that is one link, titled `transclude`: `[t](doc.md#name "transclude")`. **This amends 0001** |
| Q6 | whether a moved leaf whose old place now holds new text is refused (the refill rule) | yes, kept |
| Q7 | whether resolution reads the merge's parents | not in the format. A tool MAY read them, as a check that only adds refusals |
| Q8 | deleting records | records are not deleted in normal use. A purge removes a whole thread in one commit. A reply whose parent is missing is `#REF!(reply-to)` |
| Q9 | a different document at the same path | the notes directory is authoritative. A rename moves the notes directory in the same commit, and a record id found in two notes directories is warned on. A tool MAY track document identity beyond that |
| Q10 | which suggestions apply | only a record whose `status` is `open` |
| Q11 | writing an accepted suggestion back into the file | only when the span maps exactly from the normalised leaf to the raw text. Otherwise the suggestion is stale, `unmappable-offset` |
| Q12 | editing one of two identical paragraphs | the narrowing: an edited leaf is refused for an exact copy of its old text only when that copy is paired with nothing |
| Q13 | the context stored around a span | 32 code points on each side, and no comment-only fallback, until a replay of real history prices the detachments |

`SPEC.md` §11 carries the rules this decision produces.

**Details this document fixes beyond the thirteen answers**, all decided
with them:

- the resolution reasons and their names: `document-missing`,
  `base-unavailable`, `not-in-profile` (a snapshot the profile refuses, such
  as a file committed with conflict markers), `record-inconsistent`,
  `unaccounted-copy`, `repeat`, `near-copy`, `refilled-gap`, `exact-copy`,
  `crowded-gap`, `span-ambiguous`, `name-rebound` and `pinned-<reason>`, and
  `#REF!(name)` for a transclusion name that binds zero or several targets;
- a pinned name that binds nothing in its pinned blob is
  `record-inconsistent`;
- a record is `record-inconsistent` when its `prefix` or `suffix` is shorter
  than 32 code points while the leaf's edge is further away, or when its
  `span` is empty;
- `replace` is written into the document exactly as stored, never
  normalised.

## 1. What the format guarantees, and what it cannot

**The guarantee.** A resolver reads two snapshots: `base`, the blob of the
document that the anchor was made against, and the current text. **An anchor
resolves only where every witness it has agrees. Any disagreement, any tie
and any missing witness is loud**: the anchor is shown in place, with its
reason and the text as it stood at `base`. The witnesses are:

- the correspondence between `base`'s leaves and the current leaves (§4);
- the absence of an unaccounted near-copy of the anchored leaf (§4);
- the quote of the span with its stored context (§5);
- a character alignment of the old leaf onto the new one (§5).

**The limit.** Some edits leave current bytes that are exactly what a
legitimate edit would also have produced. No resolver that sees only the two
snapshots can tell such a pair apart. §9 names the four mechanisms, and says
which reach suggestions. What separates them is *which edit happened*, not
*what the text is*, and git alone does not reliably keep that.

**So the format is the floor.** It is safe against every edit shape the bytes
can distinguish, and it documents the rest. A tool that knows more, such as
merge parents, the history of renames, or what the author meant, MAY use it
to refuse more (Q7, Q9), and never to turn a refusal into a resolution. Q3 is
of another kind: it re-bases records onto the version that lands, before
their `base` becomes unreachable. Nothing in the format requires any of
these, and correctness may not depend on them (org contract §5: no merge
driver, filter or hook).

**Why refusal beats resolution.** kindspec's invariant I3, from research
`DESIGN.md`: *"A broken reference fails visibly and locally: never zero,
never empty, never stale, never plausible."* The same document's §16, risk
1, says I3 *"is aimed at the wrong failure"*: *"The dangerous case is a
reference that still* resolves*, to something else."* An anchor on the wrong
text is that case. Brush, Bargeron, Gupta and Cadiz (CHI 2001, quoted in
research `design-findings/D8-identity.md` §3.5) found user satisfaction
correlated −.34 with edit severity for annotations that were found, and +.72
for annotations that were orphaned. D8 reads that as users preferring an
honest orphan. 0002 §2 applied the same rule when it declined the fallback
from leaf to block.

**Why a quote and its context are not enough.** D8 §3.4's two-stage resolver
(the block first, then the span inside it only) made no silent wrong at
rust-book gaps 5 and 25, against 1.73% and 15.34% for a one-stage search of
the whole file. But `spike/LOG.md` §9 then built a single commit that defeats
its first stage: reword the anchored paragraph, and quote its original
wording in a new appendix. The old paragraph's exact text now sits in the
appendix, D8's block resolver lands there under both its naive and its hard
policy, and it is wrong. No merge is involved. The design below
adds `base` and the correspondence as witnesses so that a verbatim copy of
the old text is not, on its own, evidence of where the anchored text went.

## 2. Where anchors live (Q1, Q8, Q9)

**Standoff, not inline.** Comments and suggestions are records beside the
document, and the document is never written to. An inline anchor, in the
manner of OOXML's `commentRangeStart` and `commentRangeEnd`, writes into the
target, which D8's invariant I7 forbids (*"It may write nothing into the
artifact it refers to"*). It also conflicts: D8 §11, *Still open*, item 5,
verified that a marker written on its own line above a paragraph conflicts
with another branch that rewords the paragraph. Region markers stay what 0001
made them, rare names an author chooses, and they are what transclusion
addresses (§7).

**One file per record, in `<doc>.notes/` (Q1).** For `policy.md` that is
`policy.md.notes/`, beside it. Two people who comment at the same time add
two files, which git merges cleanly. A single sidecar file, such as D8 §7.3's
`comments.yaml`, puts every new comment at the same place in one file, and
two branches that both append there conflict.

**The directory is authoritative for the document (Q9).** A record holds no
path. If one ever does, the field is not called `on`: PyYAML's `safe_load`
reads `on: doc.md` as `{True: 'doc.md'}`, because YAML 1.1 reads `on` as a
boolean.

**A record's file name is its id**, a ULID, the one minted-id shape D8 §7.4
admits, for a thing that is not text. Ids are unique within a notes directory,
and the id is never written into the document.

**A rename moves the notes directory in the same commit (Q9).** If another
branch adds a record under the old directory meanwhile, git's default
directory-rename handling (`merge.directoryRenames` is `conflict` unless set)
reports the new file's location as a conflict, which is loud. A notes
directory left behind would resolve every record against whatever document
later takes the old path.

**The same record id in two notes directories is warned on (Q9).** It means
a directory was copied, for example into an archive beside a rewritten
document, and the copies may now resolve against the wrong document. A
record made on another branch after the copy has its own id, so the warning
does not reach it. That case is part of §9's R4.

**Records are not deleted in normal use (Q8).** A suggestion is accepted or
rejected by changing its `status`, not by deleting it. A deleted record and a
reply added to it on another branch merge cleanly, because one branch deletes
a file and the other adds a different one, and the reply is left pointing at
nothing. A status change keeps the parent. Two branches that accept and
reject one suggestion edit the same `status` line and conflict, which is
loud. Where records must go, a purge removes a whole thread in one commit.
If a reply's parent is missing anyway, the reply renders as
`#REF!(reply-to)`.

## 3. The record

A record is a blockspec document. Its frontmatter carries the anchor and the
metadata, and its body is the comment:

    ---
    anchor: {base: <40 hex>, leaf: {type: p, nth: 0, text: "The reactor scram threshold is 4.2 sigma above baseline, measured over a rolling 30-second window."}, span: "4.2 sigma", prefix: "The reactor scram threshold is ", suffix: " above baseline, measured over a"}
    kind: comment
    status: open
    ---

    Is this still right after the recalibration?

- **The anchor is one line.** A re-anchoring tool rewrites the whole line.
  Two concurrent re-anchorings then conflict, where a multi-line anchor could
  be merged line by line into a record that matches neither side.
- **At least one unchanging line separates the anchor from any field edited
  freely**, here `kind` before `status`. Git conflicts on edits to adjacent
  lines, so without the spacer a status change and a re-anchoring on two
  branches would conflict for no reason.
- `base` is the full object id of the document's blob.
- `leaf` names the anchored leaf in `base`: its type (`p`, `h1` to `h6`,
  `code` or `table`), its content, and `nth`, its 0-based ordinal among the
  leaves of `base` that have the same type and content. **`base` and `nth`
  are the disambiguator 0002 §2 left open**: a leaf repeated when the anchor
  was made is still one leaf of one blob.
- `span`, `prefix` and `suffix` are a W3C TextQuoteSelector (Web Annotation
  Data Model §4.2.4) inside the leaf, and never cross its edge.
- A suggestion adds `replace:` on the same line. `kind` is `comment` or
  `suggestion`. `status` is `open`, `accepted`, `rejected` or `resolved`.
- A reply is its own record, with `reply-to: <id>` and no anchor.

**Text is parsed and normalised.** A leaf's text is its content as `SPEC.md`
§6.3 defines it, normalised to Unicode NFC, with `\n` line endings. Offsets
are code points into that text, never offsets into the file. Two saves of
the same paragraph, one in NFC and one in NFD, or one with LF and one with
CRLF, give the same leaf.

**Creation is checked.** In the commit that adds a record, `base` is the
document's blob in that commit, the leaf at `nth` exists in it, and
`prefix + span + suffix` occurs exactly once in the leaf. A tool that cannot
make the triple unique does not create the anchor.

**A record is consistent or refused.** `prefix` and `suffix` are exactly 32
code points, or fewer only where the leaf's edge is nearer; a shorter one
with the edge further away is `record-inconsistent`, and so is an empty
`span`. `replace` is written into the document exactly as stored, never
normalised.

## 4. Which leaf: correspondence, and when to refuse

The resolver works on the **text-bearing leaves** of each snapshot, in
document order: paragraphs, headings, code blocks and tables. Markers and
thematic breaks carry no text and take no part. Each leaf has a **key**: its
type, with the heading level for a heading, and its normalised text. A
heading that changes level is an edited leaf, not an unchanged one.

**Correspondence** pairs base leaves with current leaves, in three steps:

1. Keys that occur exactly once in each snapshot pair up. The longest run of
   those pairs that keeps document order on both sides is the **chain**, and
   its pairs are `EXACT`. A unique pair off the chain is `MOVED`.
2. Between two consecutive chain pairs lies a **gap** on each side. Inside a
   gap, a longest common subsequence of equal keys gives more `EXACT` pairs.
3. Leaves left over in a gap pair as `EDITED` when their similarity is at
   least 0.5, the best candidate leads the next by at least 0.15, and the
   choice is mutual. Similarity is `2·LCS/(|a|+|b|)` over code points.

The thresholds 0.5 and 0.15 are borrowed from D8 (§7.1, §7.3), where they
apply to `difflib`'s ratio. Here they apply to `2·LCS/(|a|+|b|)`, a
different measure, and they have not been tested for this resolver.

**Then the anchored leaf's pair is checked against what else changed.**
*Unmatched* means a current leaf that is no base leaf's pair. Each rule
refuses one edit shape:

- **No pair.** The leaf is `ORPHANED`, unless a current leaf has its exact
  key, which is refused as `unaccounted-copy`: the text is still there, and
  the correspondence could not say which copy descends from it.
- **`EXACT`, repeated text.** If `base` or the current text holds more than
  one leaf with this key, the gap around the anchored leaf must hold as many
  copies in both, and the pair must lie in that gap, or it is refused as
  `repeat`. When one of two identical paragraphs is deleted, the copies alone
  do not say which survived. Unchanged unique neighbours on both sides can.
  The rule fires when *either* side is repeated: deleting one of two copies
  leaves the current text with one, and `base` still has two.
- **`EXACT`, near-copy.** An unmatched leaf at similarity of at least 0.5 and
  below 1 is refused as `near-copy`. This is `spike/LOG.md` §9's shape when
  the verbatim copy keeps the paragraph's place in the order: the anchored
  paragraph is reworded, and its old wording survives verbatim. The verbatim
  copy matches exactly, and the reworded paragraph, the real descendant, is
  the near-copy.
- **`MOVED`, near-copy.** An unmatched leaf at similarity of at least 0.5 is
  refused as `near-copy`. This is the same shape when the copy lands
  elsewhere, as in the log's appendix: the reworded paragraph stays in
  place, and its old wording copied elsewhere looks like a move.
- **`MOVED`, refilled gap (Q6).** If the gap the leaf left now holds an
  unmatched leaf, it is refused as `refilled-gap`. A paragraph rewritten
  beyond recognition in place, with its old wording copied elsewhere, also
  looks like a move, and the rewrite sits where the original was. The rule
  also refuses a real move whose old place gained a new paragraph. That is
  its cost.
- **`EDITED`, exact copy.** An unmatched leaf with the anchored leaf's old
  key is refused as `exact-copy`: the old text survives verbatim, and the
  edited pair is only one candidate. **Narrowed by Q12** to unmatched copies.
  A twin that is itself paired is accounted for, so editing one of two
  identical paragraphs does not refuse comments on the other.
- **`EDITED`, crowded gap.** Another unmatched leaf in the same gap is
  refused as `crowded-gap`. When a gap gains paragraphs while the anchored one
  is edited, which of the near candidates descends from it is a guess.
- **`EDITED`, near-copy.** An unmatched leaf anywhere at similarity of at
  least 0.5 is refused as `near-copy`. A paragraph moved and edited, with a
  variant of it left in its old place, has two candidates.

## 5. Which characters: the span

For `EXACT` and `MOVED`, the leaf's text is unchanged and the span keeps its
offset.

For `EDITED`, the span is searched **inside the paired leaf only**, D8 §7.3's
two-stage rule. A hit is an occurrence of `span` with `prefix` immediately
before it and `suffix` immediately after it. No hit makes the anchor
`DETACHED`. More than one is refused as `span-ambiguous`.

**The context filter (Q13).** Requiring the stored context detaches a span
whose wording was re-added elsewhere in the leaf with paraphrased
surroundings. It also tells apart two occurrences of the span that differ
only in their context, and it detaches an anchor when the words right next
to the span change. That last case is a recall cost: the span is intact, and
the anchor still detaches. A comment-only fallback, which places a comment
by the alignment alone when no hit carries the context, was weighed and
declined. It recovers those detachments, and it lets a comment follow a
re-added span with paraphrased surroundings onto the wrong words. The width
is 32 code points, the Hypothesis convention D8 §3.4 used. A wider context
detaches more comments after nearby edits, and does not help §9's R3, whose
re-added sentence carries its own context. Both stay until a replay of real
history prices the detachments.

**The alignment.** A deterministic longest-common-subsequence alignment of
the base leaf's text onto the current leaf's must carry every character of
the span onto the hit, or the anchor is `DETACHED`. That detaches a span
rewritten in place while its old wording reappears elsewhere in the leaf
with the same context, when the alignment carries the old span to the
rewritten position rather than to the copy. When it carries the old span
onto the copy, the anchor lands there: that is §9's R3.

**Statuses**, and how each renders (D8 §10 for the loud ones):

| status | meaning | renders as |
|---|---|---|
| `RESOLVED` | the leaf is unchanged and the span is where it was | the anchor |
| `MOVED` | the unchanged leaf is elsewhere | the anchor, marked moved |
| `EDITED` | the leaf changed, and the span, its context and its alignment are intact | the anchor, marked changed |
| `DETACHED` | the leaf has a descendant, and the span or its context does not survive in it | on the leaf, flagged, with the base text |
| `ORPHANED` | the leaf has no descendant | `#REF!`, with the base text |
| `REFUSED(reason)` | the witnesses disagree, or an input is unusable | `#REF!(reason)`, with the base text |

**Comments follow moves (Q2).** A comment on a paragraph that moved,
unchanged, lands on it marked `MOVED`. Refusing every move would close §9's
R1, and would refuse every real move as well. A comment that follows a false
move is shown as moved, with its base text beside it.

## 6. Suggestions (Q2, Q10, Q11)

**A suggestion applies only when its record's `status` is `open` and its
anchor is `RESOLVED` or `EDITED`.** Otherwise it is stale.

- **Never on `MOVED` (Q2).** §9's R1 cannot be told from a real move. A
  comment that follows it is visible and harmless. A suggestion that applies
  to it edits the wrong text.
- **Only `open` (Q10).** Accepting a suggestion changes the document and sets
  `status: accepted` in one commit. A `git revert` of that commit restores
  both, and the suggestion is open again, consistently. A hand edit that
  restores the old text leaves the record `accepted`. A gate that ignored
  `status` would apply the suggestion a second time. An accepted or rejected
  suggestion renders as history, never as an edit that can be applied.
- **Write-back maps exactly or not at all (Q11).** The span's offsets are NFC
  code points of the parsed leaf. The file may hold the leaf in another
  normalisation form, and container prefixes (`> `, list indentation),
  continuation indentation and carriage returns sit between its lines. The
  span is located in the leaf's parsed content, the NFC form of that piece
  of content must be `span`, and its position is mapped back through the
  parse to raw positions, skipping those characters (`SPEC.md` §11.7).
  Container prefixes and line endings are re-emitted line by line from the
  parse, and nothing outside the span is re-normalised. Otherwise the
  suggestion is stale, `unmappable-offset`.
  Mapping the whole raw leaf instead would make every span after the first
  line of a quoted or list paragraph, or of a CRLF file, unmappable.
  Rewriting the whole leaf to NFC was weighed and declined: it is a visible
  edit the author did not make.

## 7. Transclusion (Q4, Q5)

**A transclusion is a paragraph that is exactly one link, titled
`transclude`** (Q5):

    [Scram threshold](policy.md#scram-threshold "transclude")

It renders as a working link in every markdown tool, which is the owner's
answer to 0001 applied again. The alternative, an `<!-- include … -->`
marker, renders as nothing, so a reader in an ordinary renderer would not
know that content was missing. **This amends 0001**: inline content stays
opaque everywhere except in this one shape.

**The target is a region marker's name.** A heading slug is not a target.
0001 decided that slugs are resolvable but not durable, and a transclusion is
the most durable reference a document makes. This settles the question 0002
§4 left open, whether a slug transcludes the heading or its section: it
transcludes neither. The unit is what the name binds (0002 §4): one node with
its subtree, or the nodes of one region.

**The referrer pins the target.** A name can be moved to other content by the
target's author (Q4), and a marker separated from its text binds whatever
comes next, silently. So the referrer stores, in its own frontmatter, the
target's blob at the time it was pinned: the referrer holds the selector, as
D8 §7.3 puts it, and the target is never written to. Research `DESIGN.md`
§16, risk 1, names the same remedy, binding a reference to a fingerprint of
what it named.

Resolution:

1. Resolve the name in the current target. Zero or several matches are
   `#REF!(name)`.
2. For each text-bearing leaf the name bound in the pinned blob, run §4
   against the current target. A refusal, or no pair, refuses the
   transclusion.
3. Every pair must lie inside what the name binds now. Otherwise the
   transclusion is refused as `name-rebound`.

**A refused transclusion stays refused until the referrer re-pins (Q4)**,
which records the target's current blob and is an edit someone makes on
purpose. Editing inside the named content passes step 3, so a target's
author can usually revise the text without breaking its readers. An edit
that leaves a pinned leaf with no pair (`pinned-orphaned`), or that adds
leaves around one while editing it (`pinned-crowded-gap`), still refuses
until a re-pin, as does moving the name to other content.

**The transcluded text is never copied into the referrer** (D8 §8.1, D8's
R3).

## 8. What each edit must produce

The edit shapes the rules above exist for, and the outcome each must have.
"Stale" means a suggestion that does not apply. The conformance cases that
follow this document take their shapes from this table.

| edit | comment | suggestion | transclusion |
|---|---|---|---|
| other leaves edited | `RESOLVED` | applies | resolves |
| a new leaf, unlike the anchored one, inserted directly above or below it | `RESOLVED` | applies | resolves, except when inserted between a one-line marker and the leaf it names: the marker then names the new leaf (`SPEC.md` §7.2), `REFUSED(name-rebound)` |
| the anchored leaf edited outside the span and its context | `EDITED` | applies | resolves |
| the anchored leaf edited inside the context, not the span | `DETACHED` | stale | resolves |
| the span rewritten, including when its old wording reappears elsewhere in the leaf with other context, or where the alignment does not carry the span onto it | `DETACHED` | stale | resolves |
| the anchored leaf rewritten to similarity below 0.5 | `ORPHANED`, or refused | stale | refused |
| the anchored leaf deleted | `ORPHANED` | stale | refused |
| the unchanged leaf moved, nothing new where it was | `MOVED` | stale | resolves if the name moved with it |
| two branches edit different lines of the anchored leaf and merge cleanly | as the edit of the merged text | as the edit of the merged text | resolves |
| two branches edit the same lines | a git conflict; committed with its markers, the document is refused (`conflict-marker`) and the anchor is `REFUSED(not-in-profile)` | stale | `REFUSED(not-in-profile)` |
| the number of copies of the anchored text in its gap differs between `base` and now | `REFUSED(repeat)` | stale | — |
| identical copies separated by unchanged unique leaves | `RESOLVED` on the right copy | applies | — |
| the anchored leaf changed, and a near-copy of its old wording unaccounted for | `DETACHED` or refused, never a span on the copy | stale | refused |
| the anchored leaf's gap gains leaves while it is edited | `REFUSED(crowded-gap)` | stale | refused |
| a heading changes level only | `EDITED` | applies | resolves |
| the file re-saved in another normalisation form, or with other line endings | as if unchanged | as if unchanged, where the write-back maps exactly | as if unchanged |
| the document deleted, or renamed without its notes directory | `REFUSED(document-missing)` | stale | refused |
| `base` unreachable | `REFUSED(base-unavailable)` | stale | refused |
| the record inconsistent with `base` | `REFUSED(record-inconsistent)` | stale | refused |
| the suggestion's `status` is not `open` | — | stale, shown as history | — |

## 9. The residual: four mechanisms the bytes cannot separate

These are silent wrongs this design does not prevent. Each is a pair of
histories that leave identical snapshots, one of which is a legitimate edit.

**R1. A leaf deleted, and a verbatim copy of it elsewhere.** A paragraph is
deleted, and on another branch, or in the same commit, its wording is quoted
in a "superseded wording" appendix. The comment follows the quote as `MOVED`.
The two snapshots are identical to a real move of the paragraph.
*Suggestions are not affected*: the gate is stale on `MOVED`.

**R2. A leaf rewritten beyond recognition, with its old wording left in
order.** The paragraph is rewritten to similarity below 0.5, and a block
quote of its old wording sits directly below it. The quote's text equals the
old leaf, in the old leaf's place in the chain, so it reads as the paragraph,
unchanged, with a new paragraph inserted above it. *Suggestions are
affected*: the suggestion applies to the quotation.

**R3. Inside one leaf, the span's sentence rewritten and the old sentence
re-added with the same context.** The span keeps its 32 code points of
context, and the alignment maps the old sentence onto the re-added copy. The
snapshots are identical to moving a sentence to another place in its
paragraph and writing a new one where it was. *Suggestions are affected.*

**R4. A different document at the same path.** A document is moved to an
archive, or copied there with its notes directory, and a new document that
reuses some of its paragraphs takes the old path. The notes left at the path
resolve against the new document. *Suggestions are affected.* Git reports
the old path as modified and the archive path as added, not as a rename, so
§2's rename rule does not see either form. The duplicate-id warning flags a
copied directory's original records, and not a record made concurrently on
another branch.

`spike/LOG.md` §9's single-commit shape is the published instance of this
family. In the form the log gives, a light rewording with the original
quoted in an appendix, the reworded paragraph is still similar to its old
text, so by §4's near-copy rules it is refused rather than silently wrong.
That follows from the rules; it has not been run against the log's case. R1
and R2 are the forms in which no such similarity survives.

**What would close each**, none of which the format can require:

- **merge parents** (Q7): resolving through each side of a merge can refuse
  the two-branch forms of R1 and R2, where the sides disagree. Squash-merge
  and rebase leave no merge to read, and the one-commit forms have none;
- **edit history** kept per commit through integration, which squash and
  rebase discard;
- **an authored name** on the leaf, which survives R1 because it is carried
  in the bytes. That is a write to the document, which D8 allows only for a
  name the target's own author chooses (D8 §7.2, §11);
- **document identity** (Q9) for R4, which in the file would be a minted id
  in the target, forbidden by I7;
- **intent**, which only the author has.

A tool MAY use any of them to refuse more. Under Q7 such a check MAY only add
refusals, never turn a refusal into a resolution, and is not part of
conformance.

## 10. Prior art, and why it does or does not fit stock git

- **W3C Web Annotation Data Model** (Recommendation, 2017, §4.2): the
  TextQuoteSelector's `exact`, `prefix` and `suffix` are the record's
  vocabulary. Its resolution policy does not fit: on several matches the
  selection "SHOULD be treated as matching all of the matches", the opposite
  of refusing.
- **Hypothesis** (D8 §3.4): its matcher has no minimum score and searches the
  whole document. It is tuned for recall, and this design is tuned the other
  way.
- **Word / OOXML** (ECMA-376 Part 1 §17.13.4): comment ranges are written
  inline and linked by id. It writes into the target.
- **Google Docs**: anchors live in the editor's model, kept current by a
  central operation log. Git has no such log.
- **CRDTs**, such as Yjs relative positions and Peritext (Litt, Lim,
  Kleppmann and van Hardenberg, 2022): anchors attach to character ids. A
  hand edit in a text editor has none. An operation log of that kind is
  exactly the history that would make R1 to R3 unambiguous.
- **Transclusion systems** (D8 §8.1): AsciiDoc tags, MediaWiki sections and
  DITA's `conref`/`keyref` have the target declare the region and address it
  by name, as draft 0's markers do. None of them pins content, so a name
  moved to other content goes unnoticed there. That is an inference, not
  tested.

## 11. The cost of reversing each choice

Common to all of them: no document changes, because nothing is written into
one. Every record carries `base`, so a migration can recompute an anchor from
git while `base` is reachable.

| choice | reversed to | cost |
|---|---|---|
| one file per record (Q1) | one sidecar per document | Mechanical: concatenate. Concurrent comments then conflict. |
| comments follow moves (Q2) | every move refused | Lossless: one refusal more. Real moves stop resolving. |
| suggestions never on `MOVED` (Q2) | applied on `MOVED` | R1 reaches suggestions. Not recommended under any evidence here. |
| refill rule kept (Q6) | dropped | Lossless to drop. One silent-wrong shape returns. |
| the titled link (Q5) | a marker | Every transclusion paragraph is rewritten, mechanically, and rendering stops showing a link. |
| 32-code-point context (Q13) | wider | New records only. Existing ones keep theirs until re-anchored, which needs `base`. |
| no comment fallback (Q13) | a fallback | Lossless to add. Comments gain the recall and accept the wrong-words case. |
| the twin narrowing (Q12) | the wider rule | Lossless: more refusals. |
| only `open` applies (Q10) | any status | Reapplies restored suggestions. Not recommended. |
| exact write-back (Q11) | whole-leaf NFC | Each write-back may rewrite a whole paragraph's bytes. |

## 12. What would reverse it

1. **A replay over real history that prices the refusals.** D8 §3.4
   measured 7.1% loud refusal for its two-stage resolver on rust-book at gap
   25, 3.1% on obsidian-help and 2.1% on rust-book at gap 5. This design adds
   refusals: the near-copy, refilled-gap, crowded-gap, twin and context
   rules, and the alignment. Its rate is unknown. If it is too high, the
   crowded-gap rule and the near-copy rule on `EDITED` leaves are the likeliest
   costs, and the first to revisit. The replay needs an oracle other than this
   resolver.
2. **How often R1 to R4 occur.** Summed over the spike's FOUND cells,
   `wrong_on_deleted`, the count of quote-anchor units wrong on a target the
   oracle says was deleted, is 0 (0001, the factual disputes). That is
   suggestive for R1, not a measurement of it.
3. **Q13's replay.** If detachments from edits next to a span dominate, the
   width or the fallback is revisited.
4. **A workflow that guarantees merge commits.** Q7's check then closes the
   two-branch forms of R1 and R2, and could be required where that holds.

## Effect on 0001, 0002 and draft 0's documents

- **0001 is amended by Q5**: one inline shape, a paragraph that is exactly one
  link titled `transclude`, has meaning. Everything else inline stays opaque.
  Slugs stay resolvable and are not transclusion targets.
- **0002 is unchanged.** The correspondence key adds the heading level and NFC
  normalisation to the type and content 0002's tree pins. 0002 §2's
  disambiguator is `base` with `nth`. Its range anchor, a selection across
  leaves, stays open.
- **A document stays as it was.** The profile's reader still treats
  frontmatter as opaque. A record's frontmatter and a referrer's pins are
  read by the resolver, not by the profile.

## What draft 0 carries, from this decision

- **Records**: one file per record in `<doc>.notes/<ulid>.md`, a blockspec
  document whose frontmatter holds a one-line anchor (`base`, `leaf` with
  type, text and `nth`, `span`, `prefix`, `suffix`, and `replace` for a
  suggestion), then `kind` and `status`.
- **Resolution**: correspondence over keyed text-bearing leaves, the
  refusal rules of §4, the span search and alignment of §5, six statuses, and
  the refusal reasons `SPEC.md` §11.10 lists.
- **Suggestions**: applied only when `open`, and only on `RESOLVED` or
  `EDITED`, and written back only through an exact mapping.
- **Transclusion**: a paragraph that is one link titled `transclude`,
  addressing a marker's name, pinned by the referrer, refused when the name
  is rebound, until re-pinned.
- **Documented residuals**: R1 to R4.

## Addendum, 2026-10-16: the record's grammar, and six details

The owner's decisions of 2026-10-16, on seven details that `SPEC.md` §12
listed as left open by this document. `SPEC.md` §11 carries the rules. Where
this addendum and the body disagree, the addendum wins: §3's example is
rewritten below in the grammar decided here.

**1. A record's frontmatter.** The anchor is one frontmatter line whose value
is a JSON object (RFC 8259). JSON is valid YAML 1.2 flow syntax, so the
frontmatter stays YAML; its quoting is unambiguous; and every key inside it
is quoted, so YAML 1.1's reading of `on` as a boolean cannot reach one.
`reply-to` sits on its own line.

The lines between the record's opening and closing `---` (`SPEC.md` §5) are
exactly these, in this order, each with nothing before or after it:

- a comment or a suggestion: `anchor: ` followed by the anchor, then
  `kind: comment` or `kind: suggestion`, then `status: ` followed by `open`,
  `accepted`, `rejected` or `resolved`;
- a reply: `reply-to: ` followed by the parent's id as a JSON string, then
  `kind: comment`.

The anchor is written in one canonical form:

    {"base": B, "leaf": {"type": T, "nth": N, "text": S}, "span": S, "prefix": S, "suffix": S}

with `, "replace": S` before the final `}` for a suggestion, and never for a
comment.

- `B` is a string holding the blob's full object id in lower-case hex: 40
  digits in a SHA-1 repository, 64 in a SHA-256 one.
- `T` is a string, one of `p`, `h1` to `h6`, `code` and `table`.
- `N` is a JSON number written as decimal digits, `0` or with no leading
  zero, and no sign, fraction or exponent. A YAML 1.1 reader takes `010` for
  the octal 8.
- Each `S` is a string. A string is `"`, its code points, then `"`. `"` is
  written `\"`, `\` is written `\\`, and a line feed is written `\n`. Every
  other code point in U+0000 to U+001F, in U+007F to U+009F, and U+2028,
  U+2029, U+FEFF, U+FFFE and U+FFFF is written `\u` followed by four
  lower-case hex digits. Every other code point is written as itself, in
  UTF-8, and no other escape is used: no `\/`, no `\t`, no surrogate pair.
  The escaped set keeps the value on one line, keeps out the characters YAML
  1.2 does not allow unescaped, and keeps out U+0085, U+2028 and U+2029,
  which YAML 1.1 reads as line breaks.
- The spacing is exactly as shown: one space after each `:` and after each
  `,` between members, and none anywhere else.

The keys are in the order shown. With one canonical form, two tools that
write the same anchor write the same bytes, and a reader that parses the
value as JSON and writes it back in this form can compare the bytes.

`reply-to` is a JSON string, not a plain scalar, because a YAML 1.2 reader
under its core schema reads an id made only of digits as an integer. `kind`
and `status` stay plain words. None of their values is a YAML 1.1 boolean,
and `status` is the line people edit by hand.

The record of §3, in this form, with an illustrative `base`:

    ---
    anchor: {"base": "9b1c4e0d2f7a6385c1e0b4d9a8f7263514c0e9ab", "leaf": {"type": "p", "nth": 0, "text": "The reactor scram threshold is 4.2 sigma above baseline, measured over a rolling 30-second window."}, "span": "4.2 sigma", "prefix": "The reactor scram threshold is ", "suffix": " above baseline, measured over a"}
    kind: comment
    status: open
    ---

    Is this still right after the recalibration?

Its `prefix` is 31 code points, because the leaf's start is 31 code points
before the span (detail 6).

**A reader refuses the record as `record-inconsistent`** when it has no
frontmatter; when the frontmatter's lines are not exactly those above, in
that order, with nothing added; when the anchor, or the `reply-to` string, is
not in the canonical form, including a value that is valid JSON or valid YAML
and reads to the same values written another way: other spacing, key order
or escapes, a duplicate key, or an unquoted key; when `B` or `T` is not a
value the list above allows; or when `replace` is present on a comment or
missing on a suggestion. The rules 0003 already fixes still apply on top.

**2. A referrer's pins.** A referrer's pins are written one per line under a
`pins:` key in its frontmatter: a line that is exactly `pins:`, directly
followed by one line per pin, each `  - ` (two spaces, a hyphen and a space)
followed by an object in detail 1's canonical form and escaping:

    pins:
      - {"path": "policy.md", "blob": "9b1c4e0d2f7a6385c1e0b4d9a8f7263514c0e9ab"}

- `path` is the path part of a transclusion's link destination, everything
  before the `#`, character for character as the link writes it (detail 7).
  A transclusion uses the pin whose `path` is equal to its own.
- `blob` is the target document's blob when it was pinned, in lower-case
  hex as `B` above.
- The pins end at the first line of the frontmatter that does not begin with
  `  - `. They are sorted by `path`, ascending, comparing code point by code
  point, and no `path` appears twice.
- A line that begins with `  - ` after the pins have ended is refused when
  every line between them is blank or begins with a space or `#`. A YAML
  reader would read it as one more pin, across a blank or comment line, and
  the resolver would not.

The rest of the referrer's frontmatter stays opaque. The resolver reads the
pin lines as text and does not run a YAML reader over the frontmatter; they
are written so that a YAML 1.2 reader of a frontmatter that is a block
mapping reads `pins` as a list of mappings with the same values.

**Every transclusion in the referrer is refused as `record-inconsistent`**
when the frontmatter has more than one line that begins with `pins:`, a line
that begins with `pins:` and is not exactly `pins:`, a pin line not in the
canonical form, pins out of order, one `path` twice, or such a `  - ` line
after the pins have ended.

What one line per target buys, probed with git 2.47 on a stock `git merge`:
a pin that two branches change differently is one line, and conflicts, which
is loud. Two branches that add or re-pin different targets merge cleanly
when at least one unchanged line lies between their changes. When their
changes touch, as two additions in the same place in the list or re-pins of
two adjacent lines do, git reports a conflict. That is loud, not wrong, as
long as a referrer committed with its markers is refused as
`conflict-marker`, which is the suite's reading 12, not a decision. Sorting
by `path` spreads additions across the list where appending would put every
addition in the same place.

**3. A table's text.** A table's text, as one string, is its cells joined by
` | ` and its rows by `\n`, after the suite's reading 8 normalisation: header
row first, each cell trimmed of spaces and tabs, `\|` read as `|`, a short
row padded with `""`, cells past the header's width dropped. The string is
then normalised to NFC, as every leaf's text is.

**A cell's `|` is written `\|` before the cells are joined**, and nothing
else is escaped. That keeps the string unambiguous, and it matters: without
it, a one-column table whose cell is `a | b` and a two-column table whose
cells are `a` and `b` would have one key, so they would be copies (`SPEC.md`
§11.2), and a correspondence could pair them as `EXACT`. With it, every `|`
from a cell follows a `\`, and every `|` of a separator follows a space,
since a trimmed cell never ends in one. A cell never holds a line feed, so
`\n` separates rows. The written form is also how the cell's pipe is written
in the file.

**4. Which chain, when several are longest.** Take the leftmost. Number the
current text-bearing leaves from 0 in document order. A chain's pairs, in
base order, have increasing current indices, and since a chain's keys are
unique in the current text, the sequence of those indices identifies the
chain. Of the longest chains, the chain is the one whose sequence is
lexicographically smallest: at the first position where two sequences
differ, the smaller index wins. All the longest chains have one length, so
the comparison always ends at a difference. For two unique leaves that swap
places, both chains have length 1, and the chain is the pair of the leaf
that is now first: it is `EXACT`, and the other is `MOVED`.

**5. Thresholds compare exactly**, in integer arithmetic. With similarity
`2·L/T`, where `T = m+n`, and `T` at least 2 since every key holds its type
and U+001F:

| §11 states | compare |
| --- | --- |
| similarity at least 0.5 | `4·L ≥ T` |
| similarity below 1 | `2·L < T` |
| `2·L₁/T₁` exceeds `2·L₂/T₂` by at least 0.15 | `40·L₁·T₂ − 40·L₂·T₁ ≥ 3·T₁·T₂` |

Each keeps the sense `SPEC.md` §11 gives it: "at least" stays `≥`, and
"below" stays `<`. Each is the stated comparison multiplied through by a
positive integer: `2·T`, `T` and `20·T₁·T₂`. Checked against exact rationals
on 200,000
random draws with `T` up to 120. Floating point does differ:
`22/30 − 42/72` is exactly 0.15, and IEEE 754 doubles compute 0.1499…,
below the margin.

**6. A hit at the leaf's edge.** A `prefix` shorter than 32 code points is
short because the leaf's start was nearer, and a `suffix` shorter than 32
because the leaf's end was. A hit must still sit at that edge: with a short
`prefix`, the hit's `prefix` starts at the start of the paired leaf's text,
and with a short `suffix`, the hit's `suffix` ends at its end. An occurrence
that does not is not a hit. Without the rule, a span at a leaf's start,
stored with an empty `prefix`, could land on a later occurrence of it that
the same `suffix` follows.

**7. A transclusion's path** resolves relative to the directory that holds
the referring document, as a renderer resolves a relative link. The path is
the link destination's part before the `#` (CommonMark 0.31.2, *Links*),
**as raw text**: character for character as the file writes it, with no
backslash escape, entity reference or percent-encoding decoded, the same
text a pin's `path` holds. So `my%20doc.md` names a file called
`my%20doc.md`, and is `document-missing` where there is none. It is read in
the tree of the snapshot being resolved, from the referrer's
directory: split at `/`, a `.` segment is dropped, and a `..` segment
removes the segment before it.

- **An absolute path is refused, as `unresolvable-path`.** That is a path
  that begins with `/`, or whose first segment holds a `:`, as a URL's scheme
  or a drive letter does. Renderers disagree on what `/` is relative to: a
  forge reads it as the repository's root, and a local editor as the file
  system's. A URL leaves the repository. Refusing is lossless to relax.
- **A `..` that would go above the repository's root is refused, as
  `unresolvable-path`.** What it names is not versioned with the referrer,
  so its blob cannot be read from the repository.
- **A path that names no file in that tree is refused, as
  `document-missing`**, the reason `SPEC.md` §11.10 already gives a missing
  target. Names compare exactly, so a path that differs from a file's only
  in case names nothing.

`unresolvable-path` is a new resolution reason. The path is checked before
everything else in `SPEC.md` §11.9's step 0.

**The owner's decisions on the precision**, also of 2026-10-16. The seven
rulings above left these choices to the write-up, and the owner ratified
each as decided:

- **Byte-exact canonical JSON**, with its key order, spacing and escape set,
  `base` as lower-case hex of 40 or 64 digits, and `nth` as plain decimal:
  one form means two tools write the same bytes, and a reader can refuse
  anything else by comparing them.
- **The exact set of record lines**: a reader that knows every line can
  refuse a record that holds anything else, rather than guess at it.
- **`reply-to` as a JSON string, and a reply carrying `kind: comment` and no
  `status`**: an id of digits stays a string under YAML 1.2, and a reply's
  status has no meaning to carry.
- **Pins sorted, unique, as `  - ` lines, and a malformed block refusing the
  referrer's transclusions**: sorting spreads concurrent additions apart, a
  duplicate would give one target two blobs, and a pin that cannot be read
  must not be skipped silently.
- **The `\|` escape in a table's text**: without it two different tables
  can be copies.
- **The new reason `unresolvable-path`**: an absolute path, or one that
  leaves the repository, is a different failure from a missing file, and
  says what to fix.
- **"Leftmost" as the lexicographically smallest sequence of current
  indices**: one tie-break that every implementation computes the same way.
  It differs from a reading in base order: when two leaves swap, the leaf
  now first is `EXACT`, where a base-order reading would make the leaf that
  was first `EXACT`.

**What these leave open**, listed in `SPEC.md` §12: whether creation and the
consistency check count occurrences under detail 6's edge rule; whether a
later version admits further keys in a record's frontmatter; a pin that no
transclusion uses; a frontmatter whose other content
makes a YAML reader read the `pins:` line as something else; what a
conflict among the pin lines does if reading 12 is reversed; how a span is
written back into a table, whose text holds separators and escapes no single
raw character gives; whether a renderer-style decoding of a path's
percent-encoding, backslash escapes and entity references is wanted later,
and how empty segments are read; and a path that names a symbolic
link, a submodule or a file that is not markdown.

## Addendum, 2026-10-16: input problems, and two unreachable clauses

The owner's decisions of 2026-10-16, on nine gaps §11 left open. Each
numbered item is the owner's. Where this write-up adds
precision of its own, it says so, marked **(precision, not the owner's)**,
with the reason. `SPEC.md` §11 carries the rules.

**1. An over-long context.** A `prefix` or `suffix` longer than 32 code
points is `record-inconsistent`. With the rule 0003 already has for a short
one, a context is exactly 32 code points, or fewer only at the leaf's edge.

**2. Which input problem is reported.** When a record has several input
problems, the first in data-dependency order is reported:

1. the record's grammar (`record-inconsistent`);
2. `document-missing`;
3. the current document refused under the profile (`not-in-profile`);
4. `base-unavailable`;
5. `base` refused under the profile (`not-in-profile`);
6. the leaf at `nth` inconsistent with `base` (`record-inconsistent`).

Several `pinned-<reason>`s on one transclusion are ordered the same way.

**(precision, not the owner's)** Among several `pinned-<reason>`s, the one
reported is the first leaf's that refuses, in the pinned blob's document
order. *Reason*: that is the order in which `SPEC.md` §11.9's leaf step
visits the pinned leaves, and every implementation computes it the same
way.

**(precision, not the owner's)** What each `record-inconsistent` step
holds. Step 1 is every check that reads only the record, `leaf.text`
included: its file name and directory entry (item 5), its frontmatter's
grammar, its body (item 8), an empty `span`, a context longer than 32 code
points (item 1), `prefix + span + suffix` not occurring exactly once in
`leaf.text`, and a short context whose edge in `leaf.text` is further away.
Step 6 is the one check that needs `base`'s leaves: no leaf of `base` with
`leaf`'s type and text at ordinal `nth`. *Reason*: each check sits at the
first step whose data it reads, which is the principle the owner's order
follows. So a record whose triple occurs twice in its own `leaf.text`, and
whose `base` cannot be read, is `record-inconsistent`, not
`base-unavailable`.

**(precision, not the owner's)** The transclusion's order, from the same
rule and items 3, 6 and 7:

1. the referrer refused under the profile (`not-in-profile`, item 7);
2. `unresolvable-path`;
3. the referrer's pins block broken (`record-inconsistent`);
4. `document-missing`;
5. the current target refused under the profile (`not-in-profile`);
6. a name that only a heading slug matches in the current target
   (`#REF!(name)`, item 6);
7. the pinned blob unreadable (`base-unavailable`);
8. the pinned blob refused under the profile (`not-in-profile`);
9. no marker binding the name in the pinned blob (`record-inconsistent`);
10. then `SPEC.md` §11.9's name, leaf and rebinding steps, in order.

*Reason*: the path and the pins are read out of the referrer, so the
referrer comes first; the rest is the record's order with the pin standing
in for `base`, and item 6 needs only the current target. Here, and
throughout §11.9, a name **binds** only through a region marker (§7.2,
§7.3); a heading slug never binds.

**3. `unresolvable-path` before a broken pins block.** The path is checked
before the pins. This addendum supersedes the first addendum's detail 7,
"checked before everything else in step 0": a referrer the profile refuses
comes first (item 7), then the path.

**4. A line break that cannot be written back.** A `\n` in `replace` that
cannot be re-emitted unambiguously makes the suggestion stale, as
`unmappable-offset`. That is so when the line it breaks is:

- a list item's first line, where the container prefix is the list marker,
  which a new line cannot repeat;
- a lazy line, which has no container prefix to repeat;
- a line whose container prefix holds a tab;
- the file's last line, when the file has no final line ending to copy.

**5. What the notes directory holds.** A file in `<doc>.notes/` whose name
is not `<ULID>.md`, a subfolder, and a record whose `reply-to` is malformed
are each `record-inconsistent`.

**(precision, not the owner's)** A ULID here is 26 characters of Crockford's
base 32 in upper case, `[0-9A-HJKMNP-TV-Z]`, the first of them `0` to `7`,
as the ULID specification writes one. A malformed `reply-to` is one whose
string is not a ULID in that form. *Reason*: one spelling per id, so that
ids, file names and `reply-to` compare byte for byte, and a lower-case
spelling of the same ULID is not a second id.

**6. A name that only a heading slug matches**, in the current target, is
`#REF!(name)`, and is checked before the name's binding in the pinned blob.
A marker name that is also some heading's slug resolves to the marker, by
§8.1's order, so this is only a name no marker declares.

**7. A referrer holding conflict markers** refuses its transclusions, as
`not-in-profile`. `SPEC.md` §11.10's row for `not-in-profile` names the
referrer. Two further points, also the owner's:

- **A referrer the profile refuses is refused as a whole**, as
  `not-in-profile`, whatever the profile refuses it for, and its
  transclusions are not enumerated: a refused file has no tree in which to
  find a transclusion paragraph. The anchor case kind gives such a referrer
  one referrer-level status instead of a list.
- **A conflict-marker line anywhere in the referrer counts**: in its
  frontmatter and in a fenced code block alike, whatever the suite's
  readings 12 and 4 say. The pins sit in the frontmatter.

This closes the first addendum's open item on a conflict among the pin
lines.

**8. A record whose body the profile refuses** is `record-inconsistent`. A
record is a blockspec document (§3), so its body is one.

**9. Two clauses that can never apply are removed.**

- **`#REF!(name)` for a name that binds more than one target** (§7, step 1,
  and *Details this document fixes*). Proof: `SPEC.md` §11.9 requires the
  current target to pass the profile before the name resolves, the profile
  refuses a name declared twice (`duplicate-name`), and the name is matched
  against markers only, so it matches at most one target.
- **"The pair must lie in that gap"**, in §4's rule for an `EXACT` leaf with
  repeated text. Proof: the rule fires only when the key is repeated, a
  repeated key is never on the chain, so the pair comes from step 2's
  alignment inside one gap, and that gap is the anchored leaf's own.

The body of this document keeps both clauses as first written. This
addendum removes them, and `SPEC.md` does not carry them.

## Addendum, 2026-10-16: overlaps, replies, and two write-back edges

The owner's decisions of 2026-10-16. Each numbered item is the owner's.
Where this write-up adds precision of its own, it says so, marked
**(precision, not the owner's)**, with the reason. `SPEC.md` §11 carries
the rules.

**1. Overlapping occurrences count.** Occurrences of
`prefix + span + suffix` in `leaf.text` are counted by start position, so
two that overlap are two, and the triple does not occur exactly once. That
applies at creation and in the consistency check alike.

**(precision, not the owner's)** §11.5's hits are counted the same way: an
occurrence is a start position, and two overlapping hits are two, so
`span-ambiguous`. *Reason*: one way of counting occurrences everywhere
§11 counts them.

**2. Replies are records.** A reply whose notes directory's document is
missing, or refused by the profile, is `REFUSED(document-missing)` or
`REFUSED(not-in-profile)`, as any record is. This narrows Q8's row in the
*Decision* table and the last sentence of §2: a reply whose parent is
missing renders `#REF!(reply-to)` only once its document is found and
accepted. Both texts stay as first written.

**(precision, not the owner's)** Where it sits in the order of the second
addendum's item 2: a reply goes through steps 1 to 3, its grammar, then
`document-missing`, then the document refused under the profile. Steps 4
to 6 read an anchor, which a reply does not have. Only a reply that passes
steps 1 to 3 is looked up by its `reply-to`, and renders `#REF!(reply-to)`
when that names no record. *Reason*: the data-dependency rule puts every
check on the document before anything rendered on it, and `#REF!(reply-to)`
is how a reply renders, not an input problem.

**3. A character that comes from no single raw character.** Where a tab is
only partly consumed by container indentation, CommonMark keeps the rest of
its width as spaces in the content, and those characters of `leaf.text`
come from no single raw character. A span that crosses one makes the
suggestion stale, as `unmappable-offset`.

**(precision, not the owner's)** "Crosses" is read as: at least one code
point of the span is such a character, or the span ends right before one.
A span that begins right after one maps. *Reason*: §11.7 maps two
positions, `a` where the span begins and `b` where it ends, through the
parse to raw positions. A span that begins right after the leftover spaces
has its `a` on the raw character after the tab. A span that ends right
before them ends with the line's `\n`, and step 2 carries `b` to where the
next line's content begins, which is inside the partly consumed tab, not a
raw position.

**(precision, not the owner's, extending item 3)** The same holds for a
tab partly consumed by any indentation, not only a container's: a fenced
code block's own indentation, removed from each content line (a fence
indented two spaces, then a content line that is a tab and `foo`, leaves
two spaces of the tab in the content), and any other indentation
CommonMark removes from a line by columns. *Reason*: item
3's principle is that a character of `leaf.text` that comes from no single
raw character cannot be written back, and that is so whatever indentation
consumed the rest of the tab. An indented code block would be another
instance, but the profile refuses one (`SPEC.md` §4.1).

**4. A code block's final line ending.** A span whose last code point is
the `\n` that ends a code block's last content line makes the suggestion
stale, as `unmappable-offset`. That `\n` stands for where the block's
content ends, not for text: writing over it would join the closing fence
to the line before it, and in a fence left unclosed at the end of its
container or of the file, where reading 8 still ends the last line in
`\n`, it may come from no raw character at all.

**(precision, not the owner's)** That holds whatever `replace` ends with,
including a `\n`. *Reason*: the rule as decided names the span alone, and
read literally it stays a fact about where the span ends.

## Addendum, 2026-10-17: re-anchoring a moved comment

The owner's decision of 2026-10-17, on kindspec/blockspec#49, recorded
there. The numbered item is the owner's. Where this write-up adds precision
of its own, it says so, marked **(precision, not the owner's)**, with the
reason. `SPEC.md` §11.1 and §11.11 carry the rule.

**1. A comment may be re-anchored while it resolves `MOVED`; a suggestion
may not.** Before, `SPEC.md` re-anchored a record only while it resolved
`RESOLVED` or `EDITED`, so a comment on a paragraph that moved on a branch
kept its branch-only `base`. After a squash-merge or a rebase that rewrote
the commit holding that `base`, and once the branch was gone, it was
`REFUSED(base-unavailable)`, though its text was still in the document. The
*Decision* table's Q3 row read more widely: "each record that resolves".
Q3's row stays as first written. This narrows Q3's row for a suggestion,
to `RESOLVED` or `EDITED`, and keeps it for a comment.

Why, and what it costs:

- **A suggestion stays out.** A re-anchored suggestion would resolve
  `RESOLVED`, and so apply, where Q2 makes it stale: on a `MOVED` leaf,
  which §9's R1 cannot tell from a real move.
- **A re-anchored comment loses its moved mark**, as one already loses
  `EDITED`. It resolves `RESOLVED` on the moved paragraph, and renders as
  the anchor, no longer marked moved (`SPEC.md` §11.6).
- **Under R1, the comment ends up on the copy as `RESOLVED`.** §6 judges a
  comment that follows a false move "visible and harmless", and §5 says it
  "is shown as moved". Once re-anchored it is still harmless, and no longer
  shown as moved. That is the cost of this decision.
- **The resolver is unchanged.** What changes is what a tool may write:
  wherever §11.1 lets it re-anchor, before landing or after, a moved
  comment may now be written against the current blob, and then resolves
  `RESOLVED` instead of `MOVED`, or, once its old `base` would have gone,
  instead of `REFUSED(base-unavailable)`.

**(precision, not the owner's)** `SPEC.md` §11.11's optional CI check read
"every record that resolves has been re-based". It now covers every record
that may be re-based: a suggestion that resolves `MOVED` keeps its `base`
and is reported, as a record that does not resolve is. *Reason*: the old
wording already conflicted with §11.1 for every `MOVED` record, which
§11.1 did not let a tool re-base; the decision leaves that conflict only
for suggestions, and this reading removes it.

## Addendum, 2026-10-20: a raw U+0000 in a record

The owner's decision of 2026-10-20, on kindspec/blockspec#62, item 4. The
numbered item is the owner's. Where this write-up adds precision of its
own, it says so, marked **(precision, not the owner's)**, with the reason.
`SPEC.md` §3 and §11.1 carry the rules.

**1. A raw U+0000 in a record's anchor line is
`REFUSED(record-inconsistent)`.** `SPEC.md` §3 replaces U+0000 with U+FFFD,
as CommonMark 0.31.2 §2.3 requires, and a record is a blockspec document,
so the replacement could have reached the anchor line before its canonical
form is checked. It does not: the anchor line is checked as the file holds
it. The first addendum's string grammar spells U+0000 `\u0000`, so a raw
U+0000 there is not in the canonical form. Read the other way, the line
would hold a raw U+FFFD, which that grammar writes as itself.

**(precision, not the owner's)** In every other place, the replacement comes
before anything else reads the file: before `SPEC.md` §4.4's
conflict-marker scan, §5's frontmatter read and block parsing. *Reason*:
CommonMark §2.3 names no stage, and the reference replaces first. No current
shape depends on the order, since U+0000 and U+FFFD are both outside every
marker and fence grammar.
