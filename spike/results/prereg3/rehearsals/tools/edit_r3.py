"""Round-3 text fixes. Appendix A is not touched.

usage: python3 -I -S -B edit_r3.py <draft>
"""
import sys

f = sys.argv[1]
s = open(f, encoding="utf-8").read()
appa0 = s[s.index("## Appendix A"):s.index("## Appendix B")]


def rep(a, b):
    global s
    assert s.count(a) == 1, ("count", s.count(a), a[:90])
    s = s.replace(a, b)


# 1. Item 10 -> approval line, prereg 2's rule kept
a0 = s.index("10. **OPEN: a run that dies on an authentication error")
a1 = s.index("    to 40 minutes, longer than the 17 minutes seen before.") + len(
    "    to 40 minutes, longer than the 17 minutes seen before.")
s = s[:a0] + """10. **A run that dies on an authentication error binds, as prereg 2's run
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
      exactly the forking path the final-tiering rule (item 2) closes.""" + s[a1:]

# §6 credential bullet: no auth exception
rep("""  after it exits. If the transcript ends on an authentication error (HTTP 401
  or 403), the ledger records the run as `auth_aborted`. What may follow is
  §0 item 10.""",
"""  after it exits. If the transcript ends on an authentication error (HTTP 401
  or 403), the ledger records the run as `auth_aborted`. This is a label for
  the record and changes nothing. The run binds under the run rule like any
  other run that wrote a line (§0 item 10).""")

# 2. §6 init bullet: remove stray sentence, put the cap and the why in order
rep("""  agents. A run that fails the check is recorded as `init_failed`. Its work
  directory is kept and committed. It never binds, even if the agent wrote a
  line before it was stopped, and one rerun is allowed. That race is real: the
  prototype, given a stub whose first event was not init, stopped it, but the
  ledger still showed one line written. That run then has zero lines and counts under the rerun rule. Why:
  without the flag, 10 of the 21 rehearsals before this draft listed a
  claude.ai account connector, "claude.ai Claude Docs", as pending. No run used
  it (§10). Prereg 2's bound run has the same exposure, and this document does
  not change prereg 2.""",
"""  agents. A run that fails the check is recorded as `init_failed`. Its work
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
  exposure, and this document does not change prereg 2.""")

# 3. M-1 wording
rep("""  **The committed order check** is what holds. `aggregate` runs it from
  committed records only, and refuses unless both hold:""",
"""  **The committed order check** catches a binding prereg 2 tier-run that ran
  out of order. It does not catch an earlier tier-run that was thrown away
  and left no record. `aggregate` runs it from committed records only, and
  refuses unless both hold:""")

# 4. §9 h8check block formatting, with the new cases
rep("""reviewer's FOUND fixture and changes only P-D's q3 to "no", and
`h8check.py` then prints:

    all plants right: FOUND | overall FOUND | void []
    P-D q3=no: NO VERDICT | tiering void: P-D: q3=no, expected yes | overall INCONCLUSIVE
    V4 mutant (void not passed to cell): FOUND | overall FOUND -> KILLED by the case above
    four-plant manifest: refused: the manifest's plants are not prereg 3's Appendix B
    H8 CHECK: PASS The unchanged bound validator refuses
a manifest export. On a rehearsal export it reported
`export root holds files outside the allow-list: ['PACKETS.txt']`.""",
"""reviewer's FOUND fixture. `h8check.py` writes the plants' right answers out
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

The reviewer's six-mutant sweep over `aggregate3.py` (`r3h8/sweep.py`) hashes
the file before and after each mutation. All six go RED
(`evidence/h8sweep.out`):
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
['PACKETS.txt']`.""")

# 5. V6 no longer waits
rep("""  it passed 3 of 3 (§3). V6 repeats these bars on the bound code, and it needs
  §0 item 10 settled first.""",
"""  it passed 3 of 3 (§3). V6 repeats these bars on the bound code, under §0
  item 10's two operating rules.""")
rep("""  - **Credential and auth abort.** A stub whose transcript ends on a 401 is
    recorded as `auth_aborted`, with the credential file's sha256 and mtime
    before and after.""",
"""  - **Credential and auth abort.** A stub whose transcript ends on a 401 is
    recorded as `auth_aborted`, with the credential file's sha256 and mtime
    before and after. If it wrote a line, it binds, and no rerun is allowed.
  - **Run cap.** After a zero-line first run and an `init_failed` rerun, a
    third `tier-run` is refused. The same holds in the other order.""")

assert s[s.index("## Appendix A"):s.index("## Appendix B")] == appa0, "Appendix A changed"
open(f, "w", encoding="utf-8").write(s)
print("ok")
