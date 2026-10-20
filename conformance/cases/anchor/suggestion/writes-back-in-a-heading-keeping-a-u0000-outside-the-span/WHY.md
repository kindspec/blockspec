# A suggestion in a heading writes back and keeps a raw U+0000 outside its span

Provenance: written from SPEC.md at blob `9ffce46c2e6495698bc6fec6a6235a2f2022dbbf`
(kindspec/blockspec, ref `main`, fetched 2026-10-20) alone, by an author who saw
no implementation. Files read, by sha256 of the decoded bytes:

- `SPEC.md` `93c9c4cfc7dfc250b1179c9e8d577caf6d353d7a1b74c50bd26fb157fe0ffd98`
- `conformance/cases/README.md` `31897c4b049d5231c1f44bde11bf3bdb02d27ee4ae56a62212c37b248d00e53e`
- `conformance/cases/leaf/heading-closing-sequence/expect.json` `f6a4736f484f41f3fff3ff2f169b2a45093a78c0141d1a8a0d18c359924b0065`
- `conformance/cases/leaf/tilde-fence-with-info-string/expect.json` `ce8b0a7e56dd6eaff9c4ad890d7eb0c52632c81870b1d7296b0a07c3b12ed74e`
- `conformance/cases/anchor/suggestion/writes-back-without-normalising/expect.json` `f6b2eaa633f6944f5c24e0257dab695db275fd183cab54fee7f8686c1dec4aec`
- `conformance/cases/anchor/suggestion/writes-back-into-a-crlf-file/expect.json` `7c01999035f571b0e4216acb3dcc214631abc672bfcf5886c68d0b210c99169a`

(Directory listings of `conformance/cases/leaf/`, `conformance/cases/anchor/suggestion/`
and the four chosen case directories were also fetched, for names only. The
`tree/` and `written/` directories of the existing anchor cases were not read;
this case's layout follows README.md, *The kind `anchor`*, *Files*.)

## The repository

`tree/policy.md` is one ATX heading line, with a raw U+0000 (`\0`) after
`Ref`:

    # Ref\0 A-17: the reactor scram threshold is 4.2 sigma above baseline

`tree/policy.md.notes/01J9Z3M8Q4X7V2K6T0R5N1B801.md` is an open suggestion
made against the current blob (`{{blob:tree/policy.md}}`), with `leaf.type`
`h1`, replacing `4.2 sigma` with `4.0 sigma`. Its `leaf.text` is the heading's
raw content, `#` and the space after it removed, with U+FFFD written as itself
in UTF-8 where the file holds U+0000. The U+0000 is content code point 3,
outside the span and outside its prefix. The text before the span is 42 code
points; the prefix is its last 32, ` the reactor scram threshold is `. The
suffix, ` above baseline`, is 15 code points and reaches the leaf's end.

## Expected

`RESOLVED`, on leaf `[0]`, a heading, span `[42, 51]`. The suggestion
applies, and `written/policy.md` is the current file with `4.2` changed to
`4.0`. **The `# ` opening and the raw U+0000 byte are kept**:

    # Ref\0 A-17: the reactor scram threshold is 4.0 sigma above baseline

## Why the written file is this

SPEC.md §11.7, *Write-back*:

> Through the parse, each code point of the leaf's content comes from one
> raw character of its lines.

Each code point of the heading's content therefore has a raw source. The U+FFFD
at content position 3 comes from the U+0000 at raw byte 5. Content positions
42 and 51 come from raw positions 44 and 53, two further on because of the
opening `# `. That `#` and its space are raw characters no content code point
comes from. The heading's content is "the ATX heading's raw content (§4.2):
without the opening `#` run, an optional closing `#` run, and the spaces around
them" (README.md, *Leaves and their content*; SPEC.md §12, Reading 8: "a
heading's raw content (CommonMark §4.2)").

Steps 1 to 3:

> 1. Let `a` and `b` be the positions in the leaf's content, before NFC, such
>    that the NFC form of the content before `a` is `leaf.text` before the
>    span, and the NFC form of the content from `a` to `b` is `span`. If there
>    are no such positions, the span does not map.
> 2. Map `a` and `b` through the parse to raw positions, skipping the
>    characters above. The raw text between them is the span's raw range.
> 3. Replace the range with `replace`, written exactly as stored and never
>    normalised, except at its line breaks. [...] Nothing outside the range
>    changes.

The raw range is `4.2 sigma`. The `# ` opening and the U+0000 both lie before
it, so "Nothing outside the range changes" keeps both. The U+0000 is not
rewritten as U+FFFD. §3's replacement governs how the file is read, and
nothing in §11.7 writes the read text back over the file. README.md, *What a
case asserts*: `written/policy.md` "holds the exact bytes of the current
document after §11.7's write-back of `replace` (its steps 1 to 3)."

None of §11.7's stale shapes applies:
- `replace` holds no `\n`.
- The span holds no tab remainder.
- The leaf is not a code block.

The parenthetical list of non-content raw characters before the steps names
container prefixes, paragraph indentation and line endings. It does not name a
heading's `#` run. The list is descriptive: the deciding rule is the sentence
quoted first, which says every content code point comes from one raw character.
The `#` run is outside the content by Reading 8, so `a` and `b` map past it.

## Why the anchor resolves and the suggestion applies

SPEC.md §11.1: `leaf.type` is "`p`, `h1` to `h6`, `code` or `table`: a
paragraph, a heading with its level". `leaf.text` is "the leaf's content
(§6.3), normalised to Unicode NFC, with `\n` line endings". SPEC.md §3:
"**U+0000 is replaced with U+FFFD**". U+FFFD is not in §11.1's escape list
("Every other code point is written as itself, in UTF-8"). NFC leaves this text
unchanged.

The document is unchanged since `base`, so the heading's key occurs once in
each snapshot. SPEC.md §11.3, step 1: "Take each key that occurs exactly once
in `base` and exactly once in the current text, as a pair of positions. [...]
Its pairs are `EXACT`." No current leaf is unmatched, so no `EXACT` rule of
§11.4 applies. §11.5: "For `EXACT` and `MOVED`, the span keeps its offset in
the paired leaf", which gives `[42, 51]`. §11.6: `RESOLVED` is "`EXACT`, and
the span found".

SPEC.md §11.7: "**A suggestion applies only when its record's `status` is
`open` and its anchor is `RESOLVED` or `EDITED`**".

The record meets §11.1's consistency rules:
- `prefix + span + suffix` occurs once in `leaf.text`.
- The prefix is exactly 32 code points.
- The suffix is shorter only because the leaf's end is there.
