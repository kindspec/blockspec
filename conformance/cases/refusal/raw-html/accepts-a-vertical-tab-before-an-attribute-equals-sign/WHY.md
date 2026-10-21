# refusal/raw-html/accepts-a-vertical-tab-before-an-attribute-equals-sign

Input, one line: `<a b`, U+000B (vertical tab), `=c>`, LF.

Outcome: accepted: one paragraph, line 1.

Written blind, from these files alone, checked by hash:

- `SPEC.md` sha256 `9635b4a43bff3d7d16497e8cbfae7863d65597ac9941aa9769a634fa14537a09`
- `cases-README.md` sha256 `83410445e19c2ca4797dc76feb073d3936b25b544abde7e4193ab027d4bb14c8`
- `case-body.schema.json` sha256 `9512b41c957f0acae91c2ae84e7b1948e574bc06ea600e039991605152b3dcc8`
- `CASE-TREE.md` sha256 `ae9ef062966f380ebdbcdf3223d2d1d8f9ca5e294bc199166ce3c755493e7a8d`
- `commonmark-0.31.2-spec.txt` (CommonMark 0.31.2) sha256 `257c41ad946f7a1414a499aca402a1aa8fdac3678532266611348c1cf54f4b80`

## Why

1. CommonMark 0.31.2, *Characters and lines*: "A [tab](@) is `U+0009`." and "A [space](@) is `U+0020`." A form feed (U+000C) and a vertical tab (U+000B) are neither, and neither is a line ending ("A [line ending](@) is a line feed (`U+000A`), a carriage return (`U+000D`) not followed by a line feed, or a carriage return and a following line feed.").
2. CommonMark 0.31.2, *Raw HTML*: "An [attribute](@) consists of spaces, tabs, and up to one line ending, an [attribute name], and an optional [attribute value specification]." The space begins an attribute named `b`.
3. CommonMark 0.31.2, *Raw HTML*: "A [tag name](@) consists of an ASCII letter followed by zero or more ASCII letters, digits, or hyphens (`-`)." and "An [attribute name](@) consists of an ASCII letter, `_`, or `:`, followed by zero or more ASCII letters, digits, `_`, `.`, `:`, or `-`." The attribute name ends at `b`.
4. CommonMark 0.31.2, *Raw HTML*: "An [attribute value specification](@) consists of optional spaces, tabs, and up to one line ending, a `=` character, optional spaces, tabs, and up to one line ending, and an [attribute value]." Its optional spacing before `=` is spaces, tabs or a line ending; U+000B (vertical tab) is none of them and is not `=`, so `b` has no value specification.
5. CommonMark 0.31.2, *Raw HTML*: "An [open tag](@) consists of a `<` character, a [tag name], zero or more [attributes], optional spaces, tabs, and up to one line ending, an optional `/` character, and a `>` character." No further attribute can begin at U+000B (vertical tab), and it is not spacing, `/` or `>`, so no open tag is complete.
6. CommonMark 0.31.2, *HTML blocks*, start condition 7: "line begins with a complete [open tag] (with any [tag name] other than `pre`, `script`, `style`, or `textarea`) or a complete [closing tag], followed by zero or more spaces and tabs, followed by the end of the line." Condition 7 does not hold.
7. CommonMark 0.31.2, *HTML blocks*, start condition 6: "line begins with the string `<` or `</` followed by one of the strings (case-insensitive) `address`, `article`, `aside`, ... `ul`, followed by a space, a tab, the end of the line, the string `>`, or the string `/>`." The tag name here is `a`, which is not in that list, and the line does not go on to spell `address`, `article` or `aside`. Conditions 1 to 5 need `<pre`, `<script`, `<style`, `<textarea`, `<!--`, `<?`, `<!` and a letter, or `<![CDATA[`, none of which the line begins with.
8. CommonMark 0.31.2: "A line containing no characters, or a line containing only spaces (`U+0020`) or tabs (`U+0009`), is called a [blank line](@)." The line is not blank.
9. CommonMark 0.31.2, *Paragraphs*: "A sequence of non-blank lines that cannot be interpreted as other kinds of blocks forms a [paragraph](@)." and "The paragraph's raw content is formed by concatenating the lines and removing initial and final spaces or tabs." cases-README.md, *Leaves and their content*: `paragraph` content is "CommonMark's raw content (§4.8): the lines, each with its initial spaces or tabs removed, joined by `\n`, with final spaces or tabs removed". Content is the line.
10. SPEC.md §4.2: "**Inline content is opaque text** ... a leaf's inline content is kept as written and is not parsed"; §12, Reading 6: "The suite reads it [`raw-html`] as block-level only". So the inline tag-like text in the paragraph is not refused.
11. SPEC.md §4.3 judges "A delimiter line and the paragraph line over it"; a one-line document has no delimiter line, so `ambiguous-table` cannot apply, and no other §9 refusal fits a single paragraph line that is not a setext underline, a link reference definition or a conflict marker.
12. Its tab twin is `refusal/raw-html/refuses-a-tab-before-an-attribute-equals-sign`, which was written earlier and is not edited to list this case.

No reading is taken.
