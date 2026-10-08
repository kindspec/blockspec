# SPDX-License-Identifier: MIT
"""§9: every invocation of an arm, the exporter or the tierer, aborted ones
included, writes a transcript under results/prereg2/ that is committed.

The transcript is opened before anything else runs, written line-buffered,
and closed in a `finally` with the exit status, so an abort by exception,
SIGINT, SIGTERM or SIGHUP still records how it ended. A SIGKILL cannot be
caught; the header and everything printed up to it are already on disk.
"""
import datetime
import os
import signal
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SPIKE = os.path.dirname(os.path.dirname(HERE))
DEFAULT_DIR = os.path.join(SPIKE, "results", "prereg2", "transcripts")


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def head(spike=SPIKE):
    r = subprocess.run(["git", "-C", spike, "rev-parse", "HEAD"], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


class _Tee:
    def __init__(self, stream, f):
        self.stream, self.f = stream, f

    def write(self, s):
        self.stream.write(s)
        self.f.write(s)
        return len(s)

    def flush(self):
        self.stream.flush()
        self.f.flush()

    def __getattr__(self, n):
        return getattr(self.stream, n)


class Transcript:
    def __init__(self, cmd, label, argv, out_dir=None):
        out_dir = out_dir or DEFAULT_DIR
        os.makedirs(out_dir, exist_ok=True)
        stamp = now().replace(":", "")
        name = f"{stamp}-{cmd}" + (f"-{label}" if label else "")
        path = os.path.join(out_dir, name + ".txt")
        n = 1
        while os.path.exists(path):
            n += 1
            path = os.path.join(out_dir, f"{name}.{n}.txt")
        self.path = path
        self.f = open(path, "w", encoding="utf-8", buffering=1)
        self.f.write(f"# prereg2 {cmd}{' ' + label if label else ''}\n"
                     f"# argv: {' '.join(argv)}\n"
                     f"# start: {now()}\n"
                     f"# blockspec HEAD: {head()}\n"
                     f"# python {sys.version.split()[0]}\n")
        self.state = {"bound": False, "reasons": ["binding not yet checked"]}
        self._out, self._err = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = _Tee(sys.stdout, self.f), _Tee(sys.stderr, self.f)
        for s in (signal.SIGTERM, signal.SIGHUP):
            signal.signal(s, self._signal)

    def record_binding(self, state):
        """Write the binding check into the header, once, before any work."""
        self.state = state
        self.f.write(f"# harness bound: {state['bound']}"
                     + (f" (validation commit {state.get('validation_commit')})" if state["bound"] else "")
                     + "\n")
        for r in state.get("reasons", []) if not state["bound"] else []:
            self.f.write(f"#   not bound: {r}\n")
        self.f.write("\n")

    def _signal(self, signum, frame):
        raise SystemExit(128 + signum)

    def close(self, rc, how="exited"):
        sys.stdout.flush()
        sys.stderr.flush()
        sys.stdout, sys.stderr = self._out, self._err
        self.f.write(f"\n# end: {now()}\n# {how}: exit status {rc}\n")
        self.f.close()
