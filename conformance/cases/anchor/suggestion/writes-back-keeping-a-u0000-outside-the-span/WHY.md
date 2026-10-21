# A suggestion writes back and keeps a raw U+0000 outside its span

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
`tree/` and `written/` directories of the two anchor cases were not read; this
case's layout follows README.md, *The kind `anchor`*, *Files*.)

## The repository

`tree/policy.md` is one paragraph line, with a raw U+0000 (`\0`) at code
point 3:

    Ref\0 A-17: the reactor scram threshold is 4.2 sigma above baseline.

`tree/policy.md.notes/01J9Z3M8Q4X7V2K6T0R5N1B801.md` is an open suggestion
made against the current blob (`{{blob:tree/policy.md}}`), replacing
`4.2 sigma` with `4.0 sigma`. Its `leaf.text` holds U+FFFD, written as itself
in UTF-8 (`EF BF BD`), where the file holds U+0000. The U+0000 is outside the
span and outside its 32-code-point prefix: the text before the span is 42 code
points, and the prefix is its last 32, ` the reactor scram threshold is `.
The suffix, ` above baseline.`, is 16 code points and reaches the leaf's end.

## Expected

`RESOLVED`, on leaf `[0]`, a paragraph, span `[42, 51]`; the suggestion
applies, and `written/policy.md` is the current file with `4.2` changed to
`4.0` and **the raw U+0000 byte kept**:

    Ref\0 A-17: the reactor scram threshold is 4.0 sigma above baseline.

## Why the U+0000 survives in the written file

SPEC.md §11.7, *Write-back*, step 3:

> Replace the range with `replace`, written exactly as stored and never
> normalised, except at its line breaks. [...] Nothing outside the range
> changes.

The range is the span's raw range, from step 2:

> Map `a` and `b` through the parse to raw positions, skipping the
> characters above. The raw text between them is the span's raw range.

The U+0000 lies before `a`, so it is outside the range, and "Nothing outside
the range changes." The written file holds the U+0000 byte, not U+FFFD. §3's
replacement governs how the document is read; nothing in §11.7 writes the
read text back over the file. The paragraph before the steps says each content
code point maps to one raw character, which is how a U+FFFD in the content is
traced back to the U+0000 it was read from:

> Through the parse, each code point of the leaf's content comes from one
> raw character of its lines.

README.md, *What a case asserts*, defines the compared file:

> `FILE` is a path relative to the case directory, such as
> `written/policy.md`, and holds the exact bytes of the current document
> after §11.7's write-back of `replace` (its steps 1 to 3).

## Why the anchor resolves and the suggestion applies

`leaf.text` holds U+FFFD because it is the leaf's content. SPEC.md §11.1:

> `leaf.text` | the leaf's content (§6.3), normalised to Unicode NFC, with
> `\n` line endings

and SPEC.md §3:

> **U+0000 is replaced with U+FFFD**, as the pinned grammar requires
> (CommonMark 0.31.2 §2.3, "Insecure characters").

U+FFFD is not one of the code points §11.1's string grammar escapes, so it is
written as itself:

> Every other code point in U+0000 to U+001F, in U+007F to U+009F, and
> U+2028, U+2029, U+FEFF, U+FFFE and U+FFFF is written `\u` followed by four
> lower-case hex digits. Every other code point is written as itself, in
> UTF-8.

U+FFFD and the ASCII text around it are unchanged by NFC.

The document is unchanged since `base`, so its one text-bearing leaf has a key
that occurs once in each snapshot. SPEC.md §11.3, step 1:

> Take each key that occurs exactly once in `base` and exactly once in the
> current text, as a pair of positions. [...] Its pairs are `EXACT`.

No current leaf is unmatched, so no rule of §11.4's `EXACT` branch applies,
and §11.5 says:

> For `EXACT` and `MOVED`, the span keeps its offset in the paired leaf

giving `[42, 51]`. §11.6: `RESOLVED` is "`EXACT`, and the span found".

SPEC.md §11.7:

> **A suggestion applies only when its record's `status` is `open` and its
> anchor is `RESOLVED` or `EDITED`**

The span maps (step 1): the content before `a` normalises to `leaf.text`
before the span, and the content from `a` to `b` is `4.2 sigma`. None of
§11.7's stale shapes applies: `replace` holds no `\n`, the span holds no tab
remainder, and the leaf is not a code block.

The record meets §11.1's consistency rules: `prefix + span + suffix` occurs
once in `leaf.text`, the prefix is exactly 32 code points, and the suffix is
shorter than 32 only because the leaf's edge is there.
