# SPDX-License-Identifier: MIT
"""PRE-REGISTRATION-3.md §4, §5, §9 H3: export 3.

The texts a packet carries; PACKETS.txt; the export itself, which reuses
prereg 2's select_packets, packet_fields and write_packet unchanged; the
validator; and the checks of §5, which compare packet contents by hash and
print counts only, never a name or a text:

- same_records: export 3's real packets are prereg 2's packets, read from
  e46e320's tree, less exactly prereg 2's three plants;
- same_plants: export 3's five plant packets are this document's plants as
  prereg3_plants regenerates them;
- same_per_name: once prereg 2's sealed manifest is committed, each real
  key's packet under prereg 2's name and under prereg 3's name hold the same
  content.
"""
import collections
import hashlib
import json
import os
import shutil
import subprocess
import tempfile

from p2 import evaluate as E
from p2 import export as X

from . import binding as BD
from . import plants as PL

HERE = os.path.dirname(os.path.abspath(__file__))
SPIKE = os.path.dirname(os.path.dirname(HERE))
PREREG3 = os.path.join(SPIKE, "PRE-REGISTRATION-3.md")
# PRE-REGISTRATION-3.md as merged (blockspec 73fa0c0, #22). The
# texts a packet carries are cut from it, so a changed document is refused.
PREREG3_SHA256 = "92a97ce15783e96b042495ae6a08f581d9312a3b45460e97e2b2afd29036f8a6"
# Appendix A as PROMPT.md, as every v2.1 rehearsal recorded it (§4).
PROMPT_SHA256 = "2779cd58c9c7882aad9706e2e999c87f5e7b341f14f7141282a5bda798226a0f"
SCORING_COMMIT = "e46e320a0245e99211aea95bd436609029436f49"
EXPORT2_REL = os.path.join("results", "prereg2", "export", "packets")
MANIFEST = "PACKETS.txt"
ROOT_FILES = {"PROMPT.md", "packets", MANIFEST}


class ExportError(Exception):
    pass


# ---------------------------------------------------------------- texts

def prereg3_text():
    raw = open(PREREG3, "rb").read()
    if hashlib.sha256(raw).hexdigest() != PREREG3_SHA256:
        raise ExportError("PRE-REGISTRATION-3.md is not the merged document")
    return raw.decode("utf-8")


def appendix_a():
    return X._between(prereg3_text(), "## Appendix A — the tierer's prompt, verbatim", "## Appendix B")


def prompt_text3():
    """Appendix A as sent: the quoted paragraphs, `> ` removed."""
    lines = [ln for ln in appendix_a().splitlines() if ln.startswith(">")]
    p = "\n".join(ln[2:] if ln.startswith("> ") else ln[1:] for ln in lines) + "\n"
    if hashlib.sha256(p.encode()).hexdigest() != PROMPT_SHA256:
        raise ExportError("Appendix A does not give the registered prompt")
    return p


def questions_text3():
    """prereg 2's §7.1 table and §7.2, cut as p2/export.py cuts them, then this
    document's Appendix A."""
    t = X.prereg_text()
    table = X._between(t, "| tier | shape | qualifies |", "\nTiers are assigned")
    s72 = X._between(t, "### 7.2 Questions, and the computed tier", "### 7.3 Procedure")
    return "### 7.1 Tiers (table)\n\n" + table + "\n" + s72 + "\n" + appendix_a()


def manifest_text(names):
    return "".join(n + "\n" for n in sorted(names))


# ---------------------------------------------------------------- plants

def plant_records3():
    """Each prereg 3 plant run through the harness as a real record would be:
    the one-leg TLLC and the hardened quote resolver. A plant that does not
    come out a decided hardened mis-resolution at its stated targets raises."""
    import prereg3_plants as PP
    out = {}
    for n, (base, after, k, t, hit) in PP.PLANTS.items():
        inst = {"arm": "plant", "mode": "E", "id": f"plant:{n}", "path": "doc.md",
                "before": base, "after": after, "legs": None, "f2": True}
        recs, _ = E.evaluate(inst)
        r = [x for x in recs if x["mech"] == "Q" and x["index"] == k][0]
        if not (r.get("decided") and r["hard"]["cls"] == "WRONG" and r["target"] == t
                and r["hard"]["hit"] == hit):
            raise ExportError(f"plant {n} is not realised as Appendix B states it")
        out[n] = (r, {"before": base, "after": after, "legs": None})
    if set(out) != set(PL.PLANT_EXPECT3):
        raise ExportError("prereg3_plants.PLANTS is not P-A..P-E")
    return out


# ---------------------------------------------------------------- export

def export3(out_dir, manifest, records, instances):
    """Write export 3. Returns ({name: key} for every packet)."""
    if os.path.lexists(out_dir):
        raise ExportError(f"{out_dir} exists")
    PL.check_manifest(manifest)
    questions, prompt = questions_text3(), prompt_text3()
    nonce = manifest["nonce"]
    items = []
    for key, r in X.select_packets(records, instances).items():
        inst = instances[(r["arm"], r["instance"])]
        if "texts" not in inst:
            raise ExportError(f"{r['id']}: its instance kept no texts")
        items.append((X.packet_name(nonce, key), key, r, inst["texts"]))
    for n, (r, texts) in plant_records3().items():
        key = manifest["plants"][n]["key"]
        items.append((X.packet_name(nonce, key), key, r, texts))
    names = [i[0] for i in items]
    if len(set(names)) != len(names):
        raise ExportError("packet name collision")
    os.makedirs(os.path.join(out_dir, "packets"))
    with open(os.path.join(out_dir, "PROMPT.md"), "w", encoding="utf-8") as f:
        f.write(prompt)
    for name, key, r, texts in sorted(items):
        fields, files = X.packet_fields(r, texts)
        X.write_packet(out_dir, name, fields, files, questions)
    with open(os.path.join(out_dir, MANIFEST), "w", encoding="utf-8") as f:
        f.write(manifest_text(names))
    bad = validate3(out_dir)
    if bad:
        raise ExportError("export 3 failed its own validator: " + "; ".join(bad[:5]))
    return {i[0]: i[1] for i in items}


def validate3(root):
    """p2.export.validate's checks, with PACKETS.txt in the root allow-list and
    PROMPT.md, QUESTIONS.md and PACKETS.txt compared with this document's
    texts. Returns violations; empty means clean."""
    bad = []
    if not os.path.isdir(root):
        return [f"{root}: not a directory"]
    extra = set(os.listdir(root)) - ROOT_FILES
    if extra:
        bad.append(f"export root holds files outside the allow-list: {sorted(extra)}")
    for f in ("PROMPT.md", MANIFEST):
        p = os.path.join(root, f)
        if os.path.islink(p) or not os.path.isfile(p):
            bad.append(f"{f} missing or not a regular file")
    try:
        prompt, questions = prompt_text3(), questions_text3()
    except ExportError as e:
        return bad + [str(e)]
    if not bad:
        if open(os.path.join(root, "PROMPT.md"), encoding="utf-8").read() != prompt:
            bad.append("PROMPT.md is not Appendix A")
    pd = os.path.join(root, "packets")
    names = sorted(os.listdir(pd)) if os.path.isdir(pd) else []
    if not names:
        bad.append("no packets")
    mp = os.path.join(root, MANIFEST)
    if os.path.isfile(mp) and not os.path.islink(mp) and \
            open(mp, encoding="utf-8").read() != manifest_text(names):
        bad.append(f"{MANIFEST} does not list exactly the packets, sorted, one per line")
    # p2's per-packet checks, against this document's QUESTIONS.md. p2's
    # validate compares QUESTIONS.md and PROMPT.md with prereg 2's texts, so
    # its root and QUESTIONS findings are replaced, not reused.
    for v in X.validate(root):
        if "QUESTIONS.md is not" in v or "PROMPT.md" in v or "export root holds" in v:
            continue
        bad.append(v)
    for n in names:
        q = os.path.join(pd, n, "QUESTIONS.md")
        if os.path.isfile(q) and open(q, encoding="utf-8").read() != questions:
            bad.append(f"{n}: QUESTIONS.md is not prereg 2's §7.1 table and §7.2 with this Appendix A")
    return bad


# ---------------------------------------------------------------- content checks

def content_hash(files):
    """files: {file name: bytes} of one packet. Hashes every packet.json field
    but `packet`, and every file but packet.json and QUESTIONS.md."""
    h = hashlib.sha256()
    pj = json.loads(files["packet.json"])
    pj.pop("packet", None)
    h.update(json.dumps(pj, sort_keys=True, ensure_ascii=False).encode())
    for f in sorted(files):
        if f not in ("packet.json", "QUESTIONS.md"):
            h.update(b"\0" + f.encode() + b"\0" + files[f])
    return h.hexdigest()


def read_dir_packets(pd):
    out = {}
    for n in sorted(os.listdir(pd)):
        d = os.path.join(pd, n)
        out[n] = {f: open(os.path.join(d, f), "rb").read() for f in os.listdir(d)}
    return out


def read_tree_packets(spike, commit=SCORING_COMMIT, rel=EXPORT2_REL):
    """prereg 2's export as committed at `commit`, from git objects, not the
    work tree (§5)."""
    top = BD.toplevel(spike)
    prefix = os.path.relpath(os.path.join(spike, rel), top)
    rc, out, err = BD._git(top, "ls-tree", "-r", "--full-name", commit, "--", prefix)
    if rc != 0 or not out.strip():
        raise ExportError(f"cannot list {prefix} at {commit[:12]}: {err.strip()}")
    packets = collections.defaultdict(dict)
    for line in out.splitlines():
        meta, path = line.split("\t", 1)
        blob = meta.split()[2]
        name, fname = os.path.relpath(path, prefix).split(os.sep, 1)
        r = subprocess.run(["git", "-C", spike, "cat-file", "blob", blob],
                                         capture_output=True, env=BD.git_env())
        if r.returncode != 0:
            raise ExportError(f"cannot read blob {blob}")
        packets[name][fname] = r.stdout
    return dict(packets)


def regenerated_packets(records, questions):
    """{plant: files} for plant records, written by p2's write_packet into a
    scratch directory, exactly as an export writes them."""
    tmp = tempfile.mkdtemp(prefix="prereg3-plants-")
    try:
        out = {}
        for i, (n, (r, texts)) in enumerate(sorted(records.items())):
            name = f"{i:016x}"
            fields, files = X.packet_fields(r, texts)
            X.write_packet(tmp, name, fields, files, questions)
            out[n] = {f: open(os.path.join(tmp, "packets", name, f), "rb").read()
                      for f in os.listdir(os.path.join(tmp, "packets", name))}
        return out
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def same_records(spike, export3_dir, plant_names3, commit=SCORING_COMMIT):
    """§5: export 3's real packets are prereg 2's packets less exactly prereg
    2's three plants. Returns (ok, lines); lines carry counts only."""
    p2pk = read_tree_packets(spike, commit)
    p2h = collections.Counter(content_hash(f) for f in p2pk.values())
    p2plants = {n: content_hash(f) for n, f in
                regenerated_packets(X.plant_records(), X.questions_text()).items()}
    p3pk = read_dir_packets(os.path.join(export3_dir, "packets"))
    real3 = collections.Counter(content_hash(f) for n, f in p3pk.items() if n not in set(plant_names3.values()))
    lines = [f"prereg 2 export at {commit[:12]}: {sum(p2h.values())} packets",
             f"export 3: {len(p3pk)} packets, {sum(real3.values())} real"]
    ok = True
    for n, h in sorted(p2plants.items()):
        c = p2h.get(h, 0)
        lines.append(f"prereg 2 plant {n}: found {c} time(s) in prereg 2's export (want 1)")
        ok &= c == 1
    rest = p2h - collections.Counter(p2plants.values())
    missing, extra = rest - real3, real3 - rest
    lines.append(f"real packets in prereg 2 but not export 3: {sum(missing.values())}; "
                 f"in export 3 but not prereg 2: {sum(extra.values())}")
    ok &= not missing and not extra
    lines.append("SAME RECORDS: " + ("PASS" if ok else "FAIL"))
    return ok, lines


def same_plants(export3_dir, plant_names3):
    """§5: each of export 3's plant packets equals that plant regenerated."""
    regen = regenerated_packets(plant_records3(), questions_text3())
    ok, lines = True, []
    for p, name in sorted(plant_names3.items()):
        d = os.path.join(export3_dir, "packets", name)
        if not os.path.isdir(d):
            lines.append(f"{p}: missing from export 3")
            ok = False
            continue
        got = {f: open(os.path.join(d, f), "rb").read() for f in os.listdir(d)}
        same = content_hash(got) == content_hash(regen[p]) and got.get("QUESTIONS.md") == regen[p]["QUESTIONS.md"]
        lines.append(f"{p}: {'equal' if same else 'DIFFERS'}")
        ok &= same
    lines.append("SAME PLANTS: " + ("PASS" if ok else "FAIL"))
    return ok, lines


def same_per_name(spike, nonce2, export3_dir, nonce3, keys, commit=SCORING_COMMIT):
    """§5, at the verdict step: each real key's packet under prereg 2's name
    and under prereg 3's name hold the same content. Counts only."""
    p2pk = read_tree_packets(spike, commit)
    p3 = os.path.join(export3_dir, "packets")
    checked = differ = 0
    for k in keys:
        n2, n3 = X.packet_name(nonce2, k), X.packet_name(nonce3, k)
        checked += 1
        d3 = os.path.join(p3, n3)
        if n2 not in p2pk or not os.path.isdir(d3):
            differ += 1
            continue
        got3 = {f: open(os.path.join(d3, f), "rb").read() for f in os.listdir(d3)}
        differ += content_hash(p2pk[n2]) != content_hash(got3)
    return differ == 0, [f"per-name check: {checked} keys checked, {differ} differ",
                         "SAME PER NAME: " + ("PASS" if differ == 0 and checked else "FAIL")]
