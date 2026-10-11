#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""PRE-REGISTRATION-3.md §9, V6: rehearse the bound tier-run code on
synthetic exports. No real packet is ever used.

    prereg3_v6.py build --source DIR --source-key JSON --size 30|full --out DIR --key-out JSON
    prereg3_v6.py gate  --out DIR
    prereg3_v6.py check --state DIR --export DIR --key JSON --transcript FILE

build: an export written with this harness's own texts and plants
(p3/export3.py): PROMPT.md, PACKETS.txt, QUESTIONS.md, the five plants from
prereg3_plants run through the harness, and synthetic fillers copied from a
synthetic export's packet fields and files (its own plants left out). Every
packet gets a fresh random name. size 30 is 25 random fillers and the five
plants; size full is every filler and the five plants.

gate: a fixture repository shaped like the history after prereg 2's step 5,
dated three days back, holding the pinned tier-model.json bytes, for
`prereg3.py tier-run --unbound --gate-repo`.

check: one rehearsal's result, against the pass bar: every packet answered,
every plant's q1-q4 as §3's table expects and not unplaceable, the prompt
sent hashing to the registered prompt, and the agent's init event listing no
MCP server. Prints P-D's and P-E's q3 and their `why`. Exit 0 on a pass, 1
on a wrong answer or a missed packet, 3 on an authentication abort (an
environment fault, not a judgement on the answers).
"""
import argparse
import datetime
import json
import os
import random
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
SPIKE = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(SPIKE, "harness"))
sys.path.insert(0, HERE)

from p2 import export as X  # noqa: E402
from p2 import mech as Mx  # noqa: E402
from p3 import binding as BD  # noqa: E402
from p3 import export3 as X3  # noqa: E402
from p3 import gates as G  # noqa: E402
from p3 import plants as PL  # noqa: E402
from p3 import tierrun3 as T3  # noqa: E402


def fresh_names(n):
    out = set()
    while len(out) < n:
        out.add(os.urandom(8).hex())
    return sorted(out)


def cmd_build(a):
    if os.path.lexists(a.out) or os.path.lexists(a.key_out):
        sys.exit(f"refusing: {a.out} or {a.key_out} exists")
    Mx.load(a.d8_dir)
    skey = json.load(open(a.source_key))["packets"]
    pool = sorted(n for n, v in skey.items() if not v.get("expected"))
    plants = X3.plant_records3()
    rng = random.SystemRandom()
    fillers = rng.sample(pool, 30 - len(plants)) if a.size == "30" else list(pool)
    items = []
    for n in fillers:
        d = os.path.join(a.source, "packets", n)
        pj = json.load(open(os.path.join(d, "packet.json"), encoding="utf-8"))
        fields = {k: pj[k] for k in ("reference_kind", "reference", "mechanism_target", "oracle_target")}
        files = {role: open(os.path.join(d, fn), encoding="utf-8", newline="").read()
                 for role, fn in pj["files"].items()}
        items.append(({"filler": n, "plant": None}, fields, files))
    for p, (r, texts) in plants.items():
        fields, files = X.packet_fields(r, texts)
        items.append(({"filler": None, "plant": p}, fields, files))
    rng.shuffle(items)
    names = fresh_names(len(items))
    os.makedirs(os.path.join(a.out, "packets"))
    q = X3.questions_text3()
    key = {}
    for name, (meta, fields, files) in zip(names, items):
        X.write_packet(a.out, name, fields, files, q)
        key[name] = meta
    with open(os.path.join(a.out, "PROMPT.md"), "w", encoding="utf-8") as f:
        f.write(X3.prompt_text3())
    with open(os.path.join(a.out, X3.MANIFEST), "w", encoding="utf-8") as f:
        f.write(X3.manifest_text(names))
    bad = X3.validate3(a.out)
    if bad:
        sys.exit("validator: " + "; ".join(bad[:5]))
    json.dump({"size": a.size, "packets": key}, open(a.key_out, "w"), indent=1, sort_keys=True)
    print(f"{a.out}: {len(names)} packets ({len(plants)} plants), validate3 clean")
    return 0


def cmd_gate(a):
    if os.path.lexists(a.out):
        sys.exit(f"refusing: {a.out} exists")
    blob = subprocess.run(["git", "-C", SPIKE, "cat-file", "blob", G.TIER_MODEL_BLOB],
                          capture_output=True).stdout
    if not blob:
        sys.exit("cannot read the pinned tier-model.json blob")
    env = dict(BD.git_env())
    r2 = os.path.join(a.out, "spike", "results", "prereg2")
    os.makedirs(r2)
    d = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=3)).strftime("%Y-%m-%dT12:00:00Z")
    env.update(GIT_AUTHOR_DATE=d, GIT_COMMITTER_DATE=d, GIT_AUTHOR_NAME="v6", GIT_COMMITTER_NAME="v6",
               GIT_AUTHOR_EMAIL="v6@example.invalid", GIT_COMMITTER_EMAIL="v6@example.invalid")

    def git(*x):
        subprocess.run(["git", "-C", a.out, *x], check=True, capture_output=True, env=env)
    git("init", "-q", "-b", "main")
    open(os.path.join(r2, "tier-model.json"), "wb").write(blob)
    open(os.path.join(r2, "tiers.jsonl"), "w").write('{"packet": "fixture"}\n')
    open(os.path.join(r2, "tier-runs.txt"), "w").write(json.dumps({"event": "started", "n": 1, "at": d}) + "\n")
    git("add", "-A")
    git("commit", "-q", "-m", "fixture: prereg 2 tiers")
    open(os.path.join(r2, "verdict.json"), "w").write(json.dumps(
        {"bound": True, "binding": {"validation_commit": BD.PREREG2_VALIDATION}, "fixture": True}))
    git("add", "-A")
    git("commit", "-q", "-m", "fixture: prereg 2 verdict")
    vc = G.verdict_gate(os.path.join(a.out, "spike"))
    print(f"gate fixture {a.out}: verdict commit {vc[:12]} dated {d}; model {G.tier_model(os.path.join(a.out, 'spike'))}")
    return 0


def cmd_check(a):
    key = json.load(open(a.key))["packets"]
    names = set(os.listdir(os.path.join(a.export, "packets")))
    n, path = T3.binding_run(a.state)
    ans = {}
    for ln in open(path, encoding="utf-8") if path and os.path.exists(path) else []:
        if ln.strip():
            try:
                o = json.loads(ln)
                ans.setdefault(o.get("packet"), o)
            except ValueError:
                pass
    tr = open(a.transcript, encoding="utf-8", errors="replace").read()
    auth = any(T3.is_auth_error(ln) for ln in tr.splitlines())
    prompt_ok = f"Appendix A as sent, sha256 {X3.PROMPT_SHA256}" in tr
    init_ok = "init check: tools" in tr and "INIT CHECK FAILED" not in tr
    answered = len(set(ans) & names)
    print(f"binding run: {n}; answered {answered} of {len(names)}; prompt sha registered: {prompt_ok}; "
          f"init check passed (no MCP server): {init_ok}; auth error: {auth}")
    ok = answered == len(names) and prompt_ok and init_ok
    for name, meta in sorted(key.items(), key=lambda x: str(x[1]["plant"])):
        p = meta["plant"]
        if not p:
            continue
        e, o = PL.PLANT_EXPECT3[p], ans.get(name)
        if o is None:
            print(f"  {p}: UNTIERED")
            ok = False
            continue
        got = " ".join(o.get(q, "?") for q in ("q1", "q2", "q3", "q4"))
        right = all(o.get(q) == e[q] for q in ("q1", "q2", "q3", "q4")) and o.get("unplaceable") is False
        ok &= right
        print(f"  {p}: {got} {'OK' if right else 'MISMATCH'}"
              + (f" | q3 why: {o.get('why')}" if p in ("P-D", "P-E") else ""))
    print("V6 RUN:", "PASS" if ok else ("AUTH ABORT" if auth else "FAIL"))
    return 0 if ok else (3 if auth else 1)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("build")
    p.add_argument("--d8-dir", required=True)
    p.add_argument("--source", required=True)
    p.add_argument("--source-key", required=True)
    p.add_argument("--size", choices=("30", "full"), required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--key-out", required=True)
    p = sub.add_parser("gate")
    p.add_argument("--out", required=True)
    p = sub.add_parser("check")
    p.add_argument("--state", required=True)
    p.add_argument("--export", required=True)
    p.add_argument("--key", required=True)
    p.add_argument("--transcript", required=True)
    a = ap.parse_args()
    return {"build": cmd_build, "gate": cmd_gate, "check": cmd_check}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
