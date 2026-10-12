"""Build the synthetic tiering rehearsal exports (prereg 2), outside every repo.

Structure and sizes mirror the real export, from file sizes only. Text comes from
pydoc renderings of CPython standard-library modules: no prereg-2 or research
corpus text, and no real packet text. Three synthetic plants are shaped like
Appendix B's packets but use their own text.

usage: python3 -I build.py <real-sizes.json> <harness dir> <out root>
"""
import hashlib
import json
import os
import pydoc
import random
import re
import sys

sizes_path, harness, root = sys.argv[1:4]
sys.path.insert(0, harness)
sys.dont_write_bytecode = True
from p2 import export as X  # noqa: E402  (prompt and question texts, and the validator)

rng = random.Random(20261010)
MODULES = ["json", "csv", "argparse", "pathlib", "collections", "itertools", "functools", "datetime",
           "decimal", "fractions", "statistics", "random", "re", "string", "textwrap", "difflib",
           "logging", "subprocess", "shutil", "tempfile", "zipfile", "tarfile", "gzip", "hashlib",
           "hmac", "secrets", "socket", "selectors", "asyncio", "threading", "queue", "sched",
           "heapq", "bisect", "array", "copy", "pprint", "enum", "dataclasses", "typing", "abc",
           "contextlib", "inspect", "dis", "ast", "tokenize", "unittest", "doctest", "pdb", "timeit",
           "trace", "sqlite3", "pickle", "shelve", "configparser", "email", "http.client",
           "urllib.parse", "urllib.request", "html", "html.parser", "xml.dom.minidom",
           "xml.etree.ElementTree", "base64", "binascii", "struct", "codecs", "locale", "gettext",
           "calendar", "zoneinfo", "math", "cmath", "operator", "weakref", "types", "io", "os",
           "os.path", "glob", "fnmatch", "filecmp", "stat", "uuid", "ipaddress", "mimetypes", "wave",
           "colorsys", "graphlib", "numbers", "platform", "sysconfig", "warnings", "traceback"]


def pool():
    paras = []
    for m in MODULES:
        try:
            t = pydoc.plain(pydoc.render_doc(m, renderer=pydoc.plaintext))
        except Exception:
            continue
        for block in re.split(r"\n\s*\n", t):
            lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
            if not lines:
                continue
            text = " ".join(lines)
            if len(text) < 30 or "Python Library Documentation" in text:
                continue
            paras.append(text[:1200])
    return paras


PARAS = pool()
WORDS = sorted({w for p in PARAS[:4000] for w in re.findall(r"\b[A-Z][a-z]{3,12}\b", p)})


def heading():
    return " ".join(rng.sample(WORDS, 2))


def doc(target):
    """Markdown sections of about `target` bytes: (list of blocks, as text)."""
    blocks, i = [], rng.randrange(len(PARAS))
    size = 0
    while size < target:
        if not blocks or rng.random() < 0.25:
            b = "## " + heading()
        else:
            b = PARAS[i % len(PARAS)]
            i += 1
        blocks.append(b)
        size += len(b.encode()) + 2
    return blocks


def render(blocks):
    return "\n\n".join(blocks) + "\n"


def fit(blocks, target, keep):
    """Trim or pad trailing blocks past index `keep` toward `target` bytes."""
    while len(render(blocks).encode()) > target and len(blocks) > keep + 1:
        blocks.pop()
    while len(render(blocks).encode()) < target:
        blocks.append(PARAS[rng.randrange(len(PARAS))])
    return blocks


def edit(p):
    w = p.split()
    for _ in range(max(1, len(w) // 12)):
        k = rng.randrange(len(w))
        w[k] = rng.choice(["now", "no longer", "only", "also", "never", "always", "first"])
    return " ".join(w)


def quote_pair(bsize, asize):
    b = doc(max(bsize, 600))
    idx = [k for k, x in enumerate(b[: max(4, len(b) // 2)]) if not x.startswith("## ") and len(x) > 60]
    if not idx:
        b.insert(1, PARAS[rng.randrange(len(PARAS))])
        idx = [1]
    k = rng.choice(idx)
    ref = b[k]
    a = list(b)
    a[k] = edit(ref)
    j = rng.randrange(k + 1, len(a) + 1)
    a[j:j] = ["## " + heading(), "Earlier wording, kept for reference:", ref]
    a = fit(a, asize, j + 2)
    return b, a, ref, a[k], ref  # before, after, reference, oracle target, mechanism target


def name_pair(bsize, asize):
    b = doc(max(bsize, 600))
    hs = [k for k, x in enumerate(b) if x.startswith("## ")]
    if len(hs) < 2:
        b += ["## " + heading(), PARAS[rng.randrange(len(PARAS))]]
        hs = [k for k, x in enumerate(b) if x.startswith("## ")]
    k, m = rng.sample(hs, 2)
    name = b[k][3:]
    a = list(b)
    a[k] = "## " + name + " (" + rng.choice(["retired", "legacy", "draft", "v2"]) + ")"
    a[m] = "## " + name
    if rng.random() < 0.5:
        a.insert(min(m + 1, len(a)), f"See also {name}.")
    a = fit(a, asize, max(k, m) + 2)

    def section(blocks, h):
        out = [blocks[h]]
        for x in blocks[h + 1:]:
            if x.startswith("## "):
                break
            out.append(x)
        return "\n\n".join(out)
    return b, a, name, section(a, k), section(a, m)


def plants():
    """Three plants shaped like Appendix B's P-A, P-B, P-C, with their own text."""
    pa_b = ["## Backup service", "Snapshots are kept for seven days\nbefore they are pruned.",
            "## Restore service", "Restores are verified against a checksum manifest."]
    pa_a = ["## Backup service", "Snapshots are kept for thirty days\nbefore they are pruned.",
            "## Restore service", "Restores are verified against a checksum manifest.",
            "## Change log", "Superseded Backup wording, kept for the change log:",
            "Snapshots are kept for seven days\nbefore they are pruned."]
    pb_b = ["## Working group Gamma", "Gamma moves build caching into the shared runners.",
            "Status: this proposal was accepted by steering vote on 2026-05-12.",
            "## Working group Delta", "Delta adds a signed provenance file to each release.",
            "Status: this proposal was accepted by steering vote on 2026-05-12."]
    pb_a = list(pb_b)
    pb_a[1] = "Gamma was narrowed to cover only nightly builds."
    pb_a[4] = "Delta moves build caching into the shared runners."
    note = "> **Note:** All dates in this section are local to the venue."
    pc_b = ["## Office hours", note, "Hours run from 10:00 to 12:00 on Tuesdays.",
            "Extra hours may be added with a day's notice.", note]
    pc_a = ["## Office hours", "Extra hours may be added with a day's notice.", note,
            "Hours run from 11:00 to 13:00 on Tuesdays.", note]
    return {
        "R-A": (pa_b, pa_a, pa_b[1], pa_a[1], pa_a[6],
                {"q1": "yes", "q2": "yes", "q3": "no", "q4": "no", "tier": "A"}),
        "R-B": (pb_b, pb_a, pb_b[2], pb_a[2], pb_a[5],
                {"q1": "yes", "q2": "no", "q3": "no", "q4": "no", "tier": "B"}),
        "R-C": (pc_b, pc_a, note, pc_a[2], pc_a[4],
                {"q1": "no", "q2": "no", "q3": "no", "q4": "no", "tier": "C"}),
    }


def main():
    rows = json.load(open(sizes_path))
    two = sorted([r for r in rows if "before.md" in r], key=lambda r: sum(r.values()))
    legs = [r for r in rows if "base.md" in r]
    two_real = two[3:]          # the three smallest two-file slots become the plants
    rng.shuffle(two_real)
    # reference-kind mix of the real export, from packet.json reference_kind only
    two_kinds = ["quote"] * (165 - 3) + ["name"] * 271
    leg_kinds = ["quote"] * 33 + ["name"] * 17
    rng.shuffle(two_kinds)
    rng.shuffle(leg_kinds)
    nonce = os.urandom(32).hex()
    items = []
    for i, (r, kind) in enumerate(zip(two_real, two_kinds)):
        pair = quote_pair if kind == "quote" else name_pair
        b, a, ref, ot, mt = pair(r["before.md"], r["after.md"])
        items.append((f"syn:{i}", kind, {"before": render(b), "after": render(a)}, ref, mt, ot, None))
    for i, (r, kind) in enumerate(zip(legs, leg_kinds)):
        pair = quote_pair if kind == "quote" else name_pair
        b, la, ref, ot, mt = pair(r["base.md"], r["leg-a.md"])
        lc = fit(list(b) + [PARAS[rng.randrange(len(PARAS))]], r["leg-c.md"], len(b))
        after = fit(list(la), r["after.md"], len(la) - 1)
        items.append((f"leg:{i}", kind, {"base": render(b), "leg_a": render(la), "leg_c": render(lc),
                                         "after": render(after)}, ref, mt, ot, None))
    for n, (b, a, ref, ot, mt, exp) in plants().items():
        items.append((f"plant:{n}", "quote", {"before": render(b), "after": render(a)}, ref, mt, ot, exp))
    named = []
    for key, kind, files, ref, mt, ot, exp in items:
        name = hashlib.sha256(f"{nonce}:{key}".encode()).hexdigest()[:16]
        named.append((name, key, kind, files, ref, mt, ot, exp))
    named.sort()
    subset = set(n[0] for n in named if n[1].startswith("plant:"))
    others = [n for n in named if not n[1].startswith("plant:")]
    legs_n = [n for n in others if n[1].startswith("leg:")]
    two_n = [n for n in others if n[1].startswith("syn:")]
    subset |= {n[0] for n in rng.sample(legs_n, 12)} | {n[0] for n in rng.sample(two_n, 120 - 12 - 3)}
    q = X.questions_text()
    for label, keep in (("export-486", None), ("export-120", subset)):
        out = os.path.join(root, label)
        os.makedirs(os.path.join(out, "packets"))
        open(os.path.join(out, "PROMPT.md"), "w", encoding="utf-8").write(X.prompt_text())
        for name, key, kind, files, ref, mt, ot, exp in named:
            if keep is not None and name not in keep:
                continue
            X.write_packet(out, name, {"reference_kind": kind, "reference": ref,
                                       "mechanism_target": mt, "oracle_target": ot}, files, q)
        bad = X.validate(out)
        print(label, len(os.listdir(os.path.join(out, "packets"))), "packets; validator:",
              "clean" if not bad else bad[:3])
    key = {name: {"key": k, "kind": kind, "expected": exp} for name, k, kind, _, _, _, _, exp in named}
    json.dump({"note": "rehearsal key: synthetic packets only; plants carry expected answers",
               "in_120": sorted(subset), "packets": key},
              open(os.path.join(root, "rehearsal-key.json"), "w"), indent=1, sort_keys=True)


main()
