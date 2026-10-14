#!/usr/bin/env -S python3 -I -S -B
# SPDX-License-Identifier: MIT
"""The reproduction write-up for prereg 3's run-2 FOUND (PRE-REGISTRATION-2.md
§8: "The write-up is the reproduction"), generated from committed records only.

For every qualifying packet, as ruling/qualifying_run2.py derives them, it
writes the corpus and pin, the commits and path, the exact commands that
produce each file, and the oracle's decided class with the hardened
resolver's result. It writes no file content: every text is left to the
commands. Indices and classes come from the committed scoring records; the
record's quoted reference and target texts are not copied.

usage: python3 -I -S -B ruling/reproduction_run2.py <spike dir> <sealed manifest> <out.md>

    e.g. ruling/reproduction_run2.py . results/prereg3/sealed-manifest.json results/prereg3/run2/reproduction.md
"""
import collections
import glob
import gzip
import json
import os
import shlex
import sys

spike, manifest, out = sys.argv[1:4]
sys.path[:0] = [os.path.join(spike, "harness3"), os.path.join(spike, "harness")]
import prose_merge as PM  # noqa: E402
from p2 import aggregate as AG  # noqa: E402
from p2 import corpus as K  # noqa: E402
from p2 import export as X  # noqa: E402
from p2 import tiers as T  # noqa: E402
from p3 import aggregate3 as A3  # noqa: E402
from p3 import binding as BD  # noqa: E402
from p3 import plants as PL  # noqa: E402

# PRE-REGISTRATION-2.md §6.2's table.
SOURCE = {"rust-book": "rust-lang/book", "obsidian-help": "obsidianmd/obsidian-help",
          "cmspec": "commonmark/commonmark-spec", "k8s-en": "kubernetes/website",
          "k8s-l10n": "kubernetes/website", "cncf-toc": "cncf/toc", "site-policy": "github/site-policy"}

R2 = os.path.join(spike, "results", "prereg2")
R3 = os.path.join(spike, "results", "prereg3")
m = PL.load_manifest(manifest, json.load(open(os.path.join(R3, "VALIDATION")))["manifest_sha256"])
verdict = json.load(open(os.path.join(R3, "run2", "verdict.json")))
arm0 = {}
for p in sorted(glob.glob(os.path.join(R2, "arm0", "*.json"))):
    o = json.load(open(p))
    arm0[o["arm"]] = o
scores = {}
for st in sorted(glob.glob(os.path.join(R2, "score", "*", "status.json"))):
    d = os.path.dirname(st)
    s = json.load(open(st))
    if "no_verdict" in s:
        continue
    inst = {}
    for line in open(os.path.join(d, "instances.jsonl"), encoding="utf-8"):
        o = json.loads(line)
        o.pop("texts", None)
        inst[(o["arm"], o["id"])] = o
    recs = [json.loads(line) for line in gzip.open(os.path.join(d, "units.jsonl.gz"), "rt", encoding="utf-8")]
    scores[s["arm"]] = {"modes": s["modes"], "instances": inst, "records": recs}
tiers, problems = T.read_tiers(os.path.join(R3, "tier-work-2", "tiers.jsonl"))
assert not problems
load = lambda d: [json.load(open(p)) for p in sorted(glob.glob(os.path.join(d, "*.json")))]  # noqa: E731
repro = A3.accept_repros(load(os.path.join(R2, "repro")), load(os.path.join(R3, "repro")),
                         BD.derive_validation(spike, BD.PREREG3)[0])
recs_all, inst_all = [], {}
for sc in scores.values():
    recs_all += sc["records"]
    inst_all.update(sc["instances"])
reps = X.select_packets(recs_all, inst_all)

# The qualifying packets, exactly as ruling/qualifying_run2.py derives them.
qual = collections.defaultdict(list)
for arm in AG.K.ARM_ORDER:
    a0, sc = arm0.get(arm, {}), scores.get(arm)
    if not a0.get("passes_bar") or sc is None:
        continue
    inst = sc["instances"]
    for mode in AG.MODES:
        if mode not in sc["modes"]:
            continue
        for mech in AG.MECHS:
            mine = [r for r in sc["records"] if r["mode"] == mode and r["mech"] == mech and r["arm"] == arm]
            recs = [r for r in mine if AG.in_cell(inst[(arm, r["instance"])])]
            keys = {X.packet_key(r) for r in recs if X.eligible(r, inst[(arm, r["instance"])])}
            units = set()
            for key in keys:
                rep = reps[key]
                name = X.packet_name(m["nonce"], key)
                ans = tiers.get(name)
                if ans is None or T.tier_of(ans) == "UNPLACEABLE" or ans["q4"] != "no":
                    continue
                if not AG.reproduced(repro[rep["id"]]):
                    continue
                if ans["q3"] == "no" and T.tier_of(ans) in ("A", "B"):
                    qual[(name, key)].append(f"{arm} {mode} {mech}")
                    units.add(X.unit_key(rep))
            assert len(units) == verdict["cells"][f"{arm}|{mode}|{mech}"].get("qualifying_distinct", 0)

q = shlex.quote


def show(commit, path):
    return f'git -C "$CLONE" show {q(commit + ":" + path)}'


def file_cmds(i):
    """[(packet file, command)] for one instance, in the packet's roles."""
    meta, path = i["meta"], i["path"]
    if i["mode"] == "E":
        return [("before.md", show(meta["parent"], path)), ("after.md", show(meta["commit"], path))]
    if i["mode"].startswith("S"):
        return [("before.md", show(meta["before_commit"], path)), ("after.md", show(meta["after_commit"], path))]
    return [("base.md", show(meta["base"], path)), ("leg-a.md", show(meta["legA"], path)),
            ("leg-c.md", show(meta["legC"], path)),
            ("after.md", f"stock_merge {q(meta['base'])} {q(meta['legA'])} {q(meta['legC'])} {q(path)}")]


STOCK_MERGE = r"""stock_merge() {  # base legA legC path: prints the merged file
  local d f; d=$(mktemp -d); mkdir "$d/.nohooks"; f="$d/$4"; mkdir -p "$(dirname "$f")"
  local G=(git -C "$d" -c core.attributesFile=/dev/null -c commit.gpgsign=false -c core.autocrlf=false
           -c merge.conflictStyle=merge -c core.hooksPath="$d/.nohooks")
  export GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null LC_ALL=C \
         GIT_AUTHOR_NAME=h GIT_AUTHOR_EMAIL=h@invalid GIT_COMMITTER_NAME=h GIT_COMMITTER_EMAIL=h@invalid \
         GIT_AUTHOR_DATE=2000-01-01T00:00:00Z GIT_COMMITTER_DATE=2000-01-01T00:00:00Z
  "${G[@]}" init -q -b main
  git -C "$CLONE" show "$1:$4" | norm > "$f"; "${G[@]}" add -A; "${G[@]}" commit -q -m base
  "${G[@]}" checkout -q -b legA
  git -C "$CLONE" show "$2:$4" | norm > "$f"; "${G[@]}" add -A; "${G[@]}" commit -q --allow-empty -m a
  "${G[@]}" checkout -q -b legC main
  git -C "$CLONE" show "$3:$4" | norm > "$f"; "${G[@]}" add -A; "${G[@]}" commit -q --allow-empty -m c
  "${G[@]}" checkout -q legA
  "${G[@]}" merge --no-edit legC >/dev/null && cat "$f"
}"""
NORM = r"""norm() {  # UTF-8 with universal newlines, as the harness reads every blob
  python3 -I -S -c 'import sys; t = sys.stdin.buffer.read().decode("utf-8"); sys.stdout.buffer.write(t.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8"))'
}"""

lines = []
w = lines.append
w("# Prereg 3, run 2: the reproduction of each qualifying packet\n")
w("PRE-REGISTRATION-2.md §8, for FOUND: \"The write-up is the reproduction.\" This file is that "
  "reproduction for prereg 3's run-2 verdict (`results/prereg3/run2/verdict.json`, LOG §35). "
  "It is generated by `ruling/reproduction_run2.py` from committed records only, and holds no "
  "file content: each file of each packet is what its command prints.\n")
w(f"Qualifying packets: {len(qual)}. Their answers are in `qualifying.md`.\n")
w("## Setup\n")
w("Clone the arm's source and check out its pin (PRE-REGISTRATION-2.md §6.2), or fetch the "
  "archived bundle whose sha256 `harness/p2/bundles.json` records. Set `CLONE` to that clone.\n")
w("| arm | source | pin | bundle sha256 |\n|---|---|---|---|")
bun = K.bundles()
for arm in K.ARM_ORDER:
    spec = K.ARMS[arm]
    w(f"| {arm} | `https://github.com/{SOURCE[arm]}` | `{spec['pin']}` | `{bun[spec['bundle']]['sha256']}` |")
w("")
w("The harness reads every blob as UTF-8 with universal newlines (`p2/arms.py` `decode_text`), and "
  "the packet files hold that text. So each command's output is piped through `norm` below. For M, "
  "the after-file is the stock-git merge of the two legs on the merge base, as `prose_merge.stock_merge` "
  "runs it (PRE-REGISTRATION-2.md §3(1)): a fresh repository, no hooks, no attributes, "
  f"`{PM.MERGE_CMDLINE}`. The corpus's own merge commit is listed for reference; the harness does "
  "not use its result.\n")
w("```sh\n" + NORM + "\n" + STOCK_MERGE + "\n```\n")
w("Each packet below gives the record the harness judged, its cells, the commits and path, the "
  "commands for each file, and the classes: the oracle's decided verdict and its target block "
  "index, and the hardened resolver's class, status and the block index it hit. A qualifying "
  "record is a decided hardened mis-resolution (`hard` WRONG) that the tierer placed in tier A or B "
  "with q3 and q4 \"no\". The oracle's target and the resolver's hit index the blocks of the "
  "after-file from 0; a hit given as a pair is its first and last block.\n")
w("## Packets\n")
for (name, key), cells in sorted(qual.items(), key=lambda x: x[0][0]):
    r = reps[key]
    i = inst_all[(r["arm"], r["instance"])]
    meta = i["meta"]
    ans = tiers[name]
    w(f"### `{name}`\n")
    w(f"- **Record:** `{r['id']}` ({r['arm']}, {r['mode']}, mechanism {r['mech']}, unit {r['index']}, "
      f"block type `{r['type']}`).")
    w(f"- **Qualifies in:** {'; '.join(cells)}.")
    w(f"- **Corpus:** `https://github.com/{SOURCE[r['arm']]}` at `{K.ARMS[r['arm']]['pin']}`; "
      f"path `{i['path']}`.")
    if i["mode"] == "E":
        w(f"- **Commits:** parent `{meta['parent']}`, commit `{meta['commit']}`.")
    elif i["mode"].startswith("S"):
        w(f"- **Commits:** before `{meta['before_commit']}`, after `{meta['after_commit']}` "
          f"({meta['gap']} commits apart in the path's history, from index {meta['i']}).")
    else:
        w(f"- **Commits:** merge base `{meta['base']}`, leg A `{meta['legA']}`, leg C `{meta['legC']}`; "
          f"the corpus's merge commit `{meta['merge']}`.")
    w(f"- **Oracle:** decided `{r['oracle']}`, target block {'none' if r['target'] is None else r['target']}. **Hardened resolver:** "
      f"`{r['hard']['cls']}`, status `{r['hard'].get('status')}`, hit block {r['hard'].get('hit')}.")
    w(f"- **Answers:** tier {T.tier_of(ans)}; q1 {ans['q1']}, q2 {ans['q2']}, q3 {ans['q3']}, q4 {ans['q4']}.\n")
    w("```sh\n" + "\n".join(f"{cmd} | norm > {f}" if not cmd.startswith("stock_merge") else f"{cmd} > {f}"
                            for f, cmd in file_cmds(i)) + "\n```\n")
with open(out, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print(f"qualifying packets: {len(qual)}; wrote {out}")
