"""Build prereg-3 rehearsal exports with the PROTOTYPE harness.

  plants mode: 30 - (number of plants) synthetic fillers drawn at random from export-486 (its
  three R-* plants excluded) plus the three candidate plants. Every packet
  gets a fresh random name, and packet.json's `packet` field matches it.
  Plant packet fields come from the harness's own evaluate() path (one-leg
  TLLC and the hardened quote resolver), never by hand.

  full mode: as plants mode, but with all 483 synthetic fillers.

  copy mode: every packet of export-486 under its own name, rewritten with
  the prototype's PROMPT.md, QUESTIONS.md and PACKETS.txt.

Both modes write PROMPT.md, PACKETS.txt and packets/ with the prototype's
export.write_packet, and refuse to finish unless its validator is clean.
Neither touches the source export.

usage:
  python3 -I -S -B build3.py plants <harness> <d8> <plants.py> <export-486> <rehearsal-key.json> <out> <out-key.json>
  python3 -I -S -B build3.py full   (same arguments as plants)
  python3 -I -S -B build3.py copy   <harness> <d8> <export-486> <out>
"""
import hashlib
import json
import os
import random
import runpy
import sys

mode, harness, d8 = sys.argv[1:4]
sys.path.insert(0, harness)
from p2 import mech as Mx  # noqa: E402
Mx.load(d8)
from p2 import evaluate as E  # noqa: E402
from p2 import export as X  # noqa: E402

ROLE_OF = {v: k for k, v in X.FILE_ROLES.items()}


def read_packet(src_root, name):
    d = os.path.join(src_root, "packets", name)
    pj = json.load(open(os.path.join(d, "packet.json"), encoding="utf-8"))
    fields = {k: pj[k] for k in ("reference_kind", "reference", "mechanism_target", "oracle_target")}
    files = {role: open(os.path.join(d, fn), encoding="utf-8", newline="").read()
             for role, fn in pj["files"].items()}
    return fields, files


def finish(out, names):
    with open(os.path.join(out, "PROMPT.md"), "w", encoding="utf-8") as f:
        f.write(X.prompt_text())
    with open(os.path.join(out, X.MANIFEST), "w", encoding="utf-8") as f:
        f.write(X.manifest_text(names))
    bad = X.validate(out)
    if bad:
        sys.exit("validator: " + "; ".join(bad[:5]))
    print(out, len(names), "packets; validator clean; PROMPT.md sha256",
          hashlib.sha256(X.prompt_text().encode()).hexdigest())


def fresh_names(n):
    out = set()
    while len(out) < n:
        out.add(os.urandom(8).hex())
    return sorted(out)


if mode in ("plants", "full"):
    plants_py, src, keyp, out, out_key = sys.argv[4:9]
    if os.path.exists(out) or os.path.exists(out_key):
        sys.exit(f"refusing: {out} or {out_key} exists")
    PL = runpy.run_path(plants_py)["PLANTS"]
    key = json.load(open(keyp))["packets"]
    pool = sorted(n for n, v in key.items() if not v["expected"])
    # plants mode: 30 packets in all; full mode: every synthetic filler
    fillers = random.SystemRandom().sample(pool, 30 - len(PL)) if mode == "plants" else list(pool)
    items = []
    for n in fillers:
        f, fl = read_packet(src, n)
        items.append(({"key": f"filler:{n}", "source": n, "plant": None, "expected": None}, f, fl))
    for p, (base, after, k, t, hit) in PL.items():
        inst = {"arm": "plant", "mode": "E", "id": f"plant:{p}", "path": "doc.md",
                "before": base, "after": after, "legs": None, "f2": True}
        recs, _ = E.evaluate(inst)
        r = [x for x in recs if x["mech"] == "Q" and x["index"] == k][0]
        if not (r.get("decided") and r["hard"]["cls"] == "WRONG" and r["target"] == t
                and r["hard"]["hit"] == hit):
            sys.exit(f"plant {p} is not realised as stated: {r}")
        f, fl = X.packet_fields(r, {"before": base, "after": after, "legs": None})
        exp = dict(X.PLANT_EXPECT[p])
        items.append(({"key": f"plant:{p}", "source": None, "plant": p, "expected": exp}, f, fl))
    names = fresh_names(len(items))
    random.SystemRandom().shuffle(items)
    os.makedirs(os.path.join(out, "packets"))
    q = X.questions_text()
    keyout = {"plants_py_sha256": hashlib.sha256(open(plants_py, "rb").read()).hexdigest(),
              "packets": {}}
    for name, (meta, f, fl) in zip(names, items):
        X.write_packet(out, name, f, fl, q)
        keyout["packets"][name] = meta
    finish(out, names)
    json.dump(keyout, open(out_key, "w"), indent=1, sort_keys=True)
elif mode == "copy":
    src, out = sys.argv[4:6]
    if os.path.exists(out):
        sys.exit(f"refusing: {out} exists")
    names = sorted(os.listdir(os.path.join(src, "packets")))
    os.makedirs(os.path.join(out, "packets"))
    q = X.questions_text()
    for n in names:
        f, fl = read_packet(src, n)
        X.write_packet(out, n, f, fl, q)
    finish(out, names)
else:
    sys.exit(__doc__)
