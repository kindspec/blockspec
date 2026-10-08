# SPDX-License-Identifier: MIT
"""PRE-REGISTRATION-2.md §7.3: the sealed nonce manifest, the export of
packets for blind tiering, the plants mixed into it, and the validator.

A packet holds the before-file or files, the after-file (and for M both
legs), the reference -- for Q the quote text only, for R the name -- the text
of both targets, and §7.1's table, §7.2 and Appendix A. Nothing else: no
counts, rates, denominators, sharing information, other records, totals or
LOG.md. `validate()` fails any file or field outside an allow-list.
"""
import hashlib
import json
import os
import re

from . import evaluate as E
from . import mech as Mx

HERE = os.path.dirname(os.path.abspath(__file__))
PREREG = os.path.join(HERE, "..", "..", "PRE-REGISTRATION-2.md")
# PRE-REGISTRATION-2.md as merged (blockspec f59c109). The texts a packet
# carries are cut from it, so a changed document is refused, not exported.
PREREG_SHA256 = "3cbcad16df127c021cbc1216bdcac54238a4ac14084878c7f65075d161f6a18f"

# Appendix B: the expected answers and tier of each plant.
PLANT_EXPECT = {
    "P-A": {"q1": "yes", "q2": "yes", "q3": "no", "q4": "no", "tier": "A"},
    "P-B": {"q1": "yes", "q2": "no", "q3": "no", "q4": "no", "tier": "B"},
    "P-C": {"q1": "no", "q2": "no", "q3": "no", "q4": "no", "tier": "C"},
}

PACKET_FIELDS = {"packet", "reference_kind", "reference", "mechanism_target",
                 "oracle_target", "files", "questions"}
FILE_ROLES = {"before": "before.md", "after": "after.md", "base": "base.md",
              "leg_a": "leg-a.md", "leg_c": "leg-c.md"}
ROOT_FILES = {"PROMPT.md", "packets"}
NAME_RE = re.compile(r"^[0-9a-f]{16}$")
DELETED_TEXT = "(none: the oracle says the referenced text was deleted by the edit)"


class ExportError(Exception):
    pass


# ---------------------------------------------------------------- texts

def prereg_text():
    raw = open(PREREG, "rb").read()
    if hashlib.sha256(raw).hexdigest() != PREREG_SHA256:
        raise ExportError("PRE-REGISTRATION-2.md is not the merged document")
    return raw.decode("utf-8")


def _between(text, start, stop):
    a = text.index(start)
    b = text.index(stop, a)
    return text[a:b].rstrip("\n") + "\n"


def questions_text():
    """§7.1's table, §7.2 and Appendix A, cut verbatim from the document."""
    t = prereg_text()
    table = _between(t, "| tier | shape | qualifies |", "\nTiers are assigned")
    s72 = _between(t, "### 7.2 Questions, and the computed tier", "### 7.3 Procedure")
    appa = _between(t, "## Appendix A — the tierer's prompt, verbatim", "## Appendix B")
    return "### 7.1 Tiers (table)\n\n" + table + "\n" + s72 + "\n" + appa


def prompt_text():
    """Appendix A as sent: the quoted paragraphs with the `> ` quoting
    removed, nothing else changed."""
    t = prereg_text()
    a = _between(t, "## Appendix A — the tierer's prompt, verbatim", "## Appendix B")
    lines = [ln for ln in a.splitlines() if ln.startswith(">")]
    return "\n".join(ln[2:] if ln.startswith("> ") else ln[1:] for ln in lines) + "\n"


# ---------------------------------------------------------------- manifest

def seal(path, nonce=None):
    """Draw a 32-byte nonce from os.urandom and write the sealed manifest.
    Refuses to overwrite. Returns its sha256."""
    if os.path.exists(path):
        raise ExportError(f"{path} exists; a manifest is sealed once")
    nonce = nonce if nonce is not None else os.urandom(32)
    if len(nonce) != 32:
        raise ExportError("the nonce is 32 bytes")
    m = {"nonce": nonce.hex(),
         "plants": {n: {"key": f"plant:{n}", "expected": PLANT_EXPECT[n]} for n in PLANT_EXPECT}}
    data = (json.dumps(m, sort_keys=True, indent=1) + "\n").encode()
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as f:
        f.write(data)
    return hashlib.sha256(data).hexdigest()


def load_manifest(path, want_sha=None):
    raw = open(path, "rb").read()
    got = hashlib.sha256(raw).hexdigest()
    if want_sha and got != want_sha:
        raise ExportError(f"manifest sha256 {got} != committed {want_sha}")
    m = json.loads(raw)
    if len(bytes.fromhex(m["nonce"])) != 32 or set(m["plants"]) != set(PLANT_EXPECT):
        raise ExportError("malformed manifest")
    return m


def packet_name(nonce_hex, key):
    """The first 16 hex characters of sha256(nonce + ":" + packet key), the
    nonce as its 32 raw bytes."""
    return hashlib.sha256(bytes.fromhex(nonce_hex) + b":" + key.encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------- selection

def unit_key(r):
    """§6.1: (arm, sha256(block)) for Q, (arm, name, sha256(unit)) for R."""
    return (r["arm"], r["mech"], r.get("name", ""), r["unit"])


def packet_key(r):
    mt = r["hard"]["mechanism_target_text"]
    ot = r.get("oracle_target_text")
    return "|".join([r["arm"], r["mech"], r.get("name", ""), r["unit"],
                     Mx.sha256_text(mt), Mx.sha256_text(ot) if ot is not None else "DELETED"])


def f1(r, inst):
    """F1: in the arm's yaml-fence selection; a site-policy M case also in
    the strict set."""
    if "yaml-fence" not in inst.get("rules", []):
        return False
    if inst["arm"] == "site-policy" and inst["mode"] == "M":
        return bool(inst.get("strict"))
    return True


def f5(r):
    return r["mech"] == "R" or r.get("nl") is True


def eligible(r, inst):
    """§7.3: a decided mis-resolution under the hardened policy, meeting
    F1-F5, with well-formed input states (F3 covers them)."""
    return (r.get("decided") is True and r.get("hard", {}).get("cls") == "WRONG"
            and f1(r, inst) and r["f2"] and r["wf"] and f5(r))


def select_packets(records, instances):
    """{packet key: representative record}. The representative of a
    distinct (unit, mechanism target, oracle target) is its record with the
    smallest id."""
    out = {}
    for r in records:
        inst = instances[(r["arm"], r["instance"])]
        if not eligible(r, inst):
            continue
        k = packet_key(r)
        if k not in out or r["id"] < out[k]["id"]:
            out[k] = r
    return out


# ---------------------------------------------------------------- packets

def packet_fields(r, texts):
    files = {}
    if texts.get("legs"):
        files.update(base=texts["before"], leg_a=texts["legs"][0], leg_c=texts["legs"][1])
    else:
        files["before"] = texts["before"]
    files["after"] = texts["after"]
    ot = r.get("oracle_target_text")
    return {"reference_kind": "quote" if r["mech"] == "Q" else "name",
            "reference": r["reference"],
            "mechanism_target": r["hard"]["mechanism_target_text"],
            "oracle_target": ot if ot is not None else DELETED_TEXT}, files


def write_packet(root, name, fields, files, questions):
    d = os.path.join(root, "packets", name)
    os.makedirs(d)
    pj = dict(fields, packet=name, questions="QUESTIONS.md",
              files={role: FILE_ROLES[role] for role in files})
    for role, text in files.items():
        with open(os.path.join(d, FILE_ROLES[role]), "w", encoding="utf-8", newline="") as f:
            f.write(text)
    with open(os.path.join(d, "QUESTIONS.md"), "w", encoding="utf-8") as f:
        f.write(questions)
    with open(os.path.join(d, "packet.json"), "w", encoding="utf-8") as f:
        f.write(json.dumps(pj, sort_keys=True, indent=1, ensure_ascii=False) + "\n")


def plant_records():
    """Run the harness on each Appendix B plant, as for a real record: the
    one-leg TLLC and the hardened quote resolver. Returns {plant: (record,
    texts)}; a plant that does not come out a decided hardened WRONG raises."""
    import prereg2_plants as PP
    out = {}
    for n, (base, after, k, _, _) in PP.PLANTS.items():
        inst = {"arm": "plant", "mode": "E", "id": f"plant:{n}", "path": "doc.md",
                "before": base, "after": after, "legs": None, "f2": True}
        recs, _ = E.evaluate(inst)
        r = [x for x in recs if x["mech"] == "Q" and x["index"] == k][0]
        if not (r.get("decided") and r["hard"]["cls"] == "WRONG"):
            raise ExportError(f"plant {n} is not a decided hardened mis-resolution: {r}")
        out[n] = (r, {"before": base, "after": after, "legs": None})
    return out


def export(out_dir, manifest, records, instances):
    """Write the export. records: unit records; instances: {(arm, id):
    instance line with texts}. Returns (sorted packet names, {name: key})."""
    if os.path.exists(out_dir):
        raise ExportError(f"{out_dir} exists")
    questions = questions_text()
    nonce = manifest["nonce"]
    chosen = select_packets(records, instances)
    items = []
    for key, r in chosen.items():
        inst = instances[(r["arm"], r["instance"])]
        if "texts" not in inst:
            raise ExportError(f"{r['id']}: its instance kept no texts")
        items.append((packet_name(nonce, key), key, r, inst["texts"]))
    for n, (r, texts) in plant_records().items():
        items.append((packet_name(nonce, manifest["plants"][n]["key"]), manifest["plants"][n]["key"],
                      r, texts))
    names = [i[0] for i in items]
    if len(set(names)) != len(names):
        raise ExportError("packet name collision")
    os.makedirs(os.path.join(out_dir, "packets"))
    with open(os.path.join(out_dir, "PROMPT.md"), "w", encoding="utf-8") as f:
        f.write(prompt_text())
    for name, key, r, texts in sorted(items):
        fields, files = packet_fields(r, texts)
        write_packet(out_dir, name, fields, files, questions)
    bad = validate(out_dir)
    if bad:
        raise ExportError("export failed its own validator: " + "; ".join(bad))
    return sorted(names), {i[0]: i[1] for i in items}


# ---------------------------------------------------------------- validator

def _no_numbers(v, where, bad):
    if isinstance(v, bool) or isinstance(v, (int, float)):
        bad.append(f"{where}: a number or boolean ({v!r})")
    elif isinstance(v, dict):
        for k, x in v.items():
            _no_numbers(x, f"{where}.{k}", bad)
    elif isinstance(v, list):
        bad.append(f"{where}: a list")
    elif v is None:
        bad.append(f"{where}: null")
    elif not isinstance(v, str):
        bad.append(f"{where}: {type(v).__name__}")


def validate(root):
    """Returns a list of violations; empty means the export is clean."""
    bad = []
    if not os.path.isdir(root):
        return [f"{root}: not a directory"]
    extra = set(os.listdir(root)) - ROOT_FILES
    if extra:
        bad.append(f"export root holds files outside the allow-list: {sorted(extra)}")
    if not os.path.isfile(os.path.join(root, "PROMPT.md")):
        bad.append("PROMPT.md missing")
    elif open(os.path.join(root, "PROMPT.md"), encoding="utf-8").read() != prompt_text():
        bad.append("PROMPT.md is not Appendix A")
    pd = os.path.join(root, "packets")
    names = sorted(os.listdir(pd)) if os.path.isdir(pd) else []
    if not names:
        bad.append("no packets")
    q = questions_text()
    for n in names:
        d = os.path.join(pd, n)
        if not NAME_RE.match(n) or not os.path.isdir(d):
            bad.append(f"{n}: not a packet name")
            continue
        files = set(os.listdir(d))
        try:
            pj = json.load(open(os.path.join(d, "packet.json"), encoding="utf-8"))
        except (OSError, ValueError) as e:
            bad.append(f"{n}: packet.json unreadable: {e}")
            continue
        if not isinstance(pj, dict):
            bad.append(f"{n}: packet.json is not an object")
            continue
        if set(pj) - PACKET_FIELDS:
            bad.append(f"{n}: fields outside the allow-list: {sorted(set(pj) - PACKET_FIELDS)}")
        if PACKET_FIELDS - set(pj):
            bad.append(f"{n}: missing fields {sorted(PACKET_FIELDS - set(pj))}")
        _no_numbers(pj, n, bad)
        if pj.get("packet") != n:
            bad.append(f"{n}: packet.json names {pj.get('packet')!r}")
        if pj.get("reference_kind") not in ("quote", "name"):
            bad.append(f"{n}: reference_kind {pj.get('reference_kind')!r}")
        fl = pj.get("files") if isinstance(pj.get("files"), dict) else {}
        if set(fl) - set(FILE_ROLES) or any(FILE_ROLES.get(k) != v for k, v in fl.items()):
            bad.append(f"{n}: files map outside the allow-list: {fl}")
        roles = set(fl)
        if roles not in ({"before", "after"}, {"base", "leg_a", "leg_c", "after"}):
            bad.append(f"{n}: file roles {sorted(roles)}")
        # The files a packet may hold are exactly those its roles name, plus
        # packet.json and QUESTIONS.md: anything else is outside the allow-list.
        want = {FILE_ROLES[r] for r in roles if r in FILE_ROLES} | {"packet.json", "QUESTIONS.md"}
        if files != want:
            bad.append(f"{n}: files {sorted(files)} != the allow-list {sorted(want)}")
        if "QUESTIONS.md" in files and open(os.path.join(d, "QUESTIONS.md"),
                                            encoding="utf-8").read() != q:
            bad.append(f"{n}: QUESTIONS.md is not §7.1/§7.2/Appendix A")
    return bad
