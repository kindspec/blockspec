# SPDX-License-Identifier: MIT
"""PRE-REGISTRATION-2.md §7.3, the tierer: the wrapper around one tiering run.

- Model. The pinned model is claude-opus-5-5. The start day is the first UTC
  calendar day after the scoring-arm commit's committer date. If the pinned
  model is not served on the start day, the tierer is the most recent
  `claude-opus-*` model the Models API lists that day. The choice is made
  from a Models API listing fetched on the start day, recorded with its
  sha256 in tier-model.json, and it holds however late tiering runs.
- Window. Tiering runs within 14 days of the scoring-arm commit. A later run
  needs a stated reason, which is logged, and changes nothing else.
- Isolation. The agent runs inside a bubblewrap sandbox (`sandbox_argv`)
  whose only view of the host is read-only system files, its own binary,
  one credential file under a fresh tmpfs HOME, and the export. No
  blockspec checkout, no other repository and no ~/.claude history is
  visible. The network stays on, and that barrier is honoured, not
  enforced (§7.3).
- Runs. The first run's tiers.jsonl binds and is committed as written. At
  most one rerun, and only if the first run wrote zero lines.
- Every run writes a transcript (the caller's), including the agent's own
  output stream.
"""
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import tempfile

PINNED_MODEL = "claude-opus-5-5"
WINDOW_DAYS = 14


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


def choose_model(listing_path, listing_day, start):
    """The pinned model if the start day's Models API listing serves it,
    otherwise the most recent claude-opus-* in that listing."""
    if listing_day != start:
        raise TierRefused(f"the Models API listing is dated {listing_day}; the start day is {start}")
    raw = open(listing_path, "rb").read()
    data = json.loads(raw)
    models = data["data"] if isinstance(data, dict) else data
    ids = [m["id"] for m in models]
    if PINNED_MODEL in ids:
        model, why = PINNED_MODEL, "the pinned model is listed on the start day"
    else:
        opus = [m for m in models if m["id"].startswith("claude-opus-")]
        if not opus:
            raise TierRefused("the pinned model is not listed and no claude-opus-* model is")
        model = max(opus, key=lambda m: m["created_at"])["id"]
        why = "the pinned model is not listed on the start day; the most recent claude-opus-* is"
    return {"model": model, "why": why, "listing_sha256": hashlib.sha256(raw).hexdigest(),
            "listing_day": str(listing_day), "start_day": str(start)}


def count_lines(path):
    if not os.path.exists(path):
        return None
    return sum(1 for ln in open(path, encoding="utf-8") if ln.strip())


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


def run(export_dir, out_tiers, state_dir, repo, scoring_commit, listing, listing_day,
        late_reason, agent_cmd, today=None, log=print, credentials=None):
    from . import export as X
    bad = X.validate(export_dir)
    if bad:
        raise TierRefused("the export fails its validator: " + "; ".join(bad))
    cday, start = start_day(repo, scoring_commit)
    today = today or datetime.datetime.now(datetime.timezone.utc).date()
    log(f"scoring-arm commit {scoring_commit}: committer day {cday} UTC; start day {start}; today {today}")
    if today < start:
        raise TierRefused(f"tiering starts on {start}, the first UTC day after the scoring-arm commit")
    late = (today - cday).days > WINDOW_DAYS
    if late:
        if not late_reason:
            raise TierRefused(f"{(today - cday).days} days after the scoring-arm commit: "
                              f"a run after {WINDOW_DAYS} days needs --late-reason")
        log(f"LATE RUN, {(today - cday).days} days after the commit. Reason: {late_reason}")
    os.makedirs(state_dir, exist_ok=True)
    mpath = os.path.join(state_dir, "tier-model.json")
    if os.path.exists(mpath):
        choice = json.load(open(mpath))
        log(f"model: {choice['model']} (chosen earlier: {choice['why']})")
    else:
        choice = choose_model(listing, datetime.date.fromisoformat(listing_day), start)
        with open(mpath, "w") as f:
            f.write(json.dumps(choice, sort_keys=True, indent=1) + "\n")
        log(f"model: {choice['model']} ({choice['why']}; listing sha256 {choice['listing_sha256']})")
    runs_path = os.path.join(state_dir, "tier-runs.txt")
    prior = [ln for ln in open(runs_path).read().splitlines() if ln.strip()] \
        if os.path.exists(runs_path) else []
    existing = count_lines(out_tiers)
    if prior:
        if len(prior) >= 2:
            raise TierRefused("two tiering runs already; no further run is allowed")
        if existing is None or existing > 0:
            raise TierRefused("the first run's tiers.jsonl binds; a rerun is allowed only if it "
                              f"wrote zero lines (it has {existing})")
        log("RERUN: the first run wrote zero lines")
    elif existing is not None:
        raise TierRefused(f"{out_tiers} exists before any recorded run")
    credentials = credentials or DEFAULT_CREDENTIALS
    if not os.path.isfile(credentials):
        raise TierRefused(f"credential file not found: {credentials}")
    if not shutil.which("bwrap"):
        raise TierRefused("bwrap is not installed; the tierer runs only inside its sandbox")
    work = tempfile.mkdtemp(prefix="tiering.")
    try:
        export_dir = os.path.realpath(export_dir)
        prompt = open(os.path.join(export_dir, "PROMPT.md"), encoding="utf-8").read()
        n_packets = len(os.listdir(os.path.join(export_dir, "packets")))
        log(f"working directory: /work in a bwrap sandbox, holding only PROMPT.md and "
            f"{n_packets} packets, read-only")
        log(f"Appendix A as sent, sha256 {hashlib.sha256(prompt.encode()).hexdigest()}:")
        for ln in prompt.splitlines():
            log("  | " + ln)
        argv = sandbox_argv(work, export_dir, agent_argv(agent_cmd, choice["model"], prompt),
                            credentials)
        log("sandboxed agent: " + " ".join(argv[:-1]) + " <PROMPT.md>")
        log("---- agent output ----")
        p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in p.stdout:
            log(line.rstrip("\n"))
        rc = p.wait()
        log(f"---- agent exit status {rc} ----")
        src = os.path.join(work, "tiers.jsonl")
        os.makedirs(os.path.dirname(os.path.abspath(out_tiers)), exist_ok=True)
        if os.path.exists(src):
            shutil.copyfile(src, out_tiers)
        else:
            open(out_tiers, "w").close()
        n = count_lines(out_tiers)
        h = hashlib.sha256(open(out_tiers, "rb").read()).hexdigest()
        log(f"tiers.jsonl: {n} lines, sha256 {h}, committed as written")
        with open(runs_path, "a") as f:
            f.write(f"{datetime.datetime.now(datetime.timezone.utc).isoformat()} model={choice['model']} "
                    f"lines={n} sha256={h} agent_exit={rc}\n")
        return rc, n
    finally:
        shutil.rmtree(work, ignore_errors=True)
