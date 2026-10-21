# refusal/raw-html/refuses-a-tab-before-a-single-quoted-attribute-value

Input, one line: `<a b=`, U+0009 (tab), `'q'>`, LF.

Outcome: refused: `raw-html`.

Written blind, from these files alone, checked by hash:

- `SPEC.md` sha256 `9635b4a43bff3d7d16497e8cbfae7863d65597ac9941aa9769a634fa14537a09`
- `cases-README.md` sha256 `83410445e19c2ca4797dc76feb073d3936b25b544abde7e4193ab027d4bb14c8`
- `case-body.schema.json` sha256 `9512b41c957f0acae91c2ae84e7b1948e574bc06ea600e039991605152b3dcc8`
- `CASE-TREE.md` sha256 `ae9ef062966f380ebdbcdf3223d2d1d8f9ca5e294bc199166ce3c755493e7a8d`
- `commonmark-0.31.2-spec.txt` (CommonMark 0.31.2) sha256 `257c41ad946f7a1414a499aca402a1aa8fdac3678532266611348c1cf54f4b80`

Controls (each differs from this input in the byte under test only): `refusal/raw-html/accepts-a-form-feed-before-a-single-quoted-attribute-value`, `refusal/raw-html/accepts-a-vertical-tab-before-a-single-quoted-attribute-value`.

## Why

1. CommonMark 0.31.2, *Raw HTML*: "An [attribute value specification](@) consists of optional spaces, tabs, and up to one line ending, a `=` character, optional spaces, tabs, and up to one line ending, and an [attribute value]." The tab is the optional spacing after `=`.
2. CommonMark 0.31.2, *Raw HTML*: "An [attribute value](@) consists of an [unquoted attribute value], a [single-quoted attribute value], or a [double-quoted attribute value]." CommonMark 0.31.2, *Raw HTML*: "A [single-quoted attribute value](@) consists of `'`, zero or more characters not including `'`, and a final `'`." `'q'` is one.
3. CommonMark 0.31.2, *Raw HTML*: "An [open tag](@) consists of a `<` character, a [tag name], zero or more [attributes], optional spaces, tabs, and up to one line ending, an optional `/` character, and a `>` character." `>` follows, so the line begins with a complete open tag.
4. CommonMark 0.31.2, *HTML blocks*, start condition 7: "line begins with a complete [open tag] (with any [tag name] other than `pre`, `script`, `style`, or `textarea`) or a complete [closing tag], followed by zero or more spaces and tabs, followed by the end of the line." The end of the line follows, so the line starts an HTML block of type 7.
5. SPEC.md §4.1: "an HTML block that is not a region marker (`raw-html`)", and §9, item 4: "`raw-html`: an HTML block that is not a region marker". §7.1: a region marker is a line matching `^[ \t]*<!--[ \t]*#[a-z0-9][a-z0-9-]*(:begin|:end)?[ \t]*-->[ \t]*$`, which a line beginning `<a` or `</a` does not.

No reading is taken.
