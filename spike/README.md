<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# spike — does prose have a silent-wrong-merge?

`blockspec#2`. **This directory contains no specification, no format and no
implementation.** blockspec does not exist and may not come to. This is an
experiment that runs stock git, plus the criterion it is judged against.

Read in this order:

| file | what it is |
|---|---|
| `PRE-REGISTRATION.md` | **normative and binding.** Committed before the experiment. §8 freezes §3, §4 and §6. |
| `ORACLE.md` | the oracle, named and frozen **before** the merge arm ran, as §3.1 requires. **It is frozen, and §6 of it is wrong** — read `LOG.md` §9 and §6.2 alongside it, never on its own. |
| `harness/` | the harness, its planted cases, and the two gates |
| `results/` | raw output, pasted, not summarised |
| `LOG.md` | the running record. Candidate cases live here with `tier: UNASSIGNED`. |

## What this arm adds to D8

`PRE-REGISTRATION.md` §2.1: D8 measured a **rebase** — `git merge-file` applying
one author's real edit. That is *one* editor moving under a citation. rowspec's
defect needs **two** branches changing different things and git reconciling both
cleanly. This runs that case, against real two-parent merge commits out of real
history, with standoff anchors present and stock `git merge` doing the merging.

The mechanism under test is **imported from `kindspec/research`, never
reimplemented**, so the control arm and the merge arm measure the same thing.

## Running it

```sh
export D8_DIR=/path/to/kindspec/research/experiments/D8-identity
export CORPORA=/path/to/pinned/clones          # see harness/corpora.json

harness/run_control.sh                          # the gate: reproduce D8
python3 harness/prose_merge.py --plant          # §7: two verdicts, demonstrated
harness/armed_check.sh                          # each gate broken, watched to go red
python3 harness/check_control_gate.py --selftest
python3 harness/oracle_limitation.py            # LOG.md §6.2, demonstrated
```

**The merge arm** — the arm behind every candidate in `results/` and behind the
157/157 reconstruction claim — is not run by any of the above:

```sh
python3 harness/prose_merge.py \
  --d8-dir "$D8_DIR" \
  --corpus "rust-book=$CORPORA/rust-book:src/" \
  --corpus "obsidian-help=$CORPORA/obsidian-help:en/" \
  --corpus "cmspec=$CORPORA/cmspec:" \
  --records results/merge-arm-candidates.jsonl
```

`--corpus NAME=REPO:PREFIX` names a pinned clone and the path prefix to sample;
`PREFIX` may be empty (cmspec). `--records FILE` writes one JSON object per
candidate. `--limit N` caps cases and `--max-blocks N` caps blocks per case;
both default to 0, meaning no cap.

Corpora are **not** redistributed and **not** committed. `harness/corpora.json`
names each source and pins a commit, because a clone at HEAD is not the clone D8
ran against — and that difference turned out to matter (see `LOG.md`).

## The three gates, and why there are three

1. **The control gate** (`check_control_gate.py`) — §7: *"if the harness does
   not reproduce D8's prose result on D8's corpora, stop and fix the harness."*
2. **The planted-case gate** (`prose_merge.py --plant`) — §7: *"plant a known
   silent-wrong case and confirm the harness catches it; plant a known-clean case
   and confirm it stays silent. Both directions, both demonstrated."*
3. **The armed check** (`armed_check.sh`) — the org contract §2.2: gates 1 and 2
   reporting PASS proves nothing until each has been **broken and watched to go
   red**. Six mutations, hash-verified so a mutation that fails to apply is
   reported BROKEN rather than as a survived mutant.

There are three planted cases, not two. `single-leg-01` is the one that
**refuted this spike's own central claim** — see `LOG.md` §9 — and it is kept as
a fixture so the refutation is executable rather than narrated.

## Read these before believing anything here

- **`LOG.md` §9** — the both-legs claim is retracted. One author in one commit
  reproduces the defect; `ORACLE.md` §6 is wrong on two counts and is frozen, so
  the correction lives in the log. This changes how D8's result should be read.
- **`LOG.md` §6.2**, demonstrated by `harness/oracle_limitation.py` — TLLC has a
  third limitation beyond the two `ORACLE.md` §4/§5 name in advance. It returns
  `SURVIVED` with full confidence on single-line repeated blocks where the answer
  is undecidable. Nothing currently reported depends on it; §5's duplicate-heavy
  corpora are exactly that shape, so that arm needs a superseding oracle first.

## What is deliberately not here

- **No tier is assigned to anything.** §4.1 requires the tier to be assigned from
  the written definitions *before the frequency is known, by someone who has not
  seen the frequency*. Whoever ran this has seen frequencies and is disqualified
  from tiering their own results. Candidates carry `"tier": "UNASSIGNED"`.
- **No verdict.** §6's FOUND / NOT FOUND / NEAR MISS is not decided here.
- **No duplicate-heavy corpora.** §5's second arm requires an amendment naming
  them, recorded in §8 with a date and a reason, with an argument per choice.
  That has not been done, so that arm has not been run.
