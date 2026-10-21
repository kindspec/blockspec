# U+0000 is replaced in every leaf type that carries text

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
and the four chosen case directories were also fetched, for names only.)

## The input

`input.md` is 24 bytes, three blocks, each holding one raw U+0000 byte (`\0`):

    # A\0B
    (blank)
    C\0D
    (blank)
    ```
    E\0F
    ```

## Expected

Accepted. A heading on line 1, a paragraph on line 3, a fenced code block on
lines 5 to 7, no names. Leaf content: `"A�B"`, `"C�D"` and
`"E�F\n"`.

## Why

SPEC.md §3:

> **U+0000 is replaced with U+FFFD**, as the pinned grammar requires
> (CommonMark 0.31.2 §2.3, "Insecure characters").

The sentence is unconditional and sits in §3, *Encoding and lines*, before
any block or leaf rule, so it applies to the document as read, and so to every
leaf's content.

SPEC.md §6.3:

> **A leaf's content is its parsed content, as CommonMark parses it, with
> container prefixes removed**

SPEC.md §12, Reading 8, gives each type's content:

> a paragraph's raw content (CommonMark §4.8: each line's initial spaces or
> tabs removed, joined by `\n`, final spaces or tabs removed); a heading's
> raw content (CommonMark §4.2); a code block's lines between the fences,
> each ending in `\n`, with the fence's indentation removed and no info
> string;

None of these strips or keeps a U+0000; each is taken over the text §3 has
already replaced. So the heading's raw content is `A`, U+FFFD, `B`; the
paragraph's is `C`, U+FFFD, `D`; and the code block's one line is `E`,
U+FFFD, `F` followed by `\n`.

The three leaf types are the ones §6.2 says an anchor can land in, other than a
table:

> A marker and a thematic break carry no text, so an anchor lands in a
> paragraph, heading, fenced code block or table.

The structure (three blocks, their line ranges, `names: {}`) needs nothing
beyond §4.1's table of admitted blocks and §6.1:

> **A block is a top-level node.**

U+FFFD, like U+0000, is not a space or tab, so it changes no block boundary,
heading opening or fence.

## Not asserted

No `resolve` entry: the heading's slug depends on whether U+FFFD is in
github-slugger 2.0.0's character class, which SPEC.md §8.2 does not quote
(see `AMBIGUITIES.md`). A table leaf is left out to keep the case to the three
types named in the task; §3's sentence covers it equally.
