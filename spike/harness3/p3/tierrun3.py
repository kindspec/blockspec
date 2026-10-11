# SPDX-License-Identifier: MIT
"""PRE-REGISTRATION-3.md §6, §9 H4: prereg 3's tier-run.

p2/tierrun.py's run, with these differences:
- the export is validated with export3.validate3;
- the sandbox also binds <export>/PACKETS.txt read-only at /work/PACKETS.txt;
- the agent argv adds --strict-mcp-config, and the first JSON event must be
  system/init with exactly the five built-in tools and no MCP server, else
  the agent is stopped and the run is recorded `init_failed`, which never
  binds;
- the credential file's sha256 and mtime are logged before and after; a run
  whose transcript shows an authentication error is labelled `auth_aborted`,
  which is a label only: it binds like any run that wrote a line (§0 item 10);
- the gate, start day and window are §6's (gates.py); the model is read from
  the pinned results/prereg2/tier-model.json;
- the ledger and work directories are under results/prereg3/;
- the run cap: one rerun in total, ever, allowed only if the first run wrote
  zero lines or was `init_failed`.
"""
import datetime
import hashlib
import json
import os
import subprocess

from p2 import tierrun as T2

from . import export3 as X3
from . import gates as G

INIT_TOOLS = ["Edit", "Glob", "Grep", "Read", "Write"]
AUTH_TEXT = "Failed to authenticate"


def is_auth_error(line):
    """An authentication failure in the agent's stream: an event whose
    error_status is 401 or 403, or the CLI's 'Failed to authenticate'."""
    if AUTH_TEXT in line:
        return True
    try:
        ev = json.loads(line)
    except ValueError:
        return False
    return isinstance(ev, dict) and ev.get("error_status") in (401, 403)
LEDGER = "tier-runs.txt"


class TierRefused(Exception):
    pass


def read_ledger(state_dir):
    p = os.path.join(state_dir, LEDGER)
    if not os.path.exists(p):
        return []
    return [json.loads(ln) for ln in open(p, encoding="utf-8") if ln.strip()]


def append_ledger(state_dir, rec):
    with open(os.path.join(state_dir, LEDGER), "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")
        f.flush()
        os.fsync(f.fileno())


def work_tiers(state_dir, n):
    return os.path.join(state_dir, f"tier-work-{n}", "tiers.jsonl")


def run_status(state_dir, n):
    """(lines, init_failed) of run n, from the ledger and its work dir."""
    ends = [e for e in read_ledger(state_dir) if e.get("n") == n and e.get("event") != "started"]
    init_failed = any(e.get("init_failed") for e in ends)
    return T2.count_lines_bytes(T2.safe_read(work_tiers(state_dir, n))), init_failed


def rerun_allowed(state_dir):
    """The run cap. Returns (n of the next run, note) or raises TierRefused."""
    started = [e["n"] for e in read_ledger(state_dir) if e.get("event") == "started"]
    if not started:
        return 1, None
    if len(started) >= 2:
        raise TierRefused("two tiering runs have started; there is one rerun in total, ever")
    lines, init_failed = run_status(state_dir, 1)
    if init_failed:
        return 2, "RERUN: the first run failed the init check"
    if lines == 0:
        return 2, "RERUN: the first run wrote zero lines"
    raise TierRefused(f"the first run's tiers.jsonl binds; it wrote {lines} line(s)")


def binding_run(state_dir):
    """(n, path) of the binding run, or (None, None). A run that failed the
    init check, or wrote nothing, binds nothing."""
    started = [e["n"] for e in read_ledger(state_dir) if e.get("event") == "started"]
    for n in started:
        lines, init_failed = run_status(state_dir, n)
        if not init_failed and lines > 0:
            return n, work_tiers(state_dir, n)
        if not init_failed and n == started[-1]:
            return n, work_tiers(state_dir, n)
    return None, None


def cred_stat(path):
    """sha256 and mtime of the credential file. The bytes are hashed, never
    printed."""
    st = os.stat(path)
    with open(path, "rb") as f:
        h = hashlib.sha256(f.read()).hexdigest()
    return {"sha256": h, "mtime": datetime.datetime.fromtimestamp(
        st.st_mtime, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}


def agent_argv(agent_cmd, model, prompt):
    argv = T2.agent_argv(agent_cmd, model, prompt)
    if agent_cmd == "claude":
        i = argv.index("--permission-mode") + 2
        argv[i:i] = ["--strict-mcp-config"]
    return argv


def sandbox_argv(work, export_dir, argv, credentials):
    a = T2.sandbox_argv(work, export_dir, argv, credentials)
    i = a.index("--chdir")
    a[i:i] = ["--ro-bind", os.path.join(export_dir, X3.MANIFEST), "/work/" + X3.MANIFEST]
    return a


def init_ok(ev):
    return (isinstance(ev, dict) and ev.get("type") == "system" and ev.get("subtype") == "init"
            and sorted(ev.get("tools") or []) == INIT_TOOLS and ev.get("mcp_servers") == [])


def run(export_dir, state_dir, gate_repo, late_reason, agent_cmd, today=None, log=print,
        credentials=None):
    bad = X3.validate3(export_dir)
    if bad:
        raise TierRefused("the export fails its validator: " + "; ".join(bad[:5]))
    try:
        vc = G.verdict_gate(gate_repo)
        log(f"gate: prereg 2's verdict commit {vc[:12]} (bound to {G.BD.PREREG2_VALIDATION[:12]})")
        today = today or datetime.datetime.now(datetime.timezone.utc).date()
        log(G.window(G.commit_day(gate_repo, vc), today, late_reason))
        model = G.tier_model(gate_repo)
    except G.GateError as e:
        raise TierRefused(str(e))
    log(f"model: {model} (results/prereg2/tier-model.json, blob {G.TIER_MODEL_BLOB[:12]})")
    os.makedirs(state_dir, exist_ok=True)
    n, note = rerun_allowed(state_dir)
    if note:
        log(note)
    credentials = credentials or T2.DEFAULT_CREDENTIALS
    if not os.path.isfile(credentials):
        raise TierRefused(f"credential file not found: {credentials}")
    if not T2.shutil.which("bwrap"):
        raise TierRefused("bwrap is not installed; the tierer runs only inside its sandbox")
    work = os.path.join(state_dir, f"tier-work-{n}")
    os.makedirs(work)
    export_dir = os.path.realpath(export_dir)
    prompt = open(os.path.join(export_dir, "PROMPT.md"), encoding="utf-8").read()
    n_packets = len(os.listdir(os.path.join(export_dir, "packets")))
    log(f"working directory: /work in a bwrap sandbox, holding only PROMPT.md, {X3.MANIFEST} and "
        f"{n_packets} packets, read-only; its output stays in {work}")
    log(f"Appendix A as sent, sha256 {hashlib.sha256(prompt.encode()).hexdigest()}")
    cred0 = cred_stat(credentials)
    log(f"credential before: mtime {cred0['mtime']}, sha256 {cred0['sha256'][:16]}")
    argv = sandbox_argv(work, export_dir, agent_argv(agent_cmd, model, prompt), credentials)
    log("sandboxed agent: " + " ".join(argv[:-1]) + " <PROMPT.md>")
    append_ledger(state_dir, {"event": "started", "n": n,
                              "at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                              "model": model, "work": os.path.basename(work)})
    rc, p, checked, init_failed, auth = None, None, False, False, False
    try:
        log("---- agent output ----")
        p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in p.stdout:
            log(line.rstrip("\n"))
            if is_auth_error(line):
                auth = True
            if not checked:
                try:
                    ev = json.loads(line)
                except ValueError:
                    continue
                checked = True
                if init_ok(ev):
                    log(f"init check: tools {INIT_TOOLS}, mcp_servers []")
                else:
                    init_failed = True
                    log("INIT CHECK FAILED: the first JSON event is not system/init with exactly "
                        f"{INIT_TOOLS} and no MCP server; stopping the agent")
                    p.terminate()
        rc = p.wait()
        if not checked:
            init_failed = True
            log("INIT CHECK FAILED: the stream ended with no init event")
        log(f"---- agent exit status {rc} ----")
    finally:
        if p is not None and p.poll() is None:
            p.terminate()
        for mp in ("PROMPT.md", X3.MANIFEST, "packets"):
            q = os.path.join(work, mp)
            if os.path.isfile(q) and not os.path.islink(q) and os.path.getsize(q) == 0:
                os.remove(q)
            elif os.path.isdir(q) and not os.path.islink(q) and not os.listdir(q):
                os.rmdir(q)
        b = T2.safe_read(os.path.join(work, "tiers.jsonl"))
        nl = T2.count_lines_bytes(b)
        h = hashlib.sha256(b or b"").hexdigest()
        cred1 = cred_stat(credentials)
        log(f"credential after: mtime {cred1['mtime']}, sha256 {cred1['sha256'][:16]}"
            + ("  (CHANGED during the run)" if cred1 != cred0 else ""))
        rec = {"event": "completed" if rc is not None else "aborted", "n": n, "lines": nl,
               "sha256": h, "agent_exit": rc, "init_failed": init_failed,
               "credential_changed": cred1 != cred0}
        if auth:
            rec["status"] = "auth_aborted"
        append_ledger(state_dir, rec)
        log(f"run {n}: tiers.jsonl {nl} lines, sha256 {h}"
            + ("; init_failed: this run never binds" if init_failed else "")
            + ("; auth_aborted (a label: the run binds if it wrote a line)" if auth else ""))
    return rc, nl, init_failed
