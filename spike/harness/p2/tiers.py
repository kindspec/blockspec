# SPDX-License-Identifier: MIT
"""PRE-REGISTRATION-2.md §7.2 and §7.3: read tiers.jsonl, compute each
packet's tier from its answers, and apply the void rule.

The tier is computed, never read: A if question 2 is yes, otherwise B if
question 1 is yes, otherwise C. A packet the tierer marks unplaceable is
UNPLACEABLE, which is not a finding.

The tiering is void if any plant's computed tier falls on the wrong side of
the B/C line, if any plant's answer to question 3 or question 4 differs from
the expected answer, or if a plant is untiered. Confusing A with B does not
void it.
"""
import json

YN = ("yes", "no")
QUALIFIES = {"A": True, "B": True, "C": False}


def read_tiers(path):
    """{packet: answers}. The first well-formed line for a packet binds
    ("do not revise a line once it is written"); later lines for it, and
    malformed lines, are counted and ignored. Returns (tiers, problems)."""
    tiers, problems = {}, []
    try:
        lines = open(path, encoding="utf-8").read().splitlines()
    except FileNotFoundError:
        return {}, [f"{path}: missing"]
    for n, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            o = json.loads(line)
            assert isinstance(o, dict)
            for q in ("q1", "q2", "q3", "q4"):
                assert o[q] in YN
            assert isinstance(o["unplaceable"], bool)
            assert isinstance(o["packet"], str)
        except (ValueError, AssertionError, KeyError, TypeError):
            problems.append(f"line {n}: malformed")
            continue
        if o["packet"] in tiers:
            problems.append(f"line {n}: {o['packet']} already answered; first line binds")
            continue
        tiers[o["packet"]] = o
    return tiers, problems


def tier_of(ans):
    if ans.get("unplaceable"):
        return "UNPLACEABLE"
    if ans["q2"] == "yes":
        return "A"
    if ans["q1"] == "yes":
        return "B"
    return "C"


def void_reasons(manifest, plant_names, tiers):
    """plant_names: {plant: packet name}. Returns the reasons the tiering is
    void; empty means it is not."""
    out = []
    from .export import PLANT_EXPECT
    for plant, name in sorted(plant_names.items()):
        # Appendix B's expectations, never the manifest's (review C4).
        exp = PLANT_EXPECT[plant]
        ans = tiers.get(name)
        if ans is None:
            out.append(f"{plant}: untiered")
            continue
        t = tier_of(ans)
        # §7.2: UNPLACEABLE "is not a finding", so it lies on the side of the
        # B/C line that does not qualify (review A4, LOG §16).
        if QUALIFIES.get(t, False) != QUALIFIES[exp["tier"]]:
            out.append(f"{plant}: tier {t} is on the wrong side of the B/C line (expected {exp['tier']})")
        for q in ("q3", "q4"):
            if ans[q] != exp[q]:
                out.append(f"{plant}: {q}={ans[q]}, expected {exp[q]}")
    return out
