# Rehearsal evidence for PRE-REGISTRATION-3.md

This directory holds the rehearsal evidence that PRE-REGISTRATION-3.md §2, §3,
§4, §9 and §10 cite. It is committed at step 2 of §7 (validation 3). Paths in
the document that start `results/prereg3/rehearsals/` are relative to
`spike/` and land here.

No rehearsal tierer saw a real packet. Every rehearsal used synthetic packets,
built from Python standard-library documentation, plus synthetic plants,
prereg 3's plants or prereg 2's three published plant packets.

## Layout

- `REHEARSALS.md`: one row per prereg 2 and prereg 3 rehearsal run, failures
  included. `tools/rehearsal_table.py` generated it from the run directories.
- `BARS.txt` and `bars-sha.log`: each pass bar, written before the runs it
  judges, and its sha256 recorded outside the file before each series.
- `cred-mtime.log`, and the `drive-*.log` files: the credential file's rewrite
  times, read from metadata only, and each series' driver output.
- `pdpe_q3.out`: P-D's and P-E's q3 answers and rationales for every v2.1 run.
- `plants/`: every version of the plants module. `candidates/`: every
  candidate tried. `plant_mutants.out`: the plant mutants.
- `prototype-harness.diff` and `prototype-PRE-REGISTRATION-3-standin.md`: the
  scratch prototype that the rehearsals ran on. Also `initcheck.out`,
  `h8check.out` and `h8sweep.out`.
- `cell_counts.out`: prereg 2's per-cell exported-packet counts (§8), counts
  only.
- `review-probes/`: the review's probes that the document cites.
- `tools/`: the rehearsal tools. `v2.0/`: the v2.0 draft, prompt and table.
- `runs.tar.xz`: every rehearsal run directory, with every transcript, and the
  export key files.
- `v6/`: V6, the rehearsal of harness3's bound tier-run code. It ran in
  `--unbound` mode, on synthetic exports, at #23's merge commit `33f3a34`.
  It holds `BARS-V6.txt`, the driver log, and each run's `check.txt`,
  `run-info.txt` and `key.json`. `v6/v6-runs.tar.xz` holds the full run
  directories and the gate fixture.
- `v6-702bad3-superseded/`: an earlier V6, run on harness3 at `702bad3`
  before the review fixes changed code that tier-run imports. It passed 10/10
  and 3/3. It is kept as superseded evidence.

## Scrubbing and redaction

Local directories are replaced by `<REHEARSAL>`, `<SCRATCH>`, `<V6>`, `<TMP>`
and `<HOME>`, in plain files and inside both archives. The names of prereg 2's
three plant packets are withheld until prereg 2's manifest commit (§10). The
staging script refuses to finish if any staged file, archived or not, still
holds a local path or one of those names. It checks for the names by
comparing the sha256 of every 16-hex token with the names' sha256 values, so
the script itself never holds the names.

The archives leave out the synthetic exports' packets and keep their key
files. Each key file maps every packet name to its plant, or to the synthetic
packet it was copied from in the rehearsal source export.

## V6: a failed run, and the owner's ruling on the bar

- **Bar B** (3 runs at 488 packets) passed 3 of 3.
- **Bar A:** `v6a-8` failed, because P-E answered q3 "no". The run is
  reported and kept.
- **The wording.** `v6/BARS-V6.txt` first said a failure "stops the series
  and fails the bar", which is stricter than the cited bar.
- **The ruling.** The owner ruled that the frozen document's cited bar governs:
  `BARS.txt` bar 1, "10 consecutive runs … A run that fails restarts the
  count", with every run kept. An addendum to `BARS-V6.txt` recorded this
  before `v6a-9`. It also set a stop condition: stop at 3 failed bar-A runs.
- **Result:** after the ruling, `v6a-9` to `v6a-18` passed: 10 consecutive. Bar A passed, with 1 failed run (`v6a-8`) among its 18 runs. The stop condition, 3 failed runs, was not reached.
- **§9's summary is wrong.** PRE-REGISTRATION-3.md §9 summarises V6's 30-packet
  bar as "one 30-packet run". That misstates the bar it cites, which is 10
  consecutive runs.
- **P-E's q3 record,** over every completed run with the final plants and
  prompt: P-E answered q3 'yes' in 46 of 47 completed runs, and 'no' in 1 (`v6a-8`). The exact one-sided 95% upper bound on the per-run 'no' rate is 9.7% (`tools/pe_record.py`, output in `pe_record.out`).

## Which harness is bound (the split reading)

As with prereg 2's #16 and #17, the harness and the validation commit are
separate pull requests:
- blockspec#23 merged harness3 as `33f3a341a6ef1995d5623795b25b48f1e70c3c00`.
- The validation pull request then adds `results/prereg3/VALIDATION`, and
  adds nothing under `harness3/` or `PRE-REGISTRATION-3.md`.

The harness it binds is the tree at `33f3a34`:

| path | git tree or blob sha at `33f3a34` |
|---|---|
| `spike/harness3` | `3b26a87215a0c51b723633b2afb423254044e07d` |
| `spike/PRE-REGISTRATION-3.md` | `f36b1ecafae7fc67edc570a8e11fea9117b4196a` |
| `spike/harness` | `cf57ca84e353810fa4c8f34f1c50ac43d10d2f54` (equal to `d79bf2e`'s) |
| `spike/PRE-REGISTRATION-2.md` | `24496a7385ca2748f899f5db7eaea20b9082ec21` (equal to `d79bf2e`'s) |
| `spike/ORACLE.md` | `4a72c84cefbd0a91cd15573caf11a6c3dff2ffe6` (equal to `d79bf2e`'s) |

The `spike/harness3` tree at `33f3a34` equals the tree at #23's last
commit, `b50beb2`.

The V0–V5 transcripts in `results/prereg3/validation/` and the V6 runs carry
the stamp `33f3a34`, the commit they ran on. The validation commit adds no
byte under `harness3/` or `PRE-REGISTRATION-3.md`, so the harness they ran is
the harness it binds.

## V6's prompt check

V6's prompt-sha assertion is made against the line "Appendix A as sent,
sha256 …" in each run's tier-run transcript, which harness3 writes before the
agent starts. It is not made against a separate run-info file. Every V6 run
recorded `2779cd58c9c7882aad9706e2e999c87f5e7b341f14f7141282a5bda798226a0f`.

## Archive checksums

- `runs.tar.xz`: `94be7f1e1b36acf0a0ef23f56a4c130594dbe1a8a42db9ba499fdfc8f5f49b25`
- `v6-702bad3-superseded/v6-runs.tar.xz`: `41f8beeb8f9b07bcedc6caaa5242bc4de981b9abd26b46feced3a416593ad04b`
- `v6/v6-runs.tar.xz`: `e25766aeb1cfcbc2a94c17cc8537910b001b171f915e970f8dbcba61d50925a3`

## Observation: tiers.jsonl rewrites

In `run-p3i-1` the tierer rewrote `tiers.jsonl` six times, and the rehearsal
monitor flagged each rewrite. Comparing every rewrite's before and after
copies, kept in that run's directory, shows that no line was lost and no line
changed: the lines were only reordered. Neither harness monitors this, and
neither pre-registration requires `tiers.jsonl` to be append-only. The bound
answer is the file as the run leaves it.
