# SPDX-License-Identifier: MIT
"""PRE-REGISTRATION-2.md §7.3, the tierer: choosing its model, and the
wrapper around each tiering run.

- Scoring-arm commit. Derived, never named by the operator: the one commit
  in HEAD's history that added results/prereg2/score/ (review C6).
- Model (`tier_model`). The pinned model is claude-opus-5-5. The start day is
  the first UTC calendar day after the scoring-arm commit's committer date.
  The harness fetches the Models API listing itself and takes the listing's
  day from the response's Date header, which must be the start day. If the
  pinned model is not listed, the tierer is the most recent claude-opus-*
  model listed. The listing and tier-model.json are written under
  results/prereg2/ and committed; the choice holds however late tiering runs.
- Window. Tiering runs within 14 days of the scoring-arm commit. A later run
  needs a stated reason, which is logged, and changes nothing else.
- Isolation. The agent runs inside a bubblewrap sandbox (`sandbox_argv`)
  whose only view of the host is read-only system files, its own binary,
  one credential file under a fresh tmpfs HOME, and the export.
- Runs (review C2). Each run is recorded in tier-runs.txt as "started"
  BEFORE the agent starts, and its working directory, tier-work-<n>/, is
  under results/prereg2/ and is never deleted, so an aborted run leaves its
  output to be committed. The first started run binds, completed or not: if
  its tier-work-1/tiers.jsonl holds a line, no other run may start. One
  rerun is allowed, and only if the first wrote zero lines.
"""
import datetime
import email.utils
import hashlib
import json
import os
import shutil
import stat
import subprocess
import urllib.request

PINNED_MODEL = "claude-opus-5-5"
WINDOW_DAYS = 14
MODELS_URL = "https://api.anthropic.com/v1/models"
LEDGER = "tier-runs.txt"
SCORE_REL = os.path.join("results", "prereg2", "score")


class TierRefused(Exception):
    pass


def utc_day(iso):
    return datetime.datetime.fromisoformat(iso).astimezone(datetime.timezone.utc).date()


def start_day(repo, commit):
    r = subprocess.run(["git", "-C", repo, "log", "-1", "--format=%cI", commit],
                       capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        raise TierRefused(f"cannot read the committer date of {commit} in {repo}")
    cday = utc_day(r.stdout.strip())
    return cday, cday + datetime.timedelta(days=1)


def is_late(cday, today):
    """§7.3: tiering runs within 14 days of the scoring-arm commit's day."""
    return (today - cday).days > WINDOW_DAYS


def scoring_commit(spike):
    """The one commit in HEAD's history that added results/prereg2/score/."""
    r = subprocess.run(["git", "-C", spike, "log", "--format=%H", "--diff-filter=A", "--",
                        SCORE_REL], capture_output=True, text=True)
    commits = [c for c in r.stdout.split() if c]
    if len(commits) != 1:
        raise TierRefused(f"{len(commits)} commits add {SCORE_REL} in HEAD's history; "
                          "the scoring-arm results must land as one commit")
    return commits[0]


def choose_model(data, listing_day, start):
    """The pinned model if the start day's Models API listing serves it,
    otherwise the most recent claude-opus-* in that listing."""
    if listing_day != start:
        raise TierRefused(f"the Models API listing is dated {listing_day}; the start day is {start}")
    models = data["data"]
    ids = [m["id"] for m in models]
    if PINNED_MODEL in ids:
        return PINNED_MODEL, "the pinned model is listed on the start day"
    opus = [m for m in models if m["id"].startswith("claude-opus-")]
    if not opus:
        raise TierRefused("the pinned model is not listed and no claude-opus-* model is")
    return (max(opus, key=lambda m: m["created_at"])["id"],
            "the pinned model is not listed on the start day; the most recent claude-opus-* is")


def fetch_listing(url, api_key):
    """Every page of the Models API listing, and the first response's Date."""
    data, pages, date, after = [], [], None, None
    while True:
        q = url + "?limit=1000" + (f"&after_id={after}" if after else "")
        req = urllib.request.Request(q, headers={"x-api-key": api_key,
                                                 "anthropic-version": "2023-06-01"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read()
            date = date or resp.headers.get("Date")
        page = json.loads(body)
        pages.append(body.decode("utf-8"))
        data += page["data"]
        if not page.get("has_more"):
            break
        after = page["last_id"]
    if not date:
        raise TierRefused("the Models API response carried no Date header")
    return {"data": data}, pages, date


def tier_model(state_dir, spike, commit, url, api_key, log=print):
    """Fetch the listing on the start day and fix the tierer's model."""
    mpath = os.path.join(state_dir, "tier-model.json")
    if os.path.exists(mpath):
        raise TierRefused(f"{mpath} exists; the model is chosen once")
    if not api_key:
        raise TierRefused("ANTHROPIC_API_KEY is not set; the Models API needs it")
    cday, start = start_day(spike, commit)
    data, pages, date = fetch_listing(url, api_key)
    day = email.utils.parsedate_to_datetime(date).astimezone(datetime.timezone.utc).date()
    log(f"scoring-arm commit {commit}: committer day {cday} UTC; start day {start}")
    log(f"Models API {url}: Date {date} (UTC day {day}), {len(data['data'])} models")
    model, why = choose_model(data, day, start)
    os.makedirs(state_dir, exist_ok=True)
    listing = {"url": url, "date_header": date, "pages": pages}
    lraw = (json.dumps(listing, sort_keys=True, indent=1) + "\n").encode()
    with open(os.path.join(state_dir, "models-listing.json"), "wb") as f:
        f.write(lraw)
    choice = {"model": model, "why": why, "scoring_commit": commit, "start_day": str(start),
              "listing_day": str(day), "listing_date_header": date,
              "listing_sha256": hashlib.sha256(lraw).hexdigest()}
    with open(mpath, "w") as f:
        f.write(json.dumps(choice, sort_keys=True, indent=1) + "\n")
    log(f"model: {model} ({why})")
    return choice


def safe_read(path):
    """A regular file's bytes, opened without following a symlink (review
    B7); None if absent. A symlink or any other kind of file is refused."""
    try:
        st = os.lstat(path)
    except FileNotFoundError:
        return None
    if not stat.S_ISREG(st.st_mode):
        raise TierRefused(f"{path} is not a regular file (a symlink or other); refused")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, "rb") as f:
        return f.read()


def count_lines_bytes(b):
    return 0 if b is None else sum(1 for ln in b.decode("utf-8", errors="replace").splitlines() if ln.strip())


def read_ledger(state_dir):
    p = os.path.join(state_dir, LEDGER)
    if not os.path.exists(p):
        return []
    return [json.loads(ln) for ln in open(p, encoding="utf-8") if ln.strip()]


def append_ledger(state_dir, rec):
    p = os.path.join(state_dir, LEDGER)
    with open(p, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")
        f.flush()
        os.fsync(f.fileno())


def work_tiers(state_dir, n):
    return os.path.join(state_dir, f"tier-work-{n}", "tiers.jsonl")


def binding_run(state_dir):
    """The run whose tiers.jsonl binds, by the ledger: the first started run,
    unless it wrote zero lines and a second run started. Returns (n, path) or
    (None, None) if no run started."""
    started = [e["n"] for e in read_ledger(state_dir) if e.get("event") == "started"]
    if not started:
        return None, None
    if count_lines_bytes(safe_read(work_tiers(state_dir, 1))) > 0 or len(started) == 1:
        return 1, work_tiers(state_dir, 1)
    return 2, work_tiers(state_dir, 2)


def agent_binary(agent_cmd):
    """The real file the agent runs from, so the sandbox can bind just it."""
    path = shutil.which(agent_cmd) if os.sep not in agent_cmd else agent_cmd
    if not path:
        raise TierRefused(f"agent command not found: {agent_cmd}")
    return os.path.realpath(path)


def agent_argv(agent_cmd, model, prompt):
    """The default agent: a fresh Claude Code session in print mode, no saved
    session, file tools only. Any other --agent-cmd is a stub taking
    (model, prompt), used by V3."""
    binary = agent_binary(agent_cmd)
    if agent_cmd != "claude":
        return [binary, model, prompt]
    return [binary, "-p", "--model", model, "--no-session-persistence",
            "--output-format", "stream-json", "--verbose", "--permission-mode", "acceptEdits",
            "--tools", "Read", "Write", "Edit", "Glob", "Grep", "--", prompt]


SANDBOX_HOME = "/home/tierer"
DEFAULT_CREDENTIALS = os.path.expanduser("~/.claude/.credentials.json")


def sandbox_argv(work, export_dir, argv, credentials):
    """The tierer's bubblewrap sandbox (owner ruling 2026-10-08, LOG.md §15).

    Visible inside, and nothing else:
    - /usr read-only, with /bin, /lib, /lib64 and /sbin as its usual links;
    - /etc/ssl, /etc/resolv.conf (its target), /etc/hosts and
      /etc/nsswitch.conf read-only, for TLS and name resolution;
    - the agent's own binary, read-only, at its own path;
    - a fresh tmpfs HOME at /home/tierer, holding only the one credential
      file, read-only, at ~/.claude/.credentials.json;
    - /work, the working directory: an empty host directory, writable so
      the agent can write tiers.jsonl there as Appendix A asks, with the
      export's PROMPT.md and packets/ bound read-only inside it;
    - fresh /tmp, /proc and /dev.
    Every namespace is unshared except the network, which stays on: the
    network barrier is honoured, not enforced (§7.3). The environment is
    cleared except HOME, PATH and LANG."""
    resolv = os.path.realpath("/etc/resolv.conf")
    a = ["bwrap", "--die-with-parent", "--new-session", "--unshare-all", "--share-net",
         "--clearenv", "--setenv", "HOME", SANDBOX_HOME, "--setenv", "PATH", "/usr/bin:/bin",
         "--setenv", "LANG", "C.UTF-8",
         "--ro-bind", "/usr", "/usr"]
    for link, target in (("/bin", "usr/bin"), ("/lib", "usr/lib"), ("/lib64", "usr/lib64"),
                         ("/sbin", "usr/sbin")):
        a += ["--symlink", target, link]
    a += ["--ro-bind", "/etc/ssl", "/etc/ssl", "--ro-bind", resolv, "/etc/resolv.conf",
          "--ro-bind-try", "/etc/hosts", "/etc/hosts",
          "--ro-bind-try", "/etc/nsswitch.conf", "/etc/nsswitch.conf",
          "--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp",
          "--tmpfs", "/home", "--dir", SANDBOX_HOME, "--dir", SANDBOX_HOME + "/.claude",
          "--ro-bind", credentials, SANDBOX_HOME + "/.claude/.credentials.json",
          "--ro-bind", argv[0], argv[0],
          "--bind", work, "/work",
          "--ro-bind", os.path.join(export_dir, "PROMPT.md"), "/work/PROMPT.md",
          "--ro-bind", os.path.join(export_dir, "packets"), "/work/packets",
          "--chdir", "/work", "--"]
    return a + argv


def run(export_dir, state_dir, repo, commit, late_reason, agent_cmd, today=None, log=print,
        credentials=None):
    from . import export as X
    bad = X.validate(export_dir)
    if bad:
        raise TierRefused("the export fails its validator: " + "; ".join(bad))
    cday, start = start_day(repo, commit)
    today = today or datetime.datetime.now(datetime.timezone.utc).date()
    log(f"scoring-arm commit {commit}: committer day {cday} UTC; start day {start}; today {today}")
    if today < start:
        raise TierRefused(f"tiering starts on {start}, the first UTC day after the scoring-arm commit")
    if is_late(cday, today):
        if not late_reason:
            raise TierRefused(f"{(today - cday).days} days after the scoring-arm commit: "
                              f"a run after {WINDOW_DAYS} days needs --late-reason")
        log(f"LATE RUN, {(today - cday).days} days after the commit. Reason: {late_reason}")
    mpath = os.path.join(state_dir, "tier-model.json")
    if not os.path.exists(mpath):
        raise TierRefused("no tier-model.json: run `prereg2.py tier-model` on the start day first")
    choice = json.load(open(mpath))
    if choice.get("scoring_commit") != commit:
        raise TierRefused("tier-model.json was chosen for another scoring-arm commit")
    log(f"model: {choice['model']} ({choice['why']})")
    started = [e for e in read_ledger(state_dir) if e.get("event") == "started"]
    if len(started) >= 2:
        raise TierRefused("two tiering runs have started; no further run is allowed")
    if started:
        done = [e for e in read_ledger(state_dir) if e.get("event") == "completed" and e["n"] == 1]
        lines = count_lines_bytes(safe_read(work_tiers(state_dir, 1)))
        log(f"run 1 started earlier, {'completed' if done else 'did not complete'}, "
            f"and wrote {lines} line(s)")
        if lines > 0:
            raise TierRefused("the first run's tiers.jsonl binds; a rerun is allowed only if it "
                              f"wrote zero lines (it wrote {lines})")
        log("RERUN: the first run wrote zero lines")
    elif os.path.lexists(os.path.join(state_dir, "tiers.jsonl")):
        raise TierRefused("tiers.jsonl exists before any recorded run")
    n = len(started) + 1
    credentials = credentials or DEFAULT_CREDENTIALS
    if not os.path.isfile(credentials):
        raise TierRefused(f"credential file not found: {credentials}")
    if not shutil.which("bwrap"):
        raise TierRefused("bwrap is not installed; the tierer runs only inside its sandbox")
    work = os.path.join(state_dir, f"tier-work-{n}")
    os.makedirs(work)
    export_dir = os.path.realpath(export_dir)
    prompt = open(os.path.join(export_dir, "PROMPT.md"), encoding="utf-8").read()
    n_packets = len(os.listdir(os.path.join(export_dir, "packets")))
    log(f"working directory: /work in a bwrap sandbox, holding only PROMPT.md and "
        f"{n_packets} packets, read-only; its output stays in {work}")
    log(f"Appendix A as sent, sha256 {hashlib.sha256(prompt.encode()).hexdigest()}:")
    for ln in prompt.splitlines():
        log("  | " + ln)
    argv = sandbox_argv(work, export_dir, agent_argv(agent_cmd, choice["model"], prompt), credentials)
    log("sandboxed agent: " + " ".join(argv[:-1]) + " <PROMPT.md>")
    append_ledger(state_dir, {"event": "started", "n": n,
                              "at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                              "model": choice["model"], "work": os.path.basename(work)})
    rc, p = None, None
    try:
        log("---- agent output ----")
        p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in p.stdout:
            log(line.rstrip("\n"))
        rc = p.wait()
        log(f"---- agent exit status {rc} ----")
    finally:
        if p is not None and p.poll() is None:
            p.terminate()
        for mp in ("PROMPT.md", "packets"):
            q = os.path.join(work, mp)
            if os.path.isfile(q) and not os.path.islink(q) and os.path.getsize(q) == 0:
                os.remove(q)
            elif os.path.isdir(q) and not os.path.islink(q) and not os.listdir(q):
                os.rmdir(q)
        b = safe_read(os.path.join(work, "tiers.jsonl"))
        nl = count_lines_bytes(b)
        h = hashlib.sha256(b or b"").hexdigest()
        append_ledger(state_dir, {"event": "completed" if rc is not None else "aborted", "n": n,
                                  "lines": nl, "sha256": h, "agent_exit": rc})
        log(f"run {n}: tiers.jsonl {nl} lines, sha256 {h}, kept as written in {work}")
    if b is not None:
        with open(os.path.join(state_dir, "tiers.jsonl"), "wb") as f:
            f.write(b)
    return rc, nl
