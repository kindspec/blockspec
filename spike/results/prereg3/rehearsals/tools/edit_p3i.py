"""Write the p3i results into the draft. Appendix A is not touched.

usage: python3 -I -S -B edit_p3i.py <draft>
"""
import sys

f = sys.argv[1]
s = open(f, encoding="utf-8").read()
appa0 = s[s.index("## Appendix A"):s.index("## Appendix B")]


def rep(a, b):
    global s
    assert s.count(a) == 1, ("count", s.count(a), a[:90])
    s = s.replace(a, b)


a0 = s.index("10. **OPEN: a run that dies on an authentication error")
a1 = s.index("   until the owner picks one.") + len("   until the owner picks one.")
s = s[:a0] + """9. **Appendix A adds one sentence for q3 (§2.7, §4):** "For question 3, a
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
10. **OPEN: a run that dies on an authentication error (§2.8).** Prereg 2's
    rule, which this document keeps, lets the first run that writes any line
    bind.
    - **Recommended:** the same rule, with one exception. A run recorded as
      `auth_aborted` (§6) is kept and committed, and nobody reads its answer
      lines. One rerun is allowed, and the rerun binds. The exception needs a
      401 or 403 at the end of the committed transcript, and it is used once.
    - *Alternative:* keep prereg 2's rule unchanged. A run that dies this way
      then binds, partial.

    Either way, two operating rules apply to this document's run and to
    prereg 2's frozen run:
    - Start a bound run just after the credential file has been rewritten.
    - Keep every other Claude session off the account during the run.

    The refresh interval has not been measured yet. `cred-mtime.log` records
    one rewrite, at 08:52:20Z. The file then stayed unchanged until at least
    10:20:52Z, the last check after `run-p3i-3`. So the interval is at least
    1 h 28 min. A full-size run took 960 to 2,401 seconds (`p3i`). That is up
    to 40 minutes, longer than the 17 minutes seen before.""" + s[a1:]

rep("""  - **Bar 2′, 488 packets: FAILED at `run-p3h-1`, by an environment fault.**
    The tierer wrote 280 lines. Then the API answered 401 "OAuth token
    revoked", and the agent exited with status 1. P-A was untiered, so under
    the void rule the run voids. P-B, P-C, P-D and P-E were tiered, and all
    four were right.
  - The stop rule held. `p3h-2` and `p3h-3` were not run.
- **Rates, never pooled across sizes.** See the table in §0 item 9. At 30
  packets, 0 failures in 10 runs under each prompt, 95% upper bound 25.9%. At
  full size under v2.0, 1 failure in 3, bound 86.5%. At full size under v2.1,
  no completed run.""",
"""  - **`run-p3h-1`, 488 packets: environment abort.** The tierer wrote 280
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
  - at full size under v2.1, 0 failures in 3 completed runs, bound 63.2%.""")

rep("""  failed in 1 of 3 runs under v2.0. Under v2.1 it stopped at its first run on
  an environment fault (§3). So V6 on the bound code waits until §0 items 9
  and 10 are settled and the prototype passes both bars.""",
"""  failed in 1 of 3 runs under v2.0. Under v2.1, after one environment abort,
  it passed 3 of 3 (§3). V6 repeats these bars on the bound code, and it needs
  §0 item 10 settled first.""")

rep("""  subscription credential, never an API key. There are 68 runs in all:""",
"""  subscription credential, never an API key. There are 71 runs in all:""")
rep("""  - 11 for v2.1: `p3g` 10 and `p3h` 1. Of these, 1 failed, on an
    environment fault (§2.8).""",
"""  - 14 for v2.1: `p3g` 10, `p3h` 1 and `p3i` 3. Only one did not pass:
    `p3h-1`, an environment abort (§2.8).""")
rep("""all 47 v2 rehearsals list no MCP""", """all 50 v2 rehearsals list no MCP""")

assert s[s.index("## Appendix A"):s.index("## Appendix B")] == appa0, "Appendix A changed"
open(f, "w", encoding="utf-8").write(s)
print("ok")
