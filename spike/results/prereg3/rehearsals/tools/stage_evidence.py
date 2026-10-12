"""Stage the rehearsal evidence for the validation-3 commit, scrubbed.

- evidence/ from the approved draft folder, copied as is (already scrubbed
  and redacted), plus REHEARSALS.md;
- runs.tar.xz: every rehearsal run directory and its export key, with local
  paths replaced in every text file (<REHEARSAL>, <SCRATCH>, <V6>, <HOME>);
- v6/: the V6 series (bars, drive log, each run's check, run-info and
  transcript), scrubbed the same way, and v6-runs.tar.xz with the full V6
  run directories.

Refuses if any staged text still holds a local path or a prereg 2 plant name.

usage: python3 -I -S -B stage_evidence.py <draft dir> <rehearsal dir> <v6 dir> <superseded v6 dir> <out dir>
"""
import hashlib
import io
import lzma
import os
import re
import shutil
import sys
import tarfile

draft, reh, v6, v6old, out = sys.argv[1:6]
SCRATCH = "<SCRATCH>"
SUBS = [(SCRATCH, "<SCRATCH>"), (reh, "<REHEARSAL>"), (v6, "<V6>"), (v6old, "<V6-702bad3>"), ("<TMP>", "<TMP>"), ("<HOME>", "<HOME>")]
FORBID = ["/home/" + "cam"]
# sha256 of prereg 2's three plant packet names (16 hex characters each).
# The names themselves are withheld until prereg 2's manifest commit (§10),
# so the check hashes every 16-hex token it meets and compares the hashes.
FORBID_NAME_SHA256 = {
    "5ddfd50ff5f4173e82216107c237d316f24283f7f5ef4b8fa5d0ed980f9d0a4e",
    "e8031ffe46edf00804c9c6fd3405253bf5d2d853b80bb490dad17f49ced930e1",
    "6b911a70f19a106e7a84fecf4229bcb374e20ead069055f5b48dd73332d43f2d",
}
HEX16 = re.compile(rb"(?<![0-9a-f])[0-9a-f]{16}(?![0-9a-f])")


def scrub(b):
    try:
        t = b.decode("utf-8")
    except UnicodeDecodeError:
        return b
    for a, r in SUBS:
        t = t.replace(a, r)
    return t.encode("utf-8")


def check(b, where):
    for f in FORBID:
        if f.encode() in b:
            sys.exit(f"refusing: {where} still holds {f!r}")
    for m in set(HEX16.findall(b)):
        if hashlib.sha256(m).hexdigest() in FORBID_NAME_SHA256:
            sys.exit(f"refusing: {where} holds one of prereg 2's plant packet names")


def tar_dirs(dest, base, names):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as tf:
        for n in names:
            root = os.path.join(base, n)
            paths = [root] if os.path.isfile(root) else [os.path.join(dp, f) for dp, _, fs in os.walk(root) for f in fs]
            # synthetic exports' packets are left out; their key files are kept
            paths = [p for p in paths if os.sep + "export" + os.sep + "packets" + os.sep not in p]
            for p in sorted(paths):
                data = scrub(open(p, "rb").read())
                check(data, p)
                ti = tarfile.TarInfo(os.path.relpath(p, base))
                ti.size, ti.mtime, ti.mode = len(data), 0, 0o644
                tf.addfile(ti, io.BytesIO(data))
    open(dest, "wb").write(lzma.compress(buf.getvalue(), preset=9))
    return len(names)


if os.path.exists(out):
    sys.exit(f"refusing: {out} exists")
os.makedirs(out)
for dp, _, fs in os.walk(os.path.join(draft, "evidence")):
    for f in fs:
        src = os.path.join(dp, f)
        dst = os.path.join(out, os.path.relpath(src, os.path.join(draft, "evidence")))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        data = scrub(open(src, "rb").read())
        check(data, src)
        open(dst, "wb").write(data)
shutil.copy(os.path.join(draft, "REHEARSALS.md"), os.path.join(out, "REHEARSALS.md"))
runs = sorted(n for n in os.listdir(reh) if n.startswith("run-")) + \
    sorted(n for n in os.listdir(reh) if n.startswith("export-") and n.endswith("-key.json")) + \
    ["rehearsal-key.json", "plants-p30-key.json", "rehearse.sh", "rehearse3.sh", "build.py", "monitor.py"]
print("runs.tar.xz:", tar_dirs(os.path.join(out, "runs.tar.xz"), reh, runs), "entries")
def stage_v6(src, sub, archive):
    v6out = os.path.join(out, sub)
    os.makedirs(v6out)
    for f in ("BARS-V6.txt", "drive.log", "SUPERSEDED.txt"):
        if os.path.exists(os.path.join(src, f)):
            data = scrub(open(os.path.join(src, f), "rb").read())
            check(data, f)
            open(os.path.join(v6out, f), "wb").write(data)
    runs6 = sorted(n for n in os.listdir(src) if n.startswith("v6"))
    for n in runs6:
        for f in ("check.txt", "run-info.txt", "key.json"):
            p = os.path.join(src, n, f)
            if os.path.exists(p):
                data = scrub(open(p, "rb").read())
                check(data, p)
                os.makedirs(os.path.join(v6out, n), exist_ok=True)
                open(os.path.join(v6out, n, f), "wb").write(data)
    print(archive + ":", tar_dirs(os.path.join(v6out, archive), src, runs6 + ["gate"]), "entries")
    return os.path.join(sub, archive)


arch = ["runs.tar.xz", stage_v6(v6, "v6", "v6-runs.tar.xz"),
        stage_v6(v6old, "v6-702bad3-superseded", "v6-runs.tar.xz")]
import hashlib  # noqa: E402
shas = {n: hashlib.sha256(open(os.path.join(out, n), "rb").read()).hexdigest()
        for n in arch}
open(os.path.join(out, "ARCHIVES.sha256"), "w").write("".join(f"{h}  {n}\n" for n, h in sorted(shas.items())))
for n, h in sorted(shas.items()):
    print(f"{h}  {n}")
total = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(out) for f in fs)
print(f"staged {out}: {total / 1e6:.1f} MB")
