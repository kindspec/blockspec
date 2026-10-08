# SPDX-License-Identifier: MIT
"""The two mechanisms of PRE-REGISTRATION-2.md §3, and the D8 pin.

Q, the quote anchor, is imported unchanged from kindspec/research
`experiments/D8-identity/` at d51ce09: `anchor_eval.anchor_of` builds it and
`anchor_eval3.reanchor2` resolves it.

R, the named reference, is new harness code. Two pieces are copied verbatim
from d51ce09, because their modules run experiments when imported:
`slugs()` from e9_headings.py lines 8-13, and `REGION` and `regions()` from
e6_transclude.py lines 14 and 17-31. They sit between the COPIED markers
below, and V3 compares them with the source lines byte for byte.
"""
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
sys.dont_write_bytecode = True

import d8_cheap_arm as C  # noqa: E402
import prose_merge as P  # noqa: E402

# sha256 of each file at kindspec/research d51ce09cdb23 (§3). anchor_eval*.py
# are byte-identical at f088cd76fd13. A --d8-dir whose files differ is refused.
D8_PIN = "d51ce09cdb23af32f35e7a3c6111ac21ab0f033f"
D8_SHA256 = {
    "anchor_eval.py": "889ac71c30eedfcfc21f6ae0b3d891b5224a8095e38e57acd76307cd339c9675",
    "anchor_eval2.py": "cb6d0c512a842d13d59b5916acc87598fe3b5da3c24d3e176be62ec5323a7c6a",
    "anchor_eval3.py": "d9404bc9534afcd857715348e5358dcd0efd084da5f04e01fb4b7f72c0d16369",
    "e9_headings.py": "67086b524ea3cafe437c6b967fb74c9720fba478c702ea1a338bf80a775c2734",
    "e6_transclude.py": "ee960a4b6c3765e9847d4af2f8158c2bd33860ae4fef0384f69383963f38d7cf",
}

D8 = D82 = D83 = None
NL_TYPES = ("prose", "list", "heading")   # F5


class Refused(SystemExit):
    pass


def sha256_text(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def verify_d8(d8_dir):
    bad = []
    for f, want in D8_SHA256.items():
        p = os.path.join(d8_dir, f)
        try:
            got = hashlib.sha256(open(p, "rb").read()).hexdigest()
        except OSError:
            got = "missing"
        if got != want:
            bad.append(f"{f}: {got[:16]} != {want[:16]}")
    return bad


def load(d8_dir):
    """Import the mechanism from a --d8-dir whose files match d51ce09."""
    global D8, D82, D83
    d8_dir = os.path.abspath(d8_dir)
    bad = verify_d8(d8_dir)
    if bad:
        print("prereg2: --d8-dir is not kindspec/research experiments/D8-identity "
              f"at {D8_PIN[:12]}: " + "; ".join(bad), file=sys.stderr)
        raise Refused(2)
    if D8 is None:
        if d8_dir not in sys.path:
            sys.path.insert(0, d8_dir)
        import anchor_eval  # noqa: E402
        import anchor_eval2  # noqa: E402
        import anchor_eval3  # noqa: E402
        D8, D82, D83 = anchor_eval, anchor_eval2, anchor_eval3
    P.D8, P.D83 = D8, D83
    C.D8, C.D82, C.D83 = D8, D82, D83
    return D8, D82, D83


def typer(text, blk):
    """btype(), except that a block inside a leading YAML fence is
    `frontmatter` (§4 F5). This is d8_cheap_arm's --frontmatter-type rule."""
    end = C.frontmatter_end(text)
    if end >= 0 and blk["off"] < end:
        return "frontmatter"
    return D83.btype(blk["content"])


# ---- COPIED VERBATIM: e9_headings.py lines 8-13 at d51ce09 ----
def slugs(t):
    out=[]
    for m in re.finditer(r'^(#{1,6})\s+(.+?)\s*$', t, re.M):
        s=re.sub(r'[^\w\s-]','',m.group(2).lower()).strip().replace(' ','-')
        out.append(s)
    return out
# ---- END COPIED ----

# ---- COPIED VERBATIM: e6_transclude.py line 14 at d51ce09 ----
REGION = re.compile(r'^<!--\s*#([a-z0-9][a-z0-9-]*)\s*-->$', re.M)
# ---- END COPIED ----

# ---- COPIED VERBATIM: e6_transclude.py lines 17-31 at d51ce09 ----
def regions(text):
    """name -> [block text].  A named region is the block FOLLOWING a marker line."""
    out={}; lines=text.split('\n'); i=0
    while i < len(lines):
        m = REGION.match(lines[i].strip())
        if m:
            j=i+1
            while j<len(lines) and not lines[j].strip(): j+=1
            blk=[]
            while j<len(lines) and lines[j].strip() and not REGION.match(lines[j].strip()):
                blk.append(lines[j]); j+=1
            if blk: out.setdefault(m.group(1),[]).append('\n'.join(blk))
            i=j
        else: i+=1
    return out
# ---- END COPIED ----

COPIED = (("e9_headings.py", 8, 13), ("e6_transclude.py", 14, 14),
          ("e6_transclude.py", 17, 31))

# slugs()'s own pattern, used only to read the level of a heading slugs()
# has already named. It is the same expression, so the two cannot disagree on
# which lines are headings.
_HEADING = re.compile(r'^(#{1,6})\s+(.+?)\s*$', re.M)


def line_to_block(text, bl):
    return P._line_to_block(text, bl)


def headings(text, bl):
    """[(block index, level, slug)], one per name slugs() yields, over the
    blocks btype() types `heading` (§3)."""
    out = []
    for i, b in enumerate(bl):
        if D83.btype(b["content"]) != "heading":
            continue
        names = slugs(b["content"])
        levels = [len(m.group(1)) for m in _HEADING.finditer(b["content"])]
        assert len(names) == len(levels)
        for s, lv in zip(names, levels):
            out.append((i, lv, s))
    return out


def region_spans(text, bl):
    """[(name, block index)]: regions(), with the block each region's first
    line lies in. The scan mirrors regions() line for line, and its output is
    checked against regions() so the two cannot drift."""
    lines = text.split('\n')
    l2b = line_to_block(text, bl)
    out, got = [], {}
    i = 0
    while i < len(lines):
        m = REGION.match(lines[i].strip())
        if m:
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            start, blk = j, []
            while j < len(lines) and lines[j].strip() and not REGION.match(lines[j].strip()):
                blk.append(lines[j])
                j += 1
            if blk:
                got.setdefault(m.group(1), []).append('\n'.join(blk))
                out.append((m.group(1), l2b[start]))
            i = j
        else:
            i += 1
    if got != regions(text):
        raise AssertionError("region_spans() disagrees with regions()")
    return out


def section_end(bl, hs, h):
    """Last block index of the section headed by block h: the heading plus
    the blocks up to the next heading of the same or a higher level (§3)."""
    lv = min(l for i, l, _ in hs if i == h)
    for i, l, _ in hs:
        if i > h and l <= lv:
            return i - 1
    return len(bl) - 1


def r_names(text, bl):
    """Every name in a text: region names, then slugs."""
    names = [n for n, _ in region_spans(text, bl)]
    names += [s for _, _, s in headings(text, bl)]
    return sorted(set(names))


REF = "#REF!"


def resolve_r(text, bl, name):
    """§3 Resolution. Region markers first, then slugs. Zero matches, or more
    than one, is #REF!. Returns (kind, first block, last block) or REF."""
    reg = [b for n, b in region_spans(text, bl) if n == name]
    if reg:
        return ("region", reg[0], reg[0]) if len(reg) == 1 else REF
    hs = headings(text, bl)
    hit = [i for i, _, s in hs if s == name]
    if len(hit) == 1:
        return ("slug", hit[0], section_end(bl, hs, hit[0]))
    return REF


def span_text(text, bl, a, b):
    """The text of blocks a..b inclusive, from a's first byte to b's last."""
    return text[bl[a]["off"]:bl[b]["off"] + len(bl[b]["content"])]
