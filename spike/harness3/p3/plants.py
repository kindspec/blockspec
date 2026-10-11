# SPDX-License-Identifier: MIT
"""PRE-REGISTRATION-3.md §1, §3, §9 H2: the five plants' expected answers,
the sealed manifest, and the void rule over all five.

p2/export.py's PLANT_EXPECT stays at three plants and is read by
p2.tiers.void_reasons, p2.export.load_manifest and, through the former,
p2.aggregate.aggregate. None of those three is called by prereg 3: with a
five-plant manifest they raise KeyError on P-D. This module replaces them.
"""
import hashlib
import json
import os

from p2 import export as X

# §3's table: expected answers and tier, never a manifest's own.
PLANT_EXPECT3 = {
    "P-A": {"q1": "yes", "q2": "yes", "q3": "no", "q4": "no", "tier": "A"},
    "P-B": {"q1": "yes", "q2": "no", "q3": "no", "q4": "no", "tier": "B"},
    "P-C": {"q1": "no", "q2": "no", "q3": "no", "q4": "no", "tier": "C"},
    "P-D": {"q1": "yes", "q2": "yes", "q3": "yes", "q4": "no", "tier": "A"},
    "P-E": {"q1": "yes", "q2": "yes", "q3": "yes", "q4": "yes", "tier": "A"},
}
QUALIFIES = {"A": True, "B": True, "C": False}


class PlantError(Exception):
    pass


def manifest_plants():
    return {n: {"key": f"plant:{n}", "expected": PLANT_EXPECT3[n]} for n in PLANT_EXPECT3}


def seal(path, nonce=None):
    """Draw a 32-byte nonce from os.urandom and write the sealed manifest.
    Refuses to overwrite. Returns its sha256."""
    if os.path.lexists(path):
        raise PlantError(f"{path} exists; a manifest is sealed once")
    nonce = nonce if nonce is not None else os.urandom(32)
    if len(nonce) != 32:
        raise PlantError("the nonce is 32 bytes")
    data = (json.dumps({"nonce": nonce.hex(), "plants": manifest_plants()}, sort_keys=True, indent=1)
            + "\n").encode()
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as f:
        f.write(data)
    return hashlib.sha256(data).hexdigest()


def check_manifest(m):
    """A manifest's plants must be exactly P-A..P-E, keyed plant:P-x, with
    §3's expectations."""
    if not isinstance(m, dict) or m.get("plants") != manifest_plants():
        raise PlantError("the manifest's plants are not PRE-REGISTRATION-3.md's Appendix B")
    try:
        if len(bytes.fromhex(m["nonce"])) != 32:
            raise ValueError
    except (KeyError, ValueError, TypeError):
        raise PlantError("malformed manifest: the nonce is not 32 bytes")
    return m


def load_manifest(path, want_sha):
    if not want_sha or len(want_sha) != 64:
        raise PlantError("the manifest's expected sha256 is required")
    raw = open(path, "rb").read()
    got = hashlib.sha256(raw).hexdigest()
    if got != want_sha:
        raise PlantError(f"manifest sha256 {got} != committed {want_sha}")
    return check_manifest(json.loads(raw))


def plant_names(manifest):
    return {p: X.packet_name(manifest["nonce"], v["key"]) for p, v in manifest["plants"].items()}


def tier_of(ans):
    if ans.get("unplaceable"):
        return "UNPLACEABLE"
    return "A" if ans["q2"] == "yes" else ("B" if ans["q1"] == "yes" else "C")


def void_reasons(names, tiers):
    """§1's void rule over all five plants. names: {plant: packet name}."""
    out = []
    if set(names) != set(PLANT_EXPECT3):
        out.append(f"plants {sorted(names)} are not {sorted(PLANT_EXPECT3)}")
    for plant, name in sorted(names.items()):
        exp = PLANT_EXPECT3.get(plant)
        if exp is None:
            continue
        ans = tiers.get(name)
        if ans is None:
            out.append(f"{plant}: untiered")
            continue
        t = tier_of(ans)
        if QUALIFIES.get(t, False) != QUALIFIES[exp["tier"]]:
            out.append(f"{plant}: tier {t} is on the wrong side of the B/C line (expected {exp['tier']})")
        for q in ("q3", "q4"):
            if ans[q] != exp[q]:
                out.append(f"{plant}: {q}={ans[q]}, expected {exp[q]}")
    return out
