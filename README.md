# blockspec

A file format and test suite for prose documents that must survive version
control.

A blockspec document is a markdown file that renders and edits correctly in
today's markdown tools. It adds one convention, a marker that lets an author
name a part of the document. It refuses the markdown constructs that mature
parsers read differently, or that hide what a merge did.

```markdown
# Runbook

<!-- #restart -->
## Restart the service

Run `systemctl restart app`, then check the logs.
```

The marker names the heading after it, and renders as nothing. A comment or a
transclusion can point at `restart` and keep working when the text around it moves.

Unlike a [rowspec](https://github.com/kindspec/rowspec) row, **a block gets no
minted id**, so nothing has to be written into the prose. Identity is computed
from content where it can be, and named by an author where it must be.
[`DESIGN-BRIEF.md`](DESIGN-BRIEF.md) has the measurement behind that.

## Status

Draft 0. [`SPEC.md`](SPEC.md) is the format, `conformance/cases/` encodes it,
and `reference/blockspec/` is the only implementation so far. It is not on
PyPI.

The experiment behind the format found that prose does have a silent wrong
merge worth a format. That verdict came from a second run under an owner ruling
made after the first run's result was public, so read
[the status page](docs/status.md) before relying on it.

## Try it

From a clone, with Python 3.11 or newer and no dependencies:

```sh
git clone https://github.com/kindspec/blockspec
cd blockspec
PYTHONPATH=reference python3 -c '
import blockspec
doc = blockspec.parse("<!-- #intro -->\nHello.\n")
print(doc.names)
'
```

`parse` raises `Refusal`, with a `SPEC.md` §9 code, on a document it won't
accept.

## Check documents

```sh
blockspec check docs/    # refuses a document the profile cannot read safely
```

It exits 0 when every document reads, 1 when one is refused, and 2 when
nothing was checked. `--format github` writes annotations. In CI:

```yaml
- uses: actions/checkout@v7
- uses: kindspec/blockspec@v0.1.0
  with:
    paths: docs
```

## The reference's API

`reference/blockspec/` is standard library only, and run from its source
tree (`pythonpath = ["reference"]`).

| function | what it does |
| --- | --- |
| `parse(text)` | reads a document, or raises `Refusal` with a `SPEC.md` §9 code; the `Document` has `frontmatter`, `blocks`, `leaves`, `names` and `resolve(name)` |
| `conform(text, queries)` | `parse` as the conformance runner calls it |
| `resolve(repo, queries)` | §11's anchors and transclusions, as the runner calls it (`anchor.py`) |
| `edit.replace_block(text, node, source)` | the text with block `node`'s lines replaced by `source` |
| `edit.insert_block(text, source, before=, after=)` | the text with `source` inserted as a block before or after a block, or after the last |
| `edit.delete_block(text, node)` | the text without block `node` |

A block is named by its node path, `[i]`. Each `edit` function reads its
result back and raises `Refusal`, or its subclass `edit.EditRefused` for the
API's own reasons, rather than return a document whose other blocks or names
read differently. It never touches a `<doc>.notes/` record.
[`docs/editing-api.md`](docs/editing-api.md) gives the rules, and `tests/edit-cases/` pins them.

## Develop

```sh
just setup      # install dependencies
just check      # format and lint
just test       # the tests
just conform    # the conformance tree against the reference
just mutants    # break the reference; the suite must notice
```

## More

- [`DESIGN-BRIEF.md`](DESIGN-BRIEF.md): what was decided and measured before the
  format was written.
- [`docs/adjudications/`](docs/adjudications/): the decisions that define draft 0.
- [`spike/`](spike/README.md): the experiment.
- [kindspec](https://github.com/kindspec): the other formats.
