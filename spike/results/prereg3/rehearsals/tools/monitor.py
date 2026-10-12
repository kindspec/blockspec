"""Watch a rehearsal tier-run: every minute, log the line count, size and sha256 of
tier-work-1/tiers.jsonl, and flag any change that is not a pure append.
Afterwards, summarise the run against the rehearsal key.

usage: python3 -I monitor.py <run dir> <pid> <key json> <interval seconds> <export dir>
"""
import datetime
import glob
import hashlib
import json
import os
import sys
import time

run, pid, keyp, interval, export = sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4]), sys.argv[5]
NL = b"\n"
tiers = os.path.join(run, "state", "tier-work-1", "tiers.jsonl")
log = open(os.path.join(run, "tiers-poll.log"), "a", buffering=1)
t0 = time.time()
prev = b""
rewrites = 0


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def alive():
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


log.write("# utc  elapsed_s  lines  bytes  sha256  append_only\n")
while True:
    running = alive()
    cur = open(tiers, "rb").read() if os.path.isfile(tiers) else b""
    ok = cur.startswith(prev)
    if not ok:
        rewrites += 1
        for tag, data in (("before", prev), ("after", cur)):
            open(os.path.join(run, f"rewrite-{rewrites}-{tag}.jsonl"), "wb").write(data)
    log.write(f"{now()}  {int(time.time() - t0)}  {cur.count(NL)}  {len(cur)}  "
              f"{hashlib.sha256(cur).hexdigest()[:16]}  {'yes' if ok else 'REWRITE'}\n")
    prev = cur
    if not running:
        break
    time.sleep(interval)

# ---- summary
key = json.load(open(keyp))["packets"]
export_names = set(os.listdir(os.path.join(export, "packets")))
lines, bad, seen, dup = [], 0, set(), 0
for ln in prev.decode("utf-8", "replace").splitlines():
    try:
        o = json.loads(ln)
        lines.append(o)
        if o.get("packet") in seen:
            dup += 1
        seen.add(o.get("packet"))
    except ValueError:
        bad += 1
plants = {n: v for n, v in key.items() if v["expected"]}
plant_rows = []
for n, v in sorted(plants.items(), key=lambda x: x[1]["key"]):
    got = next((o for o in lines if o.get("packet") == n), None)
    exp = v["expected"]
    plant_rows.append({"plant": v["key"], "packet": n, "expected": exp,
                       "got": {k: got.get(k) for k in ("q1", "q2", "q3", "q4", "unplaceable")} if got else None})
result_events = []
tx = sorted(glob.glob(os.path.join(run, "transcripts", "*.txt")))
limit_lines = []
for p in tx:
    for ln in open(p, encoding="utf-8", errors="replace"):
        s = ln.strip().lstrip("| ").strip()
        if s.startswith("{") and '"type"' in s:
            try:
                o = json.loads(s)
            except ValueError:
                continue
            if o.get("type") == "result" or "rate_limit" in o.get("type", "") or o.get("subtype", "").startswith("error"):
                result_events.append(o)
        low = ln.lower()
        if "limit" in low and ("reset" in low or "usage" in low or "rate" in low):
            limit_lines.append(ln.rstrip()[:400])
ledger = os.path.join(run, "state", "tier-runs.txt")
summary = {
    "wall_seconds": int(time.time() - t0),
    "tiers_lines": prev.count(NL), "parsed": len(lines), "unparsable": bad, "duplicate_packets": dup,
    "distinct_packets_answered": len(seen),
    "packets_in_export": len(export_names) if export_names is not None else None,
    "unknown_packet_names": sorted(seen - export_names)[:20] if export_names is not None else None,
    "append_only": rewrites == 0, "rewrites": rewrites,
    "plants": plant_rows,
    "ledger": [json.loads(x) for x in open(ledger)] if os.path.exists(ledger) else None,
    "stream_json_result_and_error_events": result_events[-5:],
    "limit_like_lines": limit_lines[-20:],
}
json.dump(summary, open(os.path.join(run, "summary.json"), "w"), indent=1, default=str)
print(json.dumps({k: summary[k] for k in ("wall_seconds", "tiers_lines", "distinct_packets_answered",
                                          "packets_in_export", "append_only", "rewrites")}))
