# SPDX-License-Identifier: MIT
"""Build the instances of arms E, S and M from a corpus at its pin, evaluate
them, and rebuild any one instance from its id for reproduction (F9).

The id fixes the instance completely:

  E:<commit>:<path>            the commit's parent -> the commit
  S<gap>:<i>:<path>            cs[i] -> cs[i+gap] of the path's history
  M:<merge>:<path>             merge base, both parents, stock git merge
"""
import gzip
import os

from . import corpus as K
from . import evaluate as E
from . import mech as Mx

P = Mx.P


def blob(repo, commit, path):
    """`git show <commit>:<path>`, read as D8's git() and find_merge_cases()
    read it -- UTF-8 with universal newlines, which is what subprocess's
    text mode gives them -- or None if the blob is absent or is not UTF-8.
    D8's reader would raise on a non-UTF-8 blob; here it is not evaluated,
    and is counted."""
    r = K.git(repo, "show", f"{commit}:{path}", check=False)
    if r.returncode != 0:
        return None
    try:
        t = r.stdout.decode("utf-8")
    except UnicodeDecodeError:
        return None
    return t.replace("\r\n", "\n").replace("\r", "\n")


def inst_e(arm, repo, item, authors, rules):
    commit, parent, path = item
    before, after = blob(repo, parent, path), blob(repo, commit, path)
    if before is None or after is None:
        return None
    return {"arm": arm, "mode": "E", "id": f"E:{commit}:{path}", "path": path,
            "meta": {"commit": commit, "parent": parent, "author": authors.get(commit)},
            "rules": rules, "f2": True, "before": before, "after": after, "legs": None}


def inst_s(arm, repo, item, gap, authors, rules):
    path, i, ci, cj = item
    before, after = blob(repo, ci, path), blob(repo, cj, path)
    if before is None or after is None:
        return None
    return {"arm": arm, "mode": f"S{gap}", "id": f"S{gap}:{i}:{path}", "path": path,
            "meta": {"before_commit": ci, "after_commit": cj, "i": i, "gap": gap,
                     "before_author": authors.get(ci), "after_author": authors.get(cj)},
            "rules": rules, "f2": True, "before": before, "after": after, "legs": None}


def inst_m(arm, case):
    """A kept find_merge_cases() case, merged by stock git (F2). Returns
    (instance or None, merge result)."""
    res = P.stock_merge(case["base"], case["a"], case["c"], case["path"])
    meta = dict(case["meta"])
    inst = {"arm": arm, "mode": "M", "id": f"M:{meta['merge']}:{case['path']}",
            "path": case["path"], "meta": meta, "rules": case["rules"],
            "f2": bool(res["clean"]), "before": case["base"], "after": res["merged"],
            "legs": [case["a"], case["c"]]}
    if arm == "site-policy":
        inst["strict"], inst["set25"] = case["strict"], case["set25"]
    if not res["clean"] or res["merged"] is None:
        return None, res
    return inst, res


class Writer:
    """instances.jsonl and units.jsonl.gz, canonical and deterministic."""

    def __init__(self, out_dir):
        os.makedirs(out_dir, exist_ok=True)
        self.inst = open(os.path.join(out_dir, "instances.jsonl"), "w", encoding="utf-8")
        self.units = gzip.GzipFile(os.path.join(out_dir, "units.jsonl.gz"), "wb", mtime=0)

    def add(self, inst):
        recs, keep = E.evaluate(inst)
        self.inst.write(E.dumps(E.instance_line(inst, keep)) + "\n")
        for r in recs:
            self.units.write((E.dumps(r) + "\n").encode("utf-8"))
        return recs

    def close(self):
        self.inst.close()
        self.units.close()


def build_e(arm, repo, pin, sel_by_rule, k=K.SAMPLE_E):
    """Arm E instances, in sample-rank order, each tagged with the rules
    whose sample holds it. Returns (instances generator, counts)."""
    pops, counts, authors = {}, {}, None
    for rule in K.RULES:
        pop, c, authors = K.enumerate_e(arm, repo, pin, sel_by_rule[rule])
        pops[rule] = pop
        counts[rule] = c
    by_key = {}
    for rule in K.RULES:
        keys = {K.e_key(x): x for x in pops[rule]}
        for kk in K.sample(arm, list(keys), k):
            by_key.setdefault(kk, (keys[kk], []))[1].append(rule)
        counts[rule]["sample"] = min(k, len(keys))
    order = K.sample(arm, list(by_key), len(by_key))

    def gen():
        for kk in order:
            item, rules = by_key[kk]
            yield kk, inst_e(arm, repo, item, authors, rules)
    return gen(), counts


def build_s(arm, repo, sel_by_rule, gap, k=K.SAMPLE_S, cache=None):
    cache = cache if cache is not None else {}
    counts, by_key, authors = {}, {}, None
    for rule in K.RULES:
        if rule not in cache:
            cache[rule] = K.enumerate_s(arm, repo, sel_by_rule[rule])
        pops, c, authors = cache[rule]
        counts[rule] = {kk: v for kk, v in c.items() if kk == "paths" or kk.startswith(f"gap{gap}:")}
        keys = {K.s_key(x, gap): x for x in pops[gap]}
        for kk in K.sample(arm, list(keys), k):
            by_key.setdefault(kk, (keys[kk], []))[1].append(rule)
        counts[rule]["sample"] = min(k, len(keys))
    order = K.sample(arm, list(by_key), len(by_key))

    def gen():
        for kk in order:
            item, rules = by_key[kk]
            yield kk, inst_s(arm, repo, item, gap, authors, rules)
    return gen(), counts


def build_m(arm, repo, sel_by_rule):
    spec = K.ARMS[arm] if arm in K.ARMS else None
    prefix = spec["prefix"] if spec else ""
    cases, st = P.find_merge_cases(repo, prefix)
    kept, fc = K.m_filter(arm, repo, cases, sel_by_rule)
    return kept, {"find_merge_cases": dict(st), "filter": fc}


# ---------------------------------------------------------------- F9

def rebuild(arm, repo, inst_id, sel_by_rule, prefix=None):
    """Rebuild one instance from its id, at the pin, without sampling or
    enumerating anything else."""
    rules_of = lambda path: [r for r in K.RULES if path in set(sel_by_rule[r])]  # noqa: E731
    mode, rest = inst_id.split(":", 1)
    if mode == "E":
        commit, path = rest.split(":", 1)
        line = K.gtext(repo, "rev-list", "--parents", "-n", "1", commit).split()
        parent = line[1] if len(line) > 1 else None
        author = K.gtext(repo, "log", "-1", "--format=%an <%ae>", commit).rstrip("\n")
        # rules: the samples are not recomputed here, so the rules are those
        # that select the path; the committed record carries the sample's.
        return inst_e(arm, repo, (commit, parent, path), {commit: author}, rules_of(path))
    if mode.startswith("S"):
        gap = int(mode[1:])
        i, path = rest.split(":", 1)
        i = int(i)
        cs = K.path_history(repo, path)
        ci, cj = cs[i], cs[i + gap]
        au = {c: K.gtext(repo, "log", "-1", "--format=%an <%ae>", c).rstrip("\n") for c in (ci, cj)}
        return inst_s(arm, repo, (path, i, ci, cj), gap, au, rules_of(path))
    if mode == "M":
        merge, path = rest.split(":", 1)
        line = K.gtext(repo, "rev-list", "--parents", "-n", "1", merge).split()
        m, p1, p2 = line
        base = K.gtext(repo, "merge-base", "--all", p1, p2).split()
        if len(base) != 1:
            raise RuntimeError(f"{inst_id}: {len(base)} merge bases")
        base = base[0]
        case = {"path": path, "base": P.g(repo, "show", f"{base}:{path}"),
                "a": P.g(repo, "show", f"{p1}:{path}"), "c": P.g(repo, "show", f"{p2}:{path}"),
                "meta": {"merge": m, "base": base, "legA": p1, "legC": p2},
                "rules": rules_of(path)}
        if arm == "site-policy":
            subj = K.merge_subject(repo, m)
            case["meta"]["subject"] = subj
            case["strict"], case["set25"] = K.site_policy_sets(subj)
        inst, _ = inst_m(arm, case)
        return inst
    raise ValueError(f"unknown instance id {inst_id!r}")
