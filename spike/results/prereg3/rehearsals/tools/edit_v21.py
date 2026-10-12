"""Write the v2.1 results into the draft. Appendix A is not touched.

usage: python3 -I -S -B edit_v21.py <draft>
"""
import sys

f = sys.argv[1]
s = open(f, encoding="utf-8").read()
appa0 = s[s.index("## Appendix A"):s.index("## Appendix B")]


def rep(a, b):
    global s
    assert s.count(a) == 1, ("count", s.count(a), a[:90])
    s = s.replace(a, b)


rep("""9. **OPEN: how q3 reads duplicated text (§2.7).** The full-size bar failed
   once in three runs (§3). The draft does not yet settle this, and it does
   not merge until it does. Two options:
   - **(a) Recommended.** Add one sentence to Appendix A: "For question 3, a
     quote that matches more than one place does not by itself show that it
     landed wrong." This reads F7 as prereg 2 §2 states it. Then rehearse
     again to both bars, which takes about 2.5 hours.
   - **(b)** Keep the prompt, and accept a measured void risk of 1 in 13
     runs, with a 95% upper bound of 31.6%.""",
"""9. **OPEN: how q3 reads duplicated text (§2.7), and whether to keep the
   sentence added for it.** v2.1 added to Appendix A: "For question 3, a
   quote that matches more than one place does not by itself show that it
   landed wrong." Its bars were set in advance (§3).
   - The 30-packet bar passed 10 of 10.
   - The full-size bar failed at its first run, `run-p3h-1`. That run stopped
     after 280 of 488 packets on an authentication error (§2.8), not on a wrong
     answer. P-A was among the packets left untiered. The four plants that were
     tiered were right. The pre-set stop rule then ended the series, so v2.1
     has no completed full-size run.

   The measurements so far, with each size counted on its own:

   | prompt | packets per run | runs | failed | 95% upper bound on the per-run failure rate |
   |---|---|---|---|---|
   | v2.0 | 30 | 10 | 0 | 25.9% |
   | v2.0 | 488 | 3 | 1 (`p3f-2`, P-B and P-C q3 "yes") | 86.5% |
   | v2.1 | 30 | 10 | 0 | 25.9% |
   | v2.1 | 488 | 1 | 1 (`p3h-1`, environment fault) | not measured: no completed run |

   Bounds are exact one-sided 95% (Clopper–Pearson). The choices are:
   - **(b) Recommended for now:** keep the v2.0 prompt, without the sentence,
     and accept the measured full-size void risk: 1 failure in 3 runs, with a
     95% upper bound of 86.5%.
   - **(a′):** keep the sentence, and first rerun the full-size bar once §2.8
     is fixed. The sentence has shown no harm so far. P-D and P-E answered q3
     "yes" in all 11 v2.1 runs, and every P-E rationale rested on the 50 GB
     against 80 GB content (`pdpe_q3.py`, in `evidence/`). But the sentence
     has no completed full-size evidence for it.

   This item does not close until the owner picks one.""")

rep("""- **What the numbers bound.** The final plants and prompt ran 13 times, with
  one failure. The exact one-sided 95% upper bound on the per-run failure rate
  is 31.6% for 1 failure in 13 (Clopper–Pearson). It would be 25.9% for the 10
  passing 30-packet runs alone. So a void bound run is a live possibility, not
  a remote one. §2.7 says what failed, and §0 item 9 asks the owner how to
  respond.""",
"""- **v2.1 (§0 item 9's sentence added). Bars set before the first run, in
  `BARS.txt` at 07:49:30Z.** Its sha256 is recorded outside the file in
  `bars-sha.log`, at 08:10Z during the 30-packet series, and again at 08:36Z,
  14 seconds after `run-p3h-1` began.
  - **Bar 1′, 30 packets: PASSED.** `run-p3g-1` to `run-p3g-10`, 10 of 10,
    30 of 30 packets in each.
    - P-D answered q3 "yes" in all 10, each time citing the "Superseded" label.
    - P-E answered q3 "yes" in all 10, each time citing the 50 GB copy against
      the live "80 GB, raised from 50 GB" text. None cited only the duplicate
      match.
  - **Bar 2′, 488 packets: FAILED at `run-p3h-1`, by an environment fault.**
    The tierer wrote 280 lines. Then the API answered 401 "OAuth token
    revoked", and the agent exited with status 1. P-A was untiered, so under
    the void rule the run voids. P-B, P-C, P-D and P-E were tiered, and all
    four were right.
  - The stop rule held. `p3h-2` and `p3h-3` were not run.
- **Rates, never pooled across sizes.** See the table in §0 item 9. At 30
  packets, 0 failures in 10 runs under each prompt, 95% upper bound 25.9%. At
  full size under v2.0, 1 failure in 3, bound 86.5%. At full size under v2.1,
  no completed run.""")

rep("""Source: `REHEARSALS.md`, whose summary groups runs by plant set and prompt.""",
"""Source: `REHEARSALS.md`. Its summary groups runs by plant set, prompt and
packets per run, so 30-packet and full-size runs are never pooled.""")

rep("""So one tiering run is a noisy instrument.""",
"""**2.8 A tier-run can die on the host's credential.** `run-p3h-1` stopped at
08:52Z on `401 … OAuth token revoked`. The host's
`~/.claude/.credentials.json` had been rewritten at that same minute (its
mtime). The sandbox binds that one file read-only, so the tierer keeps a token
that a refresh elsewhere on the host has revoked. The cause looks like token
rotation by another session on the same account, but that is inferred, not
reproduced. Prereg 2's bound tier-run has the same exposure. Under the run
rules, a run that dies this way after writing lines **binds**: it is not a
zero-line run, so no rerun is allowed, its untiered real packets are NO
VERDICT, and an untiered plant voids it. §6 and §0 item 10.

So one tiering run is a noisy instrument.""")

rep("""- **No connectors.** The agent argv adds `--strict-mcp-config`.""",
"""- **The credential (§2.8).** For the length of a tier-run, nothing else on
  the host may use the account whose credential the sandbox binds. The harness
  logs the credential file's sha256 and mtime before the agent starts and
  after it exits. If the transcript ends on an authentication error (HTTP 401
  or 403), the ledger records the run as `auth_aborted`. What may follow is
  §0 item 10.
- **No connectors.** The agent argv adds `--strict-mcp-config`.""")

rep("""  if the stream ends with no init event. The check also applies to stub
  agents.""",
"""  if the stream ends with no init event. The check also applies to stub
  agents. A run that fails the check is recorded as `init_failed`. Its work
  directory is kept and committed. It never binds, even if the agent wrote a
  line before it was stopped, and one rerun is allowed. That race is real: the
  prototype, given a stub whose first event was not init, stopped it, but the
  ledger still showed one line written.""")

rep("""8. **Harness changes land in new files only (§9).** Nothing under
   `spike/harness/`, `PRE-REGISTRATION-2.md` or `ORACLE.md` changes.""",
"""8. **Harness changes land in new files only (§9).** Nothing under
   `spike/harness/`, `PRE-REGISTRATION-2.md` or `ORACLE.md` changes.
10. **OPEN: a run that dies on an authentication error (§2.8).** Prereg 2's
    rule, which this document keeps, lets the first run that writes any line
    bind.
    - **Recommended:** the same rule, with one exception. A run recorded as
      `auth_aborted` (§6) is kept and committed, but nobody reads its lines.
      One rerun is allowed, and the rerun binds. The exception is narrow: it
      needs the 401 or 403 in the committed transcript, and it is used once.
    - *Alternative:* keep prereg 2's rule unchanged. A run that dies this way
      then binds, partial.

    Either way, the operator keeps every other session off the account
    during the run.""")

rep("""  - **Init check.** Each of these stubs is stopped, and the run records zero
    lines:""",
"""  - **Credential and auth abort.** A stub whose transcript ends on a 401 is
    recorded as `auth_aborted`, with the credential file's sha256 and mtime
    before and after.
  - **Init check.** Each of these stubs is stopped, and its run is recorded
    as `init_failed` and does not bind, even if the stub wrote a line first:""")

rep("""  failed in 1 of 3 runs (§3). So V6 on the bound code waits until §0 item 9 is
  settled and the prototype passes both bars.""",
"""  failed in 1 of 3 runs under v2.0. Under v2.1 it stopped at its first run on
  an environment fault (§3). So V6 on the bound code waits until §0 items 9
  and 10 are settled and the prototype passes both bars.""")

rep("""  subscription credential, never an API key. There are 57 runs in all:""",
"""  subscription credential, never an API key. There are 68 runs in all:""")
rep("""  - 36 for v2: `p3b` 5, `p3c` 9, `p3d` 9, `p3e` 10 and `p3f` 3. Of these, 4
    failed bar 1 or bar 2 (§3).""",
"""  - 36 for v2.0: `p3b` 5, `p3c` 9, `p3d` 9, `p3e` 10 and `p3f` 3. Of these,
    4 failed bar 1 or bar 2 (§3).
  - 11 for v2.1: `p3g` 10 and `p3h` 1. Of these, 1 failed, on an
    environment fault (§2.8).""")
rep("""  same exposure. With `--strict-mcp-config`, all 36 v2 rehearsals list no MCP""",
"""  same exposure. With `--strict-mcp-config`, all 47 v2 rehearsals list no MCP""")

assert s[s.index("## Appendix A"):s.index("## Appendix B")] == appa0, "Appendix A changed"
open(f, "w", encoding="utf-8").write(s)
print("ok")
