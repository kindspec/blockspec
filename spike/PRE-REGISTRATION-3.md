<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Pre-registration 3: the final tiering of prereg 2's exported records

**Status: approved by the owner on 2026-10-11.** "Committed" means merged to
`main`. Nothing under this document runs before it merges. The rehearsal
evidence it cites is committed under `spike/results/prereg3/rehearsals/` at step 2 of §7; paths below
that start `results/prereg3/rehearsals/` are relative to `spike/`.

**Scope.** This document is a second, separate tiering of the records that
`PRE-REGISTRATION-2.md` (prereg 2) exported at its scoring-arm commit. It
brings new tiering instruments: five plants, two of them positive controls,
a revised tierer prompt, a packet manifest in the export, new packet names,
and a start day. Every arm, cell, rule, sample and result of prereg 2 stands
as committed, and prereg 2's own tiering runs first, as registered (§7). Prereg
2's §4–§8 apply here unchanged unless a section below says otherwise.

**Citations.** A blockspec path means its content at `a680dd8` on `main`,
which contains the scoring-arm commit `e46e320`. Two files are not yet on
`main`: `results/prereg2/tier-model.json` and the Models API listing, from the
tier-model commit `ef62c84` on branch `prereg2/tiers`. This document pins
`tier-model.json` by its git blob,
`3ded7091b9b7b825853c140ee7ecc3c63bef2e96`
(`git rev-parse ef62c84:spike/results/prereg2/tier-model.json`), so the
commit that lands it on `main` does not matter. Every figure is given with the
command that produced it.

---

## 0. Choices the owner is approving

The owner decided the order: this document is reviewed, approved
and committed first; then prereg 2's bound tier-run runs as registered and its
verdict is published first; then this document re-tiers, and its verdict is
published beside prereg 2's, never as a revision of it (§7, §8). Approving the
document also approves the following, each as written.

1. **Positive-control plants (§3).** Two plants expect "yes": P-D expects q3
   "yes", and P-E expects q3 and q4 "yes". The export holds 483 real packets
   and 5 plants. *Alternative:* three plants, all expecting q3 and q4 "no".
   That set cannot catch a tierer that answers "no" by default, which is the
   bias that produces a false FOUND (§2.5).
2. **This is the final tiering (§8, §11).** These are the last tiers of the
   records exported at `e46e320`. No later pre-registration re-tiers them.
   *Alternative:* leave re-tiering open, which lets tiering repeat until a
   verdict is liked.
3. **Which verdict governs blockspec#2's next step (§8).** If prereg 2's
   tiering is void, this document's verdict governs. If it is not void, prereg
   2's verdict governs. Either way, prereg 2's verdict stands as published, and
   both verdicts are reported together. In the predicted case, a void tiering,
   this document's verdict governs. *Alternative:* this document's verdict
   governs whatever prereg 2's tiering gives.
4. **This document re-tiers whatever prereg 2's tiering gives (§7, §8).** Its
   verdict is published in every case, so the two can be compared.
   *Alternative:* re-tier only if prereg 2's tiering is void.
5. **P-A and P-C are re-authored, and P-B is revised (§3).** Each keeps
   prereg 2's expected answers.
6. **The export carries `PACKETS.txt`, and Appendix A changes in four places
   (§4).**
7. **The model stays `claude-opus-5-5`, as fixed on 2026-10-10 (§6).**
8. **Harness changes land in new files only (§9).** Nothing under
   `spike/harness/`, `PRE-REGISTRATION-2.md` or `ORACLE.md` changes.
9. **Appendix A adds one sentence for q3 (§2.7, §4):** "For question 3, a
   quote that matches more than one place does not by itself show that it
   landed wrong." The sentence's bars were set in advance, and it passed both:
   10 of 10 at 30 packets, and 3 of 3 at full size (§3). P-D and P-E answered
   q3 "yes" in every run, so the sentence did not suppress a true "yes". The
   full-size figures, each size counted on its own:

   | prompt | packets per run | completed runs | failed | 95% upper bound on the per-run failure rate |
   |---|---|---|---|---|
   | v2.0, without the sentence | 30 | 10 | 0 | 25.9% |
   | v2.0, without the sentence | 488 | 3 | 1 (`p3f-2`: P-B and P-C q3 "yes") | 86.5% |
   | v2.1, with the sentence | 30 | 10 | 0 | 25.9% |
   | v2.1, with the sentence | 488 | 3 | 0 | 63.2% |

   Bounds are exact one-sided 95% (Clopper–Pearson). Three runs bound a rate
   only weakly. Not counted: `run-p3h-1`, a v2.1 full-size run that stopped on an
   authentication error (§2.8) after 280 of 488 packets. `BARS.txt` recorded it
   as an environment abort and restarted the bar before the next run.
   *Alternative:* the v2.0 prompt, without the sentence.
10. **A run that dies on an authentication error binds, as prereg 2's run
    rule says (§2.8, §6).** There is no exception for it. The first run that
    writes any line binds, partial or not: its untiered real packets make
    their cells NO VERDICT, and an untiered plant voids the tiering. Two
    operating rules make such a death unlikely, and they apply to this
    document's run and to prereg 2's frozen run alike:
    - start a bound run just after the credential file has been rewritten;
    - keep every other Claude session off the account during the run.

    Under those rules, the restarted full-size bar ran 3 of 3 with no auth
    abort (`p3i-1` to `p3i-3`). The credential file's mtime stayed 08:52:20Z
    before and after each run. The refresh interval is not measured yet:
    `cred-mtime.log` holds one rewrite, at 08:52:20Z, and the file was still
    unchanged at 10:20:52Z, so the interval is at least 1 h 28 min. A
    full-size run took 960 to 2,401 seconds.

    *Rejected alternative:* allow one rerun when the committed transcript ends
    in 401 or 403 and nobody has read the aborted run's answer lines. It was
    rejected for three reasons:
    - a 401 can be caused by a second session on the account, which the
      operator controls;
    - "nobody reads the answer lines" cannot be enforced while the work
      directory is readable on the host;
    - so the exception would be a reroll the operator can trigger, which is
      exactly the forking path the final-tiering rule (item 2) closes.

## 1. What this keeps, and what it changes

**Kept, unchanged:** prereg 2's question (§2), mechanisms (§3), FOUND and its
conditions F1–F9 (§4), oracle (§5), units, corpora, selection, sampling and
floors (§6), tiers and questions (§7.1, §7.2), the run rules and the
disqualification rule (§7.3), and outcomes (§8). Also kept: the validation
commit `d79bf2e`, the Arm 0 commit `c5ddbe6`, the scoring-arm commit
`e46e320`, every record in them, prereg 2's gap file, and the tier model in
`tier-model.json`. The set of exported real records is the same.

**Changed:**

| prereg 2 | here |
|---|---|
| Appendix B: P-A, P-B, P-C | Appendix B below: new P-A, revised P-B, new P-C, new P-D and P-E |
| void rule over three plants | the same rule over five plants (§3) |
| Appendix A | Appendix A below: one sentence clarified, one added, one paragraph added, last line changed |
| export: `PROMPT.md`, `packets/` | adds `PACKETS.txt`; `QUESTIONS.md` carries the new Appendix A |
| nonce sealed at validation | a new nonce, sealed at this document's validation commit |
| start day: day after `e46e320` | start day: §6 |
| tierer argv | adds `--strict-mcp-config`, and the harness checks the agent's tool list (§6) |
| harness at `d79bf2e` | that harness, unmodified, plus new files (§9) |

**The void rule** is prereg 2 §7.3's, applied to every plant: the tiering is
void if any plant's computed tier falls on the wrong side of the B/C line, if
any plant's q3 or q4 differs from its expected answer, or if any plant is
untiered. Confusing A with B does not void it.

## 2. Why the instruments change

These findings come from rehearsals of prereg 2's tier-run. A rehearsal runs
the tier-run path in `--unbound` mode, in the same bubblewrap sandbox, with the
same model, argv and credential mount as the bound run, on synthetic exports.
No rehearsal tierer saw a real packet (§10). `results/prereg3/rehearsals/REHEARSALS.md` lists every run,
failures included. `rehearsal_table.py` generates it from the run directories.

**2.1 P-A fails question 3.** Prereg 2's P-A labels the misplaced copy
"Superseded Ingest wording, kept for audit:". The tierer reads the label and
answers that a reader can tell the reference landed wrong: q3 "yes", where
prereg 2 expects "no". The real P-A packet did this in 5 of 5 runs, and the
synthetic analogue R-A in 3 of 3. Under prereg 2 §7.3 this voids the tiering.
**Prereg 2's expected answer is arguable.** The label does make the landing
visible, so "yes" is a defensible reading, and this document uses that shape as
a q3 "yes" control (P-D). Source: the `run-p30-*`, `run-120-*`, `run-486-*`
and `run-486m-*` rows of `results/prereg3/rehearsals/REHEARSALS.md`.

**2.2 P-C fails question 4 sometimes.** P-C repeats one section note twice in
a short section. In 2 of 8 runs, counting P-C (5 runs) and its synthetic
analogue R-C (3 runs) together, the tierer
called the duplicate a visible author error: q4 "yes", where "no" is expected.
This also voids. Source: the same rows.

**2.3 The tierer can miss packets.** The agent's Glob tool lists at most 100
entries. In the 120-packet rehearsal the tierer missed packet
`8fb62437cc92bad4` and still reported "I've answered all 120 packets". Under
prereg 2, a missed real packet makes its cells NO VERDICT, and a missed plant
voids the tiering. Source: the `answered` column of `results/prereg3/rehearsals/REHEARSALS.md`.

**2.4 Cost is not a constraint.** The 486-packet rehearsal took 1,020
seconds (`wall_seconds` in its `run-info.txt`).

**2.5 Every prereg 2 plant expects q3 "no" and q4 "no".** A tierer that
answers "no" to q3 and q4 by default passes prereg 2's void rule. That is the
bias that turns a mis-resolution into a false FOUND, because F6 is q4 "no" and
F7 is q3 "no". Prereg 2's plants cannot detect it. P-D and P-E can (§3).

**2.6 Answers vary widely from run to run.** The same synthetic packets,
tiered in different runs by the same model, get different answers. These
figures compare runs. They are not accuracy: the synthetic packets have no
answer key. "Would qualify" means tier A or B with q3 "no" and q4 "no", the
tiering half of FOUND.

- On the synthetic packets of the 120-packet export, "would qualify" came out
  22 of 116 in `run-120`, 0 of 117 in `run-486`, and 23 of 117 in `run-486m`.
  `run-486` answered q4 "no" on all 117.
  (`python3 -I -S -B results/prereg3/rehearsals/review-probes/qual.py <rehearsal dir>`.)
- The same packets in `run-120` and `run-486m` agreed on q4 in 68 of 119.
  (`results/prereg3/rehearsals/review-probes/noise.py`, line "old-prompt 120 vs new-prompt 486m".)
- On all 486 packets, `run-486` (prereg 2's prompt) and `run-486m` (this
  document's prompt) gave q3 "yes" 484 vs 337, q4 "yes" 1 vs 147, and
  "would qualify" 1 vs 139. They agreed on q3 for 339 packets and on q4 for
  338. (`results/prereg3/rehearsals/review-probes/cmp486.py`.)

**2.7 At full size, q3 can flip on duplicated text.** In `run-p3f-2`, which
had 488 packets, P-B and P-C answered q3 "yes" because the quote visibly
matches more than one place. In the 30-packet runs they answered "no" every
time with the final prompt. This is a question of how q3 is read. Under
prereg 2 §2, a reader "must be unable to detect" the mis-resolution. A reader
who sees two matches knows the reference is ambiguous. That reader still cannot
tell that it landed on the wrong one. Real packets with duplicated text meet
the same reading, so this is not only a plant problem. One sentence added to
Appendix A answers it (§0 item 9, §4). With that sentence the full-size bar
passed 3 of 3 (§3).

**2.8 A tier-run can die on the host's credential.** `run-p3h-1` stopped at
08:52Z on `401 … OAuth token revoked`. The host's
`~/.claude/.credentials.json` had been rewritten at that same minute (its
mtime). The sandbox binds that one file read-only, so the tierer keeps a token
that a refresh elsewhere on the host has revoked. The cause looks like token
rotation by another session on the same account, but that is inferred, not
reproduced. Prereg 2's bound tier-run has the same exposure. Under the run
rules, a run that dies this way after writing lines **binds**: it is not a
zero-line run, so no rerun is allowed, its untiered real packets are NO
VERDICT, and an untiered plant voids it. §6 and §0 item 10.

So one tiering run is a noisy instrument. The plants check the tierer, per run,
on five known shapes. They do not measure its accuracy on real packets. This is
a limit of the method, stated before the run, and §8 reports it with the
verdict.

## 3. The plants

Appendix B gives the texts. Each plant is a quote anchor. Its packet fields are
generated as prereg 2 §7.3 says: the harness runs on the plant's before- and
after-file, TLLC's one-leg form gives the oracle target, and the hardened quote
resolver gives the mechanism target. Nothing is hand-written.

| plant | tests | expected q1 q2 q3 q4 | tier |
|---|---|---|---|
| P-A | a tier-A silent-wrong that a reader cannot see | yes yes no no | A |
| P-B | a B case: same text, different subject | yes no no no | B |
| P-C | a C case: same text, same scope | no no no no | C |
| P-D | positive control: a wrong landing a reader can see | yes yes yes no | A |
| P-E | positive control: a wrong landing explained by a visible author error | yes yes yes yes | A |

- **P-A.** The edit moves the old retry wording into a new "Defaults" section
  and gives Ingest its own value. The quote now matches the Defaults block
  exactly, once. Nothing marks that block as old or wrong.
- **P-B.** Prereg 2's P-B, with one change. In the before-file, Beta's status
  reads "under review", so the approved status line occurs once and the
  reference's origin is unambiguous. The edit moves the telemetry scope to
  Beta and approves Beta with the identical line. Why: in `run-p3b-5` the
  tierer marked prereg 2's P-B unplaceable. Its reason was that the line occurs
  twice in the before-file, so "the files don't show which occurrence the
  reference … meant". That is true of prereg 2's P-B. It had passed in the 22
  earlier runs that carried it (5 `p30`, 13 `p3`, 4 `p3b`). The revised P-B
  was marked unplaceable once more, in `run-p3d-9`, because its two targets
  have the same text. That doubt applies to any packet of this shape, so it is
  answered in the prompt (§4), not in the plant.
- **P-C.** A page-wide note, "All times on this page, in every section, are
  UTC.", opens every section as a convention. The edit splits out a Sunday
  section, and the resolver lands on another copy of the note. The words "in
  every section" were added after one rehearsal of the version without them
  answered q1 "yes" (`run-p3-3`).
- **P-D.** Prereg 2's P-A shape in new words: the misplaced copy sits under a
  "Change log" heading, labelled "Superseded Backup wording, kept for the
  change log:". Its texts are the same as `build.py`'s synthetic plant R-A,
  which drew q3 "yes" in 3 of 3 runs before P-D existed (§2.1).
- **P-E.** The edit raises an upload limit, "80 GB, raised from 50 GB in
  May,", and leaves a stale duplicate "Upload limits" section, with the old
  50 GB text, at the end of the file. The resolver lands on the stale copy.
  The words "raised from 50 GB in May" were added after one rehearsal of the
  version without them answered q3 "no", because "nothing marks which copy is
  current" (`run-p3c-9`).

**Realisable.** The prototype check `prereg3_plants.py` (§9, H2) printed:

    P-A: TLLC=('SURVIVED', 3) hard=EXACT,1 repeat_decided=True -> OK
    P-B: TLLC=('SURVIVED', 2) hard=EXACT_CTX,5 repeat_decided=True -> OK
    P-C: TLLC=('SURVIVED', 4) hard=EXACT_CTX,1 repeat_decided=True -> OK
    P-D: TLLC=('SURVIVED', 1) hard=EXACT,6 repeat_decided=True -> OK
    P-E: TLLC=('SURVIVED', 1) hard=EXACT,5 repeat_decided=True -> OK
    PLANTS: PASS

The harness's own `evaluate()` path, which builds each packet, gives the same
targets, decided, with the hardened policy `WRONG`.

**Mutants.** Each plant has mutants, each hash-verified as applied, and the
check goes red on each. `python3 -I -S -B plant_mutants.py <harness> <d8> <work>`
printed (one line per mutant, shortened):

    P-A Defaults says four       RED  hard=REFUSED_MARGIN,None
    P-A Ingest unchanged         RED  hard=EXACT_CTX,3
    P-B Beta status dated 03-05  RED  hard=EXACT,2
    P-C keeps old window time    RED  TLLC=('SURVIVED', 1) hard=EXACT_CTX,1
    P-D change-log copy edited   RED  hard=REFUSED_MARGIN,None
    P-D retention unchanged      RED  hard=EXACT_CTX,1
    P-E stale duplicate removed  RED  hard=FUZZY,1
    P-E limit unchanged          RED  hard=EXACT_CTX,1
    unmutated: PLANTS: PASS exit 0
    MUTANTS: ALL RED

A structural mutant shows only that the harness would notice a plant that no
longer realises. A *semantic* change that keeps the targets, such as P-C's
note reverting to "in this section", passes the harness check. Only rehearsal
answers test the plants' meaning.

**What the plants catch.** In one run, they catch a tierer whose answers on
these five shapes do not follow the files: one that answers q3 or q4 "no" by
default (P-D, P-E), one that answers them "yes" by default (P-A, P-B, P-C),
and one that puts a same-text, same-scope landing above the B/C line (P-C).
They also catch a run that skips a plant. They do not show that the tierer
answers real packets correctly, which have other shapes, and §2.6 shows that
its answers vary from run to run. This replaces v1's claim that the plants
catch a tierer that "misreads the questions", which the evidence does not
support.

**Rehearsed.** `results/prereg3/rehearsals/BARS.txt` set two bars before the first five-plant
run, and logged each restart before the next series began.

- **Bar 1: 10 consecutive 30-packet runs with every plant's q1–q4 right.**
  - Passed with the final plants and the final prompt, `run-p3e-1` to
    `run-p3e-10`: 10 of 10, all 30 packets answered in each.
  - It took four series. `p3b` stopped at run 5 (P-B unplaceable). `p3c`
    stopped at run 9 (P-E q3 "no"). `p3d` stopped at run 9 (P-B unplaceable).
  - Each stop led to the revision named in §3 or §4, and the count restarted.
- **Bar 2: three runs at full size, 483 synthetic fillers plus the five
  plants, 488 packets, every plant right in all three. FAILED.**
  - `run-p3f-1` and `run-p3f-3` passed, each answering 488 of 488.
  - `run-p3f-2` answered 488 of 488, but P-B and P-C both answered q3 "yes".
    The reasons given were "the quote matching twice is visible" and "the
    triple match is visible". Under the void rule that run would void.
  - `p3f-3` was run after the failure only because the bar named three runs.
    `BARS.txt` records this before its result.
- **v2.1 (§0 item 9's sentence added). Bars set before the first run, in
  `BARS.txt` at 07:49:30Z.** Its sha256 is recorded outside the file in
  `bars-sha.log`, at 08:10Z during the 30-packet series, and again at 08:36Z,
  14 seconds after `run-p3h-1` began.
  - **Bar 1′, 30 packets: PASSED.** `run-p3g-1` to `run-p3g-10`, 10 of 10,
    30 of 30 packets in each.
    - P-D answered q3 "yes" in all 10, each time citing the "Superseded" label.
    - P-E answered q3 "yes" in all 10, each time citing the 50 GB copy against
      the live "80 GB, raised from 50 GB" text. None cited only the duplicate
      match.
  - **`run-p3h-1`, 488 packets: environment abort.** The tierer wrote 280
    lines. Then the API answered 401 "OAuth token revoked", and the agent
    exited with status 1. P-A was among the untiered packets. P-B, P-C, P-D
    and P-E were tiered, and all four were right. This says nothing about the
    answers.
  - **The bar restarted.** `BARS.txt` recorded the abort and restarted bar 2′
    as `p3i-1` to `p3i-3`, same criteria, with any further auth abort to stop
    the series. Its sha256 went into `bars-sha.log` at 08:58:00Z, before
    `p3i-1` started at 08:58:20Z. The drive log records the credential file's
    mtime, from `stat -c %Y` only, before and after each run. It was 08:52:20Z
    throughout.
  - **Bar 2′, 488 packets: PASSED 3 of 3.** `run-p3i-1`, `-2` and `-3` each
    answered 488 of 488, with every plant's q1–q4 as expected. Wall time was
    1,560, 960 and 2,401 seconds.
    - P-D and P-E answered q3 "yes" in all three.
    - Every P-E rationale cites the 50 GB copy against the live 80 GB.
  - **Across all 14 v2.1 runs,** P-D and P-E answered q3 "yes" 28 times in 28
    (`pdpe_q3.out`). Every run recorded the draft's prompt sha256, 14 of 14
    (V6's assertion, applied here).
- **Rates, never pooled across sizes.** The table is in §0 item 9:
  - at 30 packets, 0 failures in 10 runs under each prompt, 95% upper bound
    25.9%;
  - at full size under v2.0, 1 failure in 3, bound 86.5%;
  - at full size under v2.1, 0 failures in 3 completed runs, bound 63.2%.

Source: `results/prereg3/rehearsals/REHEARSALS.md`. Its summary groups runs by plant set, prompt and
packets per run, so 30-packet and full-size runs are never pooled.

## 4. The packet manifest, and Appendix A

**`PACKETS.txt`.** The export root holds one more file, `PACKETS.txt`: every
packet name in the export, plants included, sorted, one per line, each line
ending in `\n`. The validator fails an export whose `PACKETS.txt` is missing,
a symlink, or not exactly the packets under `packets/`. The sandbox binds it
read-only at `/work/PACKETS.txt`.

**Accepted leak.** The packet count is 488: 483 exported real records plus 5
plants. It is a numerator with no denominator, as prereg 2 §7.3 accepts. A
reader who knows prereg 2's count, 486, can infer that two more plants were
added, which reveals nothing about any record.

**Appendix A.** Four changes from prereg 2's, and no others:

1. "They differ." becomes "They differ: unless the oracle says the text was
   deleted, they are different places in the after-file, even when their text
   is the same." Why: in `run-p3b-5` and `run-p3d-9` the tierer marked P-B
   unplaceable because its two targets have the same text and "the packet
   gives no location". Real packets of the same shape would meet the same
   doubt. The sentence states a fact that holds for every exported packet,
   because a packet exists only when the mechanism's block and the oracle's
   block differ, or the oracle says the text was deleted.
2. A new paragraph after the second: "`PACKETS.txt` names every packet, one per
   line. Work from that list, not from a directory listing, which can be cut
   short."
3. A sentence after "answer the four questions from the files alone.": "For
   question 3, a quote that matches more than one place does not by itself
   show that it landed wrong." Why: §2.7. This reads F7 as prereg 2 §2 states
   it ("unable to detect"). It must not suppress a true q3 "yes", so P-D's and
   P-E's q3 answers were checked in every run (§3).
4. The last line, "Stop when every packet has a line.", becomes "Stop when
   every packet in `PACKETS.txt` has a line."

`PROMPT.md` is Appendix A with the `> ` quoting removed, as in prereg 2. Its
sha256, as rehearsed, is
`2779cd58c9c7882aad9706e2e999c87f5e7b341f14f7141282a5bda798226a0f`
(`python3 -I -S -B results/prereg3/rehearsals/review-probes/appa.py PRE-REGISTRATION-3.md`). `QUESTIONS.md` is
prereg 2's §7.1 table and §7.2, cut from `PRE-REGISTRATION-2.md` as prereg 2
cuts them, followed by this document's Appendix A.

**Coverage stays a rule.** The manifest makes a full pass likely, not certain.
Prereg 2's rule stands: a real packet with no line makes every cell that
exported it NO VERDICT, and an untiered plant voids the tiering. Rehearsal
coverage is in §3 of `results/prereg3/rehearsals/REHEARSALS.md` and in §10 below.

## 5. The export, regenerated

`prereg3.py export` (§9, H5) writes a new export, once, at step 3 of §7. It:

1. refuses if prereg 2's tiering has started (the order guard, §9 H5);
2. reads `results/prereg2/score/`, accepting each input only if it is bound
   to `d79bf2e` (§9 H6);
3. selects records with prereg 2's `select_packets` and builds fields with its
   `packet_fields`, unchanged;
4. names each packet `sha256(nonce3 + ":" + packet key)[:16]`. `nonce3` is a
   new 32-byte nonce from `os.urandom`, sealed in this document's manifest at
   step 2. The plants are keyed `plant:P-A` to `plant:P-E`;
5. writes `PROMPT.md`, `PACKETS.txt`, and each packet with this document's
   `QUESTIONS.md`;
6. runs the checks below and exits 0 only if all pass. Their output is in
   step 3's transcript.

**Same records, checked without reading them.** The check reads prereg 2's
export from `e46e320`'s tree (`git show e46e320:<path>`), not from the work
tree. For each packet in that export and in the new one, the check hashes the content: every
`packet.json` field except `packet`, and every file except `QUESTIONS.md`.
The new export's real packets must equal prereg 2's packets as a multiset,
less exactly three. Those three must equal prereg 2's plants as
`p2/export.py`'s `plant_records` regenerates them. The new export's five plant
packets must equal this document's plants as H2 regenerates them. The check
prints counts and pass/fail, never a name or a text. Expected: 486 in prereg 2's
export (`ls spike/results/prereg2/export/packets | wc -l`), so 483 real plus 5
plants is 488.

**Per name, later.** At step 9, once prereg 2's sealed manifest is committed,
`aggregate` also checks each real key's packet under prereg 2's name and under
this document's name for equal content. It prints only the count checked and
the count that differ, which must be zero.

Prereg 2's export stays in place, committed and unchanged.

## 6. The tierer, the start day and the window

- **Model.** `claude-opus-5-5`, read from `results/prereg2/tier-model.json`,
  pinned by blob `3ded7091b9b7…`. Prereg 2 chose it on 2026-10-10 by its own
  rule, and that choice holds however late tiering runs. No new listing is
  taken.
- **Start day.** The first UTC calendar day after the committer date of
  prereg 2's verdict commit (§7, step 5).
- **Window.** Within 14 days of that commit's UTC day. A later run is logged
  with its reason and changes nothing else.
- **Runs, isolation, disqualification.** As prereg 2 §7.3: a fresh agent, the
  same sandbox plus `PACKETS.txt`, one binding run, at most one rerun and only
  if the first wrote zero lines, every transcript committed, and whoever ran an
  arm may not tier. A run that writes zero lines for any reason, including the
  model not being served, allows the one rerun. If that also writes nothing,
  every cell that exported a packet is NO VERDICT.
- **The credential (§2.8).** For the length of a tier-run, nothing else on
  the host may use the account whose credential the sandbox binds. The harness
  logs the credential file's sha256 and mtime before the agent starts and
  after it exits. If the transcript ends on an authentication error (HTTP 401
  or 403), the ledger records the run as `auth_aborted`. This is a label for
  the record and changes nothing. The run binds under the run rule like any
  other run that wrote a line (§0 item 10).
- **No connectors.** The agent argv adds `--strict-mcp-config`. Before the
  agent reads anything, the harness checks the agent's first JSON event. It
  must be the `system/init` event, its tool list must be exactly `Edit, Glob,
  Grep, Read, Write`, and its MCP server list must be empty. The harness stops
  the agent if the first JSON event is anything else, if the list differs, or
  if the stream ends with no init event. The check also applies to stub
  agents. A run that fails the check is recorded as `init_failed`. Its work
  directory is kept and committed. It never binds, even if the agent wrote a
  line before it was stopped. That race is real: the prototype, given a stub
  whose first event was not init, stopped it, but the ledger still showed one
  line written.
- **The cap on runs.** There is one rerun in total, ever, whatever caused it:
  a first run that wrote zero lines, or a first run recorded as
  `init_failed`. That is the natural reading of prereg 2 §7.3, which allows
  "at most one rerun", and the harness enforces it by refusing a third
  started run. If the rerun also fails the init check or writes zero lines,
  every cell that exported a packet is NO VERDICT.
- **Why `--strict-mcp-config`.** Without the flag, 10 of the 21 rehearsals
  before this draft listed a claude.ai account connector, "claude.ai Claude
  Docs", as pending. No run used it (§10). Prereg 2's bound run has the same
  exposure, and this document does not change prereg 2.

## 7. Order of work

Prereg 2's commits 1–3 are on `main`: validation `d79bf2e`, Arm 0 `c5ddbe6`,
scoring and export `e46e320`. The rest are separate commits, in this order.

1. **This document merges.**
2. **Validation 3.** The new harness files (§9), the V-step transcripts, the
   rehearsal evidence under `results/prereg3/rehearsals/` (§10), and the sha256
   of the new sealed manifest in `results/prereg3/VALIDATION`. The manifest
   itself stays outside the repository.
3. **Export 3.** The regenerated export, its file manifest, and the check
   transcript of §5, under `results/prereg3/`.
4. **Prereg 2's `prereg2/tiers` branch lands on `main`**, if it has not
   already: both of its commits, `da61140` (two refused tier-model attempts)
   and `ef62c84` (the tier model), unchanged.
5. **Prereg 2's `tiers.jsonl`, then its sealed manifest, reproductions, join
   and verdict**, exactly as prereg 2 registers them, with prereg 2's harness.
   The verdict is `results/prereg2/verdict.json`, published in `LOG.md`.
6. **This document's `tiers.jsonl`**, from its bound `tier-run` on export 3.
7. **Reproductions.** `prereg3.py repro` for every record that §9 H7 says needs
   one.
8. **This document's sealed manifest.**
9. **This document's join and verdict**, `results/prereg3/verdict.json`,
   published in `LOG.md` beside prereg 2's.

Steps 2 and 3 come before step 5, so this document's plants, prompt, nonce and
export are fixed before any tierer answers on a real packet. The harness
enforces that (§9 H5).

**Timeline.** Prereg 2's window ends on 2026-10-23. That is the last day
`p2/tierrun.py`'s `is_late` accepts. The scoring-arm commit's UTC day is
2026-10-09: `git log -1 --format=%cI e46e320` gives
`2026-10-09T19:43:10-04:00`, which is 23:43 UTC. If steps 1–4 take longer,
prereg 2's tier-run is a late run under prereg 2. It needs `--late-reason`, is
logged with its reason, and changes nothing else.

## 8. How this relates to prereg 2's frozen rules

Four rules in prereg 2 bear on this document.

- **§7.1:** "No tier is revised after `tiers.jsonl` is committed."
- **§10:** "After [the Arm 0] commit, no further pre-registration may address
  this question in a way that changes any cell or the overall verdict computed
  here. That verdict is published first."
- **§9, gaps:** "After the scoring-arm commit. No gap claim, code change or
  later supersession alters any cell."
- **§7.3, start:** "A later run is logged with its reason and changes nothing
  else."

**Prereg 2 is left whole.** Its tier-run runs on its own export, with its own
plants and prompt, its `tiers.jsonl` is committed as written, and its cells and
overall verdict are computed by its own harness and published first (§7, step
5). This document edits none of its files and changes none of its cells.

**Why this is a separate tiering, not a revision.** §7.1 forbids changing a
tier after `tiers.jsonl` is committed. Nothing here changes one. Prereg 2's
`tiers.jsonl` and every tier computed from it stay as committed, and prereg 2's
verdict is computed from them. This document makes a new tiering: a new
registration, frozen before any tierer sees a real packet; a new export, with
new names and five plants; a new `tiers.jsonl` in `results/prereg3/`; and a new
verdict, published under this document's name. The purpose of §7.1 is that
tiers cannot move once results are seen. That purpose holds because every
instrument here is fixed at steps 1–3, before step 5 shows anyone a tier of a
real packet, and because of the final-tiering rule below.

**The final-tiering rule.** This document is the final tiering of the records
exported at `e46e320`. Its `tiers.jsonl`, once committed, is not revised, and
no later pre-registration may tier those records again, or re-tier them by
another route. A later pre-registration may address blockspec#2 only with new
records. Owner approval item 2.

**What prereg 2 is expected to give.** The rehearsals predict that its tiering
will be void: P-A answered q3 "yes" in 5 of 5 runs (§2.1). When tiering is
void, every cell that exported a packet becomes NO VERDICT, and FOUND is
impossible. Prereg 2's NOT FOUND needs a NOT FOUND Q cell in E, S5 or S25 for
both `k8s-en` and `cncf-toc`. Every one of those six cells exported at least
one packet:

| arm | E Q | S5 Q | S25 Q |
|---|---|---|---|
| `k8s-en` | 7 | 10 | 25 |
| `cncf-toc` | 4 | 3 | 2 |

(`python3 -I -S -B cell_counts.py spike/harness spike/results/prereg2/score`,
which prints only per-cell counts. The cell sets total 483 distinct packet
keys, the export's count of real packets. The full table is in `results/prereg3/rehearsals/`.)
So a void prereg 2 tiering gives INCONCLUSIVE overall, never NOT FOUND or
NOT FOUND (Q only). The case where prereg 2 is void but not INCONCLUSIVE
cannot happen.

**Which verdict governs blockspec#2.** Owner approval item 3. The rule is
fixed now, before either verdict exists:

- **Prereg 2's tiering is void.** Its overall verdict is then INCONCLUSIVE
  (above), and prereg 2 §8 keeps blockspec#2 open. This document's overall
  verdict decides blockspec#2's next step, by prereg 2 §8's table, whatever
  form it takes. The forms are FOUND; NOT FOUND and NOT FOUND (Q only), each
  with or without "… with near misses"; and INCONCLUSIVE. This is the
  predicted case.
- **Prereg 2's tiering is not void.** Prereg 2's verdict decides blockspec#2's
  next step, as prereg 2 registered it. This document's verdict is still
  computed and published beside it, with any difference stated (item 4).

In both cases prereg 2's verdict stands as published and is published first.
The rule changes nothing in the predicted case, and it leaves prereg 2 §10
untouched in the other. *Alternative,* written out in item 3: this document's
verdict governs in both cases.

**The noise of §2.6 is reported with the verdict.** A FOUND here rests on one
tiering run. The write-up states §2.6's figures beside it and names every
qualifying packet's answers, so a reader can weigh it.

**"Changes nothing else."** That sentence is about lateness: a late run is
still the same run, with the same model, plants and prompt. Nothing here relies
on it. This document's tier-run is not a later run of prereg 2. It is a
separate run under a separate registration, so it changes nothing in prereg 2.

## 9. Validation, and the harness changes

**Why new files.** Prereg 2's binding refuses every bound command once any
commit after `d79bf2e` touches `spike/harness/`, `PRE-REGISTRATION-2.md` or
`ORACLE.md`. Prereg 2's tier-run, repro and aggregate still have to run
(§7, step 5). So this document's code goes in `spike/harness3/`, imports
prereg 2's modules unmodified, and writes under `results/prereg3/`.

**Harness change list.**

- **H1. Binding.** `harness3/p3/binding.py` is `p2/binding.py` with its
  namespace as a parameter: bound paths `harness3/` and
  `PRE-REGISTRATION-3.md`, results under `results/prereg3/`, validation file
  `results/prereg3/VALIDATION`, execution markers under
  `results/prereg3/executed/` and `<git common dir>/prereg3/`. It also refuses
  unless every file under `harness/`, `PRE-REGISTRATION-2.md` and `ORACLE.md`
  equals its blob at `d79bf2e`, compared with `git hash-object` against
  `git ls-tree`.
- **H2. Plants.** `harness3/prereg3_plants.py` holds Appendix B's texts, each
  plant's anchored block, oracle target and mechanism target, and runs the
  same four checks as `prereg2_plants.py`, reusing its `repeat_decided`.
  `harness3/p3/plants.py` holds the expected answers of §3's table and the
  plant manifest loader: a sealed manifest must list exactly P-A to P-E, keyed
  `plant:P-x`, with this document's expectations, never the manifest's own.
  Its `void_reasons` applies §1's void rule to all five. `p2/export.py`'s
  `PLANT_EXPECT` stays at three plants. Prereg 2's code reads it in
  `p2.tiers.void_reasons` and `p2.export.load_manifest`, and
  `p2.aggregate.aggregate` computes `void` through the former (its line 102)
  before it builds any cell. With a five-plant manifest that path raises
  `KeyError` on P-D. So `harness3` never calls those three functions; H8 says
  what it calls instead.
- **H3. Export.** `harness3/p3/export3.py`:
  - `prompt_text3()`: this document's Appendix A, quoting removed. The
    document is pinned by its sha256 as merged.
  - `questions_text3()`: prereg 2's §7.1 table and §7.2, cut by
    `p2/export.py`'s rules, then this document's Appendix A.
  - `MANIFEST = "PACKETS.txt"` and `manifest_text(names)`.
  - `plant_records3()`: `p2.export.plant_records`'s logic over H2's plants.
  - `export3(...)`: `p2.export.select_packets` and `packet_fields` unchanged;
    names from `nonce3`; writes `PROMPT.md`, `PACKETS.txt` and the packets;
    then `validate3` and the checks of §5.
  - `validate3(root)`: `p2.export.validate`'s checks, with `PACKETS.txt` in the
    root allow-list, and `PROMPT.md`, `QUESTIONS.md` and `PACKETS.txt` compared
    with H3's texts.
  - `same_records(export2, export3)` and `same_plants(export3)`: §5's checks.
- **H4. Tier-run.** `harness3/p3/tierrun3.py` is `p2/tierrun.py`'s `run`
  with these differences:
  - it validates with `validate3`;
  - the sandbox adds `--ro-bind <export>/PACKETS.txt /work/PACKETS.txt`, and
    the clean-up list includes `PACKETS.txt`;
  - the argv adds `--strict-mcp-config`, and the `system/init` check of §6
    runs;
  - the start day and window are §6's;
  - the ledger and work directories are under `results/prereg3/`;
  - the model is read from `results/prereg2/tier-model.json`, refused unless
    that file's blob is `3ded7091b9b7b825853c140ee7ecc3c63bef2e96`.

  **The gate.** It refuses unless all of these hold in HEAD's history:
  - exactly one commit adds `results/prereg2/verdict.json`. As committed, the
    file has `"bound": true` and a binding whose `validation_commit` is
    `d79bf2e61f5f7c0bcfdde5e17d44604b0fac9301`, and it is unchanged since that
    commit;
  - a commit adds `results/prereg2/tiers.jsonl`, and it is an ancestor of the
    verdict commit;
  - `results/prereg2/tier-runs.txt` is committed with at least one
    `"started"` entry, in a commit that is an ancestor of the verdict commit.

  Prereg 2's `aggregate` accepts zero tier-runs, so a verdict alone is not
  proof that prereg 2's tiering ran. The gate does not read the verdict's
  value: §0 item 4 re-tiers whatever it says.
- **H5. Commands.** `harness3/prereg3.py` provides `seal`, `export`,
  `validate-export`, `tier-run`, `repro` and `aggregate`, with `prereg2.py`'s
  refusals: `python3 -I -S`, no repeated or abbreviated options, `--unbound`
  for tests, and a transcript for every invocation.
  **The order guard:** `export` refuses if prereg 2's tiering has started.
  That means `results/prereg2/tier-runs.txt` or any
  `results/prereg2/tier-work-*` exists in any of these places:
  - the work tree;
  - any other work tree of the repository, as `git worktree list` names
    them;
  - any ref or reflog
    (`git log --all --reflog --full-history --format=%H -- <path>` is not
    empty).

  Prereg 2's tier-run writes no marker in `<git common dir>/prereg2/`.
  `p2/binding.py` writes such markers only for `arm0`, `score` and `export`,
  so other work trees are scanned instead. **This guard catches mistakes; it
  is not a guarantee.** It cannot see a tier-run in a separate clone, in a
  work tree that was removed, or on a branch deleted with its work tree.
  **The committed order check** catches a binding prereg 2 tier-run that ran
  out of order. It does not catch an earlier tier-run that was thrown away
  and left no record. `aggregate` runs it from committed records only, and
  refuses unless both hold:
  - the commit that adds `results/prereg3/export/` (step 3) is an ancestor of
    the commit that adds `results/prereg2/tiers.jsonl` (step 5);
  - the first `"started"` entry's `at` in the committed
    `results/prereg2/tier-runs.txt` is later than the `# executed:` time in
    step 3's committed export transcript.
- **H6. Inputs.** `aggregate` and `export` accept prereg 2's Arm 0 results and
  scores only if each is `"bound": true` with a binding whose
  `validation_commit` is `d79bf2e`, at its pin and bundle, as
  `check_pin_and_bundle` checks. Anything else is a refusal. `aggregate` passes
  prereg 2's gaps through: `p2.gaps.load_gaps(spike, e46e320, arms)`.
- **H7. Reproductions (F9).** `aggregate` raises `MissingRepro` for every
  record that meets F1–F6 under this document's answers and has no
  reproduction. Prereg 2's repro results are bound to `d79bf2e`, and prereg 2's
  `load_repro` marks a result from another validation commit unbound, so F9
  fails silently and a FOUND becomes `NOT FOUND … F9` (`results/prereg3/rehearsals/review-probes/reprodemo.py`
  printed `same repro, marked unbound (other validation commit) -> NOT FOUND |
  … F9: 1 record(s) do not reproduce`). So:
  - `prereg3.py repro` is `prereg2.py repro` under H1's binding. It writes
    `results/prereg3/repro/`. It runs at step 7 for every record that meets
    F1–F6 under this document's `tiers.jsonl` and has no accepted result.
  - `aggregate` accepts a reproduction result only if it has `"bound": true`
    and its binding's `validation_commit` is `d79bf2e` (from
    `results/prereg2/repro/`) or this document's validation commit (from
    `results/prereg3/repro/`). Any other result is a refusal, not an unbound
    result. If two accepted results carry the same record id and disagree, that
    is a refusal too.
  - The record is the same in both cases. Prereg 2's harness evaluates it, and
    H1 guarantees that harness is byte-identical to `d79bf2e`.
- **H8. Aggregate.** Replacing `p2.aggregate.aggregate`'s returned `void`
  after the fact would not work. `cell()` has already used prereg 2's void, at
  its line 214, so a P-D or P-E failure would leave a cell FOUND. So
  `harness3/p3/aggregate3.py` reimplements only the top-level loop of
  `p2.aggregate.aggregate`, about 30 lines:
  - It computes `void` with H2's `void_reasons` over all five plants, from this
    document's manifest (H2's loader) and `tiers.jsonl`.
  - It calls `p2.aggregate.cell()` unchanged for every cell, passing that
    five-plant `void`. So every cell that exported at least one packet becomes
    NO VERDICT, with the reason, whenever any plant fails.
  - It applies H6's gaps as prereg 2 does.
  - It computes the overall verdict with `p2.aggregate.overall()` unchanged,
    from those cells.
  - Inputs are H6's, reproductions H7's.
  - It then runs §5's per-name check and the order check of H5.
- **No change** to anything under `spike/harness/`.

**The prototype.** The rehearsals ran on a scratch copy of `spike/harness/`
with two files edited and one added: 52 changed lines in the diff
(`grep -c '^[+-][^+-]' results/prereg3/rehearsals/prototype-harness.diff`). `p2/export.py`
writes and validates `PACKETS.txt`, takes Appendix A and the plants from the
new sources, and lists P-D and P-E. `p2/tierrun.py` binds `PACKETS.txt`, adds
`--strict-mcp-config`, and runs the init check.

The init check was tightened after the last series ended, so no rehearsal ran
the tightened version. It now covers a first event that is not init and a
stream that ends with no init, and stubs are no longer exempt. Three stub runs
exercise it (`results/prereg3/rehearsals/initcheck.out`):
- a stub whose first event is not init is stopped;
- a stub with no init event is flagged;
- a stub with the exact init event runs.

The stopped stub had already written one line, which is why §6 adds
`init_failed`. `prereg3_plants.py` is new. The diff is in
`results/prereg3/rehearsals/prototype-harness.diff`. The bound implementation puts this logic in
H2–H4 and leaves `spike/harness/` alone. H8 is prototyped separately, in
`harness3/p3/aggregate3.py`, over prereg 2's unmodified `p2`. It takes the
reviewer's FOUND fixture. `h8check.py` writes the plants' right answers out
independently of the code under test. Then it changes one answer at a time,
and prints (shortened):

    all plants right: FOUND | overall FOUND | void []
    P-D q3=no: NO VERDICT | tiering void: P-D: q3=no, expected yes | overall INCONCLUSIVE
    P-E q4=no: NO VERDICT | tiering void: P-E: q4=no, expected yes | overall INCONCLUSIVE
    P-C answered tier B (q1=yes; q3, q4 right): NO VERDICT | … B/C line … | overall INCONCLUSIVE
    V4 mutant (void not passed to cell), P-D q3=no: FOUND | … | overall FOUND
      -> KILLED by the P-D case
    four-plant manifest: refused: the manifest's plants are not prereg 3's Appendix B
    H8 CHECK: PASS

The reviewer's six-mutant sweep over `aggregate3.py` (`results/prereg3/rehearsals/tools/sweep.py`) hashes
the file before and after each mutation. All six go RED
(`results/prereg3/rehearsals/h8sweep.out`):
- the void not passed to `cell()`;
- P-D's q3 expectation flipped;
- the q3 check dropped;
- P-E's q4 expectation flipped;
- the B/C check removed;
- the manifest check removed.

The two flipped expectations are now caught by the manifest check, against the
independent table.

The unchanged bound validator refuses a manifest export. On a rehearsal
export it reported `export root holds files outside the allow-list:
['PACKETS.txt']`.

**V steps.** These run before the validation commit and follow prereg 2 §9's
V-failure rule. V1 and V2 are not rerun: nothing they cover changes.

- **V3.** Each new component goes red on a planted case and on an empty
  input.
  - **Plants.** `prereg3_plants.py` prints `PLANTS: PASS` and goes red on each
    mutant of §3. The loader refuses a manifest with three plants, six plants,
    or one changed expectation.
  - **Void rule.** It fires on P-D answering q3 "no", on P-E answering q4 "no",
    on P-A answering q3 "yes", on P-C landing in tier B, and on each plant left
    untiered. It does not fire on A↔B confusion.
  - **Void reaches the cells (H8).** Take a fixture that is FOUND with every
    plant right. Change only P-D's q3 to "no". Every cell that exported a
    packet then becomes NO VERDICT, with the void as its reason, and the
    overall verdict becomes INCONCLUSIVE.
  - **Manifest.** `validate3` rejects a missing `PACKETS.txt`, a symlink, one
    that omits a name, one with an extra name, and an unsorted one. It accepts
    a clean export.
  - **Prereg 2 untouched.** H1 refuses a fixture checkout in which one byte
    under `harness/` differs from `d79bf2e`.
  - **Namespace.** In a fixture repository, a prereg 3 export marker lands
    under `<git common dir>/prereg3/`. A prereg 2 marker does not stop a
    prereg 3 command, and a prereg 3 marker does not stop a prereg 2 command.
  - **Same records and same plants.** Both pass on fixture exports built like
    the real ones. They go red when one byte of one real packet changes, when a
    real packet is missing, when a fourth prereg 2 plant is in excess, and when
    one plant packet's text changes.
  - **Order guard.** `export` refuses when `results/prereg2/tier-runs.txt`
    is in the work tree; when it is only in another work tree; when it was
    committed and then deleted, so that only history holds it; and when only a
    reflog holds it. The same applies to a `tier-work-1/` directory. It runs
    when none exists.
  - **Committed order check.** `aggregate` refuses on a fixture history in
    which the commit adding `results/prereg2/tiers.jsonl` does not descend from
    the export-3 commit. It also refuses when the first started `at` in
    `tier-runs.txt` is earlier than export 3's `# executed:` time. It passes on
    a fixture history in the order of §7.
  - **Inputs.** A score or Arm 0 result bound to another validation commit is
    refused. One marked unbound is refused. One bound to `d79bf2e` is
    accepted. A gap in `gaps.json` makes its cell NO VERDICT in `aggregate`.
  - **Reproductions.** A repro bound to `d79bf2e` is accepted, and so is one
    bound to this document's validation commit. One bound to any other commit
    is refused, as is one with `"bound": false`, and so is a pair of accepted
    results with the same id that disagree. A record that meets F1–F6 with no repro stops `aggregate` with
    `MissingRepro`, and never yields `NOT FOUND … F9`. The `reprodemo.py`
    case gives FOUND.
  - **Start day and window.** With a fixture prereg 2 verdict commit on day
    D, `tier-run` refuses on day D, runs on day D+1 and on day D+14, and on day
    D+15 needs `--late-reason`.
  - **Gate.** `tier-run` refuses on each of these fixtures:
    - no `results/prereg2/verdict.json`;
    - one marked `"bound": false`;
    - one bound to another commit;
    - one changed after it was added;
    - a verdict with no committed `tiers.jsonl`;
    - a verdict with no committed `tier-runs.txt`, or with one that has zero
      started runs.
  - **Model pin.** `tier-run` refuses when `tier-model.json`'s blob differs.
  - **Sandbox.** A stub agent can read `/work/PACKETS.txt` and cannot write
    it.
  - **Credential and auth abort.** A stub whose transcript ends on a 401 is
    recorded as `auth_aborted`, with the credential file's sha256 and mtime
    before and after. If it wrote a line, it binds, and no rerun is allowed.
  - **Run cap.** After a zero-line first run and an `init_failed` rerun, a
    third `tier-run` is refused. The same holds in the other order.
  - **Init check.** Each of these stubs is stopped, and its run is recorded
    as `init_failed` and does not bind, even if the stub wrote a line first:
    - one that reports an extra tool in its `system/init` event;
    - one that reports a non-empty MCP server list there;
    - one whose first JSON event is not `system/init`;
    - one that ends its stream with no init event.

    A stub with the exact init event runs.
  - **Coverage.** A stub that answers every packet but one real packet makes
    that packet's cells NO VERDICT. One that skips a plant voids the tiering.
- **V4.** A mutation sweep over H1–H8, as prereg 2's V4. Each mutation is
  hash-verified, a mutation that does not apply is BROKEN, and no survivor and
  no BROKEN is allowed. It includes at least one mutant for each of: the start
  day and window; the input binding to `d79bf2e`; the repro acceptance rule;
  the order guard; the committed order check; the plant-content check; the
  `tier-model.json` blob pin; the gate and each of its three conditions; the
  init check; the five-plant void rule; and **the propagation of that void
  into `cell()`**. The last means a mutant that passes prereg 2's three-plant
  void, or none, to `cell()`, which the V3 case above must kill.
- **V5.** Prereg 2's V5 stays green.
- **V6. Rehearsal of the bound code.** `prereg3.py tier-run --unbound` runs on
  synthetic exports with this document's plants. The pass bar, set before
  any v2 rehearsal (`results/prereg3/rehearsals/BARS.txt`): one 30-packet run with every plant's
  q1–q4 as expected, and three runs at full size, 483 synthetic fillers plus
  the five plants, each answering all 488 packets with every plant's q1–q4 as
  expected. Any failed run is reported, not rerun away. All transcripts are
  committed. For every run in the passing series, V6 asserts that
  `sha256(prompt_text3())` equals the `prompt_sha256` that the run's
  `run-info.txt` records. On the prototype, the 30-packet bar passed and the full-size bar
  failed in 1 of 3 runs under v2.0. Under v2.1, after one environment abort,
  it passed 3 of 3 (§3). V6 repeats these bars on the bound code, under §0
  item 10's two operating rules.

## 10. Disclosure: what was seen before this draft

- **Aggregates.** The authors have seen prereg 2's Arm 0 and scoring-arm
  aggregates, the export's packet count, 486, and for this draft the per-cell
  exported-packet counts of §8. These counts come from the committed scores
  through `cell_counts.py`, which prints counts only. No record, reference,
  target or packet name was printed or read.
- **No tierer has seen a real packet.** Every rehearsal tierer saw synthetic
  packets, built by `build.py` from Python standard-library documentation, plus
  either synthetic plants, this document's plants, or prereg 2's three plant
  packets.
- **Prereg 2's plant packets, and how they were found.** They are
  three packets of prereg 2's export. Their names are withheld here until
  prereg 2's manifest commit (§7, step 5), because blockspec is public and the
  names would mark the plants in the export before then. They were located
  without the nonce. A program content-matched all 486 packets of prereg 2's
  export against Appendix B's plants and printed only the three matches; no
  other packet's content was printed or read by a person. For this draft,
  `p2/export.py`'s `plant_records` regenerated the three plants, and each
  regenerated packet matched exactly one of those three named packets. No
  other real packet was opened.
- **How the p30 exports were built.** They were built before this work. Their
  construction is reconstructed from what was run:
  - 27 fillers, each content-identical to a synthetic packet of `export-486`.
    `results/prereg3/rehearsals/review-probes/fillers.py` printed `not-in-synthetic 0` for each of the five;
  - the three prereg 2 plant packets, content-identical to the real ones;
  - all 30 under fresh random names, with `packet.json`'s `packet` set to
    match;
  - prereg 2's `PROMPT.md`;
  - the names recorded in `plants-p30-key.json`.
- **What the authors of this draft opened.** The three plant packets; synthetic
  packets; every rehearsal's `tiers.jsonl`, including plant answers and their
  `why`; and the reviewer's probe outputs, which compare runs on synthetic
  packets. No other real packet and no scoring record.
- **The rehearsals.** `results/prereg3/rehearsals/REHEARSALS.md` lists every run, failures included. Its
  summary groups them by plant set and prompt. Every rehearsal used the
  subscription credential, never an API key. There are 71 runs in all:
  - 21 before v2. These are the 7 runs before v1, and v1's 13 `run-p3-*` and one `run-486m`.
  - 36 for v2.0: `p3b` 5, `p3c` 9, `p3d` 9, `p3e` 10 and `p3f` 3. Of these,
    4 failed bar 1 or bar 2 (§3).
  - 14 for v2.1: `p3g` 10, `p3h` 1 and `p3i` 3. Only one did not pass:
    `p3h-1`, an environment abort (§2.8).
- **The plants were revised after seeing answers.** P-A and P-C were rewritten
  after §2.1–§2.2. P-C was revised again after `run-p3-3`. P-D and P-E were
  added after the review of v1. P-B was revised after `run-p3b-5`, and P-E after
  `run-p3c-9`. Each revision restarted the 10-run count, as `BARS.txt`
  recorded before the next series began. No expected answer of prereg 2's three plants
  was changed. The final set was then rehearsed unchanged.
- **The bars were set before the runs they judge.** The 10-consecutive bar for
  v1 came from the brief, before `run-p3-1` started. `drive.sh`, which stops at
  the first mismatch, was written after `run-p3-1`'s result was read and before
  `run-p3-2`. `drive-2-10.log` shows it stopping at `p3-3`. The v2 bars are in
  `results/prereg3/rehearsals/BARS.txt`, written at 2026-10-11T04:09Z, before `run-p3b-1`
  started at 04:09:20Z.
- **The connector.** 10 of the 21 rehearsals before this draft list "claude.ai
  Claude Docs" as a pending MCP server in their init event. None used an MCP
  tool: no transcript names an `mcp__` tool. Prereg 2's frozen run has the
  same exposure. With `--strict-mcp-config`, all 50 v2 rehearsals list no MCP
  server at init, and the prototype's init check passed in each (the
  `MCP at init` column of `results/prereg3/rehearsals/REHEARSALS.md`).
- **Evidence.** `results/prereg3/rehearsals/` holds:
  - the rehearsal tools;
  - the candidate files `cand1.py` to `cand4.py`, with every candidate
    tried, including A2, C1–C3, E2 and B2, chosen or not;
  - all five plant-module versions (`plants/`);
  - the prototype diff, and the prototype's Appendix A stand-in;
  - the diff of `rehearse3.sh` against `rehearse.sh`;
  - the per-cell counts (`cell_counts.out`);
  - the mutant output (`plant_mutants.out`);
  - the driver logs;
  - `BARS.txt`;
  - `review-probes/`: the reviewer's probes that this document cites,
    unchanged except for path scrubbing and the redaction of prereg 2's plant
    names;
  - `v2.0/`, the v2.0 draft, prompt and table, kept so the v2.1 change is
    visible, with the same redaction;
  - the H8 prototype check `h8check.py` and its output.

  Paths are scrubbed: `<REHEARSAL>`, `<SCRATCH>` and `<HOME>` replace local
  directories.
  At step 2 of §7, the run directories, with every transcript, are committed
  under `spike/results/prereg3/rehearsals/` with the same scrubbing.

## 11. Amendment rules

**Frozen when this merges:** §0, §1, §3–§8, §10, this section, and Appendices A
and B. Before step 5 of §7, a frozen section that is wrong may be replaced by a
further pre-registration. After step 5, nothing in this document changes, no
cell or verdict computed under it changes, and no later pre-registration tiers
the records exported at `e46e320` again (§8). §2 and §9's V-list may be
corrected only where they are wrong about a fact. Until step 2 of §7, each
correction is logged below with the original wording. From step 2 on, it is
logged in `LOG.md` instead, with the original wording. Edits made while this is a draft PR are not
amendments.

| date | section | change, with the original wording | reason |
|---|---|---|---|

## Appendix A — the tierer's prompt, verbatim

> You are answering questions about records from an experiment. Work only with
> the files in this directory. Do not open, search for, or fetch any kindspec
> repository, issue or pull request, locally or over the network.
>
> Each packet describes one hypothetical reference — a quote anchor or a name —
> taken against a "before" file and resolved against an "after" file. It gives
> the target the mechanism resolved to and the target an independent oracle
> says is correct. They differ: unless the oracle says the text was deleted,
> they are different places in the after-file, even when their text is the
> same. Read the four questions in the packet.
>
> `PACKETS.txt` names every packet, one per line. Work from that list, not
> from a directory listing, which can be cut short.
>
> For every packet, answer the four questions from the files alone. For
> question 3, a quote that matches more than one place does not by itself show
> that it landed wrong. If you cannot answer question 1 or question 2, set
> `"unplaceable": true` and say why.
>
> Write one JSON object per line to `tiers.jsonl`:
> `{"packet": <name>, "q1": "yes"|"no", "q2": "yes"|"no",
> "q3": "yes"|"no", "q4": "yes"|"no", "unplaceable": true|false,
> "why": <one line>}`.
>
> Write each line as you decide it, and do not revise a line once it is
> written. Stop when every packet in `PACKETS.txt` has a line.

## Appendix B — planted packets, verbatim

The texts below are the plants' before and after files. Blocks are separated by
one blank line, and each file ends with one newline. Their packet fields are
not written by hand: `harness3/prereg3_plants.py` and the harness's
`evaluate()` produce them by running TLLC in its one-leg form and the hardened
quote resolver at `d51ce09`. Block indices count from 0 and include headings.
In every plant, the reference is the quote of the anchored block.

**P-A.** Expected answers: q1 yes, q2 yes, q3 no, q4 no. Expected tier: **A**.

Before:

    ## Ingest service

    Failed jobs are retried three times
    before an alert is raised.

    ## Export service

    Exports are written to the archive bucket nightly.

After:

    ## Defaults

    Failed jobs are retried three times
    before an alert is raised.

    ## Ingest service

    Failed jobs are retried five times
    before an alert is raised.

    ## Export service

    Exports are written to the archive bucket nightly.

- Anchored block: 1.
- TLLC: `SURVIVED`, target 3 (Ingest's edited block).
- Hardened resolver: `EXACT`, target 1 (the block under Defaults).
- REPEAT: decided.

**P-B.** Expected answers: q1 yes, q2 no, q3 no, q4 no. Expected tier:
**B**.

Before:

    ## Project Alpha

    Alpha moves sandbox telemetry into the shared pipeline.

    Status: this proposal was approved by TOC vote on 2026-03-04.

    ## Project Beta

    Beta adds a conformance badge to the landscape.

    Status: this proposal is under review.

After:

    ## Project Alpha

    Alpha was rescoped to cover only audit logs.

    Status: this proposal was approved by TOC vote on 2026-03-04.

    ## Project Beta

    Beta moves sandbox telemetry into the shared pipeline.

    Status: this proposal was approved by TOC vote on 2026-03-04.

- Anchored block: 2 (Alpha's status line).
- TLLC: `SURVIVED`, target 2.
- Hardened resolver: `EXACT_CTX`, target 5 (Beta's status line).
- REPEAT: decided.

**P-C.** Expected answers: q1 no, q2 no, q3 no, q4 no. Expected tier: **C**.

Before:

    ## Maintenance windows

    > **Note:** All times on this page, in every section, are UTC.

    Windows open at 02:00 and close at 04:00 on Sundays.

    Emergency windows may open at any time with one hour's notice.

    ## Release freezes

    > **Note:** All times on this page, in every section, are UTC.

    Freezes begin at 18:00 on the last Friday of each quarter.

After:

    ## Sunday windows

    > **Note:** All times on this page, in every section, are UTC.

    Windows open at 03:00 and close at 05:00 on Sundays.

    ## Maintenance windows

    > **Note:** All times on this page, in every section, are UTC.

    Emergency windows may open at any time with one hour's notice.

    ## Release freezes

    > **Note:** All times on this page, in every section, are UTC.

    Freezes begin at 18:00 on the last Friday of each quarter.

- Anchored block: 1 (the note under Maintenance windows).
- TLLC: `SURVIVED`, target 4 (the note under Maintenance windows).
- Hardened resolver: `EXACT_CTX`, target 1 (the note under Sunday windows).
- REPEAT: decided.

**P-D.** Positive control for q3. Expected answers: q1 yes, q2 yes, q3 yes,
q4 no. Expected tier: **A**.

Before:

    ## Backup service

    Snapshots are kept for seven days
    before they are pruned.

    ## Restore service

    Restores are verified against a checksum manifest.

After:

    ## Backup service

    Snapshots are kept for thirty days
    before they are pruned.

    ## Restore service

    Restores are verified against a checksum manifest.

    ## Change log

    Superseded Backup wording, kept for the change log:

    Snapshots are kept for seven days
    before they are pruned.

- Anchored block: 1.
- TLLC: `SURVIVED`, target 1 (Backup's edited block).
- Hardened resolver: `EXACT`, target 6 (the copy under Change log).
- REPEAT: decided.

**P-E.** Positive control for q4. Expected answers: q1 yes, q2 yes, q3 yes,
q4 yes. Expected tier: **A**.

Before:

    ## Upload limits

    Each project may store up to 50 GB
    of build artifacts at a time.

    ## Download limits

    Downloads are rate-limited to 100 requests per minute.

After:

    ## Upload limits

    Each project may store up to 80 GB, raised from 50 GB in May,
    of build artifacts at a time.

    ## Download limits

    Downloads are rate-limited to 100 requests per minute.

    ## Upload limits

    Each project may store up to 50 GB
    of build artifacts at a time.

- Anchored block: 1.
- TLLC: `SURVIVED`, target 1 (the first Upload limits block, edited).
- Hardened resolver: `EXACT`, target 5 (the stale duplicate's block).
- REPEAT: decided.
