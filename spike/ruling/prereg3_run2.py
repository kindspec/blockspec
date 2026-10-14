#!/usr/bin/env -S python3 -I -S -B
# SPDX-License-Identifier: MIT
"""Prereg 3's tier-run 2, under the owner's ruling of 2026-10-14 (LOG §34).

Run 1 stopped after 193 lines when the host lost its network (LOG §32). Under
§6 a run that wrote a line binds and allows no rerun. The owner ruled that
the tier-run is run once more, as run 2, and that run 2 binds whatever it
says. Run 1, its verdict (results/prereg3/verdict.json) and everything else
committed stay as they are.

This script imports harness3/prereg3.py unchanged, in this process, and
replaces only:

- p3.tierrun3.rerun_allowed: run 2 is allowed exactly when the ledger holds
  one started run, run 1, and no run 2. Anything else is refused, so there is
  never a run 3;
- p3.tierrun3.binding_run: run 2 once it has started, otherwise the frozen
  rule (which gives run 1);
- the bound output path of `aggregate`, results/prereg3/run2/verdict.json, so
  results/prereg3/verdict.json is never overwritten. This script's aggregate
  refuses until run 2 has started.

Every other check runs as frozen: the binding to prereg 3's validation
commit, the gate, the window, the init check, the credential log and the
ledger. It accepts three commands:

    python3 -I -S -B ruling/prereg3_run2.py tier-run
    python3 -I -S -B ruling/prereg3_run2.py repro     --d8-dir D8 --arm ARM --id RECORD --work-dir W
    python3 -I -S -B ruling/prereg3_run2.py aggregate --d8-dir D8 --manifest PATH --manifest2 PATH2
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SPIKE = os.path.dirname(HERE)
sys.dont_write_bytecode = True

COMMANDS = ("tier-run", "repro", "aggregate")
RUN2_DIR = os.path.join(SPIKE, "results", "prereg3", "run2")
RUN2_VERDICT = os.path.join(RUN2_DIR, "verdict.json")


def load_harness():
    spec = importlib.util.spec_from_file_location("prereg3", os.path.join(SPIKE, "harness3", "prereg3.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["prereg3"] = mod
    spec.loader.exec_module(mod)
    return mod


def install(H):
    """Replace the two run rules and the aggregate output path. Returns the
    frozen binding_run, for the self-test."""
    T3 = H.T3
    frozen_binding_run = T3.binding_run

    def started(state_dir):
        return [e["n"] for e in T3.read_ledger(state_dir) if e.get("event") == "started"]

    def rerun_allowed(state_dir):
        s = started(state_dir)
        if s == [1]:
            return 2, "RERUN under the owner's ruling of 2026-10-14 (LOG §34): run 2 binds whatever it says"
        raise T3.TierRefused(f"the ruling allows run 2 only after run 1 alone; the ledger has started runs {s}")

    def binding_run(state_dir):
        if 2 in started(state_dir):
            return 2, T3.work_tiers(state_dir, 2)
        return frozen_binding_run(state_dir)

    T3.rerun_allowed = rerun_allowed
    T3.binding_run = binding_run
    H.FIXED["out:aggregate"] = RUN2_VERDICT
    return frozen_binding_run


def main(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    if not argv or argv[0] not in COMMANDS:
        print(f"usage: prereg3_run2.py {{{','.join(COMMANDS)}}} ...", file=sys.stderr)
        return 64
    if argv[0] == "aggregate" and os.path.exists(RUN2_VERDICT):
        print(f"refusing: {RUN2_VERDICT} exists", file=sys.stderr)
        return 2
    H = load_harness()
    install(H)
    if argv[0] == "aggregate":
        if 2 not in [e["n"] for e in H.T3.read_ledger(H.RESULTS) if e.get("event") == "started"]:
            print("refusing: run 2 has not started; this script's aggregate is run 2's", file=sys.stderr)
            return 2
        os.makedirs(RUN2_DIR, exist_ok=True)
    return H.main(argv)


if __name__ == "__main__":
    sys.exit(main())
