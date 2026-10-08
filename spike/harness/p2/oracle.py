# SPDX-License-Identifier: MIT
"""PRE-REGISTRATION-2.md §5: TLLC in its three forms, and the two rules for
what it cannot decide.

TLLC itself is `prose_merge.tllc()`, used unmodified (§5.1):

- two-leg form (M): tllc(base, A, C, merged, ...);
- one-leg form (E, S): leg C is the base and the merged text is the
  after-state, so tllc(base, after, base, after, ...) -- both legs reduce to
  the single alignment base->after, exactly as harness/prereg2_plants.py
  calls it;
- section form (R): tllc() over one pseudo-block spanning the unit, so frac_L
  and the plurality vote run over the unit's non-blank lines.

UNDECIDABLE-REPEAT and UNDECIDABLE-SPLIT (§5.2) are new code. Neither reads
the mechanism's answer.
"""
from collections import Counter

from . import mech as Mx

P = Mx.P


def tllc_legs(base, after, legs):
    """The (side_a, side_c) pair tllc() is called with."""
    return (legs[0], legs[1]) if legs else (after, base)


def block_oracle(base, after, legs, bb, bm):
    a, c = tllc_legs(base, after, legs)
    return P.tllc(base, a, c, after, bb, bm)


def pseudo_block(text, bl, first, last):
    return {"off": bl[first]["off"], "content": Mx.span_text(text, bl, first, last)}


def unit_oracle(base, after, legs, bb, bm, first, last):
    """Section form: TLLC over base blocks first..last as one unit. Returns
    (verdict, after-state block) exactly as tllc() does for a block."""
    a, c = tllc_legs(base, after, legs)
    return P.tllc(base, a, c, after, [pseudo_block(base, bb, first, last)], bm)[0]


def proposing_maps(base, after, legs, base_lines):
    """For each leg that proposed a target for the unit made of base_lines
    (its non-blank lines), the mapped after-lines. Mirrors tllc()'s per-leg
    computation: compose base->leg and leg->after, a leg proposes when
    frac >= ORACLE_CONFIDENCE and its mapped lines land in some block."""
    a, c = tllc_legs(base, after, legs)
    lb, lm = base.splitlines(), after.splitlines()
    mine = [L for L in base_lines if L < len(lb) and lb[L].strip()]
    out = []
    if not mine:
        return out
    for leg in (a, c):
        ll = leg.splitlines()
        b2l = P._line_map(lb, ll)
        l2m = P._line_map(ll, lm)
        phi = {L: l2m[j] for L, j in b2l.items() if j in l2m}
        mapped = [phi[L] for L in mine if L in phi]
        if len(mapped) / len(mine) >= P.ORACLE_CONFIDENCE:
            out.append(mapped)
    return out


def base_lines_of(text, bl, first, last):
    s = text.count("\n", 0, bl[first]["off"])
    e = text.count("\n", 0, bl[last]["off"]) + bl[last]["content"].count("\n")
    return list(range(s, e + 1))


def split_rule(base, after, legs, base_lines, after_line_to_unit):
    """UNDECIDABLE-SPLIT: the mapped lines of k, under the leg or legs that
    proposed a target, fall in two or more units of M. Returns True when it
    fires. Mapped lines in no unit are not in a unit and are not counted."""
    units = set()
    for mapped in proposing_maps(base, after, legs, base_lines):
        units |= {after_line_to_unit[L] for L in mapped if L in after_line_to_unit}
    return len(units) >= 2


def repeat_rule(Bc, Mc, target, k, t):
    """UNDECIDABLE-REPEAT. Bc, Mc: unit contents of B and M, by index.
    target(i): TLLC's SURVIVED target for B[i], as an index into Mc, or None.
    Returns True when the verdict is DECIDED, False when it is
    UNDECIDABLE-REPEAT."""
    T = [c for c in range(len(Mc)) if c != t and (Mc[c] == Mc[t] or Mc[c] == Bc[k])]
    if not T:
        return True
    nb, nm = Counter(Bc), Counter(Mc)

    def ctx(c):
        n = 0
        for d in (-1, 1):
            kk, cc = k + d, c + d
            if not (0 <= kk < len(Bc) and 0 <= cc < len(Mc)):
                continue
            if nb[Bc[kk]] > 1 or nm[Mc[cc]] > 1:
                continue
            if target(kk) == cc:
                n += 1
        return n
    s = {c: ctx(c) for c in [t] + T}
    return s[t] >= 1 and all(s[t] > s[c] for c in T)


# ---------------------------------------------------------------- units

def block_units(text, bl):
    """Q units, and R region units: blocks."""
    return [(i, i) for i in range(len(bl))]


def heading_units(text, bl):
    """R slug units for §5.2 only: the span from a heading to the next heading
    of any level. The text names heading spans only, so blocks before the
    first heading lie in no unit (review A4, LOG §16)."""
    starts = sorted({i for i, _, _ in Mx.headings(text, bl)})
    return [(s, (starts[n + 1] - 1) if n + 1 < len(starts) else len(bl) - 1)
            for n, s in enumerate(starts)]


def unit_of_block(units):
    m = {}
    for u, (a, b) in enumerate(units):
        for i in range(a, b + 1):
            m[i] = u
    return m


def line_to_unit(text, bl, units):
    l2b = Mx.line_to_block(text, bl)
    b2u = unit_of_block(units)
    return {L: b2u[b] for L, b in l2b.items() if b in b2u}
