#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""D8's single-edit anchor analysis and quote-uniqueness measurement, made
runnable on corpora other than the three D8 hardcodes.

WHAT THIS IS NOT: a verdict, a tier, or a criterion. It produces input for a
pre-registration that has not been written. Nothing here decides FOUND or
NOT FOUND under `spike/PRE-REGISTRATION.md`.

THE MECHANISM IS IMPORTED, NOT COPIED. `blocks`, `anchor_of`, `git`
(anchor_eval), `line_oracle` (anchor_eval2) and `reanchor2`, `btype`
(anchor_eval3) are imported from an unmodified kindspec/research checkout named
by --d8-dir. Only the two DRIVER loops are copied, because both hardcode their
corpora:

  anchors     <- anchor_eval3.py `run()` and its `__main__` printer
  uniqueness  <- e4_uniqueness.py, whose loop runs at import time

What changed in each copy, and nothing else:

  1. The corpus is a CLI argument (`--corpus NAME REPO PIN PATHSPEC`), not a
     path hardcoded relative to the working directory. PATHSPEC may hold
     several whitespace-separated git pathspecs, e.g. ':(exclude).github/'.
     Headers print NAME where the original printed `os.path.basename(repo)`,
     so a corpus named as D8 names it prints D8's bytes.
  2. The file list comes from `select_files()`: D8's own rule
     (`git ls-files PATHSPEC`, keep `*.md`, in ls-files order) minus, only when
     --exclude-generated is given, files whose own text declares them generated.
     Without that flag the list is D8's, element for element.
  3. --frontmatter-type (off by default) types a block lying inside a leading
     YAML frontmatter fence as `frontmatter` instead of calling `btype()`.
     D8 §11 item 8: btype() has no frontmatter rule and calls it `prose`. It
     changes LABELS only -- reanchor2() never sees a type.
  4. --gaps (anchors; default 5,25 as D8) selects the version-skip gaps, and
     --show-wrong (off by default) prints each silent-wrong, as D8 §3.2 quotes
     its own. Neither changes what is sampled or how it is scored.
  5. It FAILS LOUDLY. The originals exit 0 printing `files=0` or
     `too few (0)` when run from the wrong directory (kindspec/research#6).
     This exits 2 on a missing or non-git corpus, on a HEAD that is not the
     stated pin, on an empty selection, and on an arm that read nothing; and 1
     on any arm that raised.

Bytecode is not written: --d8-dir is a checkout this script must not modify.
"""
import argparse
import os
import random
import re
import subprocess
import sys
from collections import Counter

sys.dont_write_bytecode = True

D8 = D82 = D83 = None


def die(msg, code=2):
    print(f"d8_cheap_arm: {msg}", file=sys.stderr)
    sys.exit(code)


def load_d8(path):
    if not os.path.isfile(os.path.join(path, "anchor_eval3.py")):
        die(f"--d8-dir has no anchor_eval3.py: {path}")
    sys.path.insert(0, os.path.abspath(path))
    global D8, D82, D83
    import anchor_eval as D8          # noqa: E402
    import anchor_eval2 as D82        # noqa: E402
    import anchor_eval3 as D83        # noqa: E402


# ---------------------------------------------------------------- selection

GENERATED = re.compile(
    r"^auto_generated:[ \t]*true[ \t]*$"          # kubernetes/website frontmatter
    r"|THIS FILE IS AUTO-GENERATED",               # cncf/toc generator banner
    re.MULTILINE | re.IGNORECASE)


def check_corpus(name, repo, pin):
    if not os.path.isdir(repo):
        die(f"{name}: corpus directory does not exist: {repo}")
    r = subprocess.run(["git", "-C", repo, "rev-parse", "--show-toplevel", "HEAD"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        die(f"{name}: not a git work tree: {repo}\n{r.stderr.strip()}")
    top, head = r.stdout.split()
    if os.path.realpath(top) != os.path.realpath(repo):
        die(f"{name}: {repo} is inside a work tree rooted at {top}, not its root")
    if head != pin:
        die(f"{name}: HEAD is {head}, pinned at {pin}")


def select_files(name, repo, pathspec, exclude_generated):
    r = subprocess.run(["git", "-C", repo, "ls-files", *pathspec.split()],
                       capture_output=True, text=True)
    if r.returncode != 0:
        die(f"{name}: git ls-files failed: {r.stderr.strip()}")
    files = [f for f in r.stdout.split("\n") if f.endswith(".md")]
    excluded = []
    if exclude_generated:
        keep = []
        for f in files:
            try:
                t = open(os.path.join(repo, f), encoding="utf-8").read()
            except Exception:
                keep.append(f)      # unreadable: uniqueness counts it as skipped
                continue
            (excluded if GENERATED.search(t) else keep).append(f)
        files = keep
    if not files:
        die(f"{name}: pathspec {pathspec!r} selects no .md files in {repo}")
    return files, excluded


def frontmatter_end(text):
    """Offset just past a leading YAML frontmatter fence, or -1."""
    m = re.match(r"---[ \t]*\n.*?\n---[ \t]*(\n|$)", text, re.DOTALL)
    return m.end() if m else -1


def make_typer(frontmatter):
    if not frontmatter:
        return lambda text, b: D83.btype(b["content"])

    def typer(text, b):
        end = frontmatter_end(text)
        if end >= 0 and b["off"] < end:
            return "frontmatter"
        return D83.btype(b["content"])
    return typer


# ---------------------------------------------------------------- anchors
# Copied from anchor_eval3.py `run()`. Changes: `files` and `typer` are
# parameters (was: git ls-files glob, and btype(content)).

def run(repo, files, gap, typer, sf=14, sb=30, seed=7, wrongs=None):
    git, blocks, anchor_of = D8.git, D8.blocks, D8.anchor_of
    line_oracle, reanchor2 = D82.line_oracle, D83.reanchor2
    rnd=random.Random(seed); t=Counter(); pairs=0
    files=list(files)
    rnd.shuffle(files); files=files[:sf]
    for f in files:
        cs=[c for c in git(repo,'log','--format=%H','--reverse','--',f).split('\n') if c]
        if len(cs)<gap+1: continue
        for start in range(0,len(cs)-gap,max(1,(len(cs)-gap)//3 or 1)):
            ti,tj=git(repo,'show',f'{cs[start]}:{f}'),git(repo,'show',f'{cs[start+gap]}:{f}')
            if not ti or not tj or ti==tj: continue
            bi,bj=blocks(ti),blocks(tj)
            if len(bi)<4 or len(bj)<4: continue
            pairs+=1; orc=line_oracle(ti,tj,bi,bj)
            idx=list(range(len(bi))); rnd.shuffle(idx)
            for k in idx[:sb]:
                anc=anchor_of(ti,bi[k])
                if len(anc['quote'])<20: continue
                truth,tgt=orc[k]
                if truth=='UNKNOWN': t['skip']+=1; continue
                ty=typer(ti,bi[k]); t['EV']+=1; t['TY:'+ty]+=1
                for lab,hard in (('naive',False),('hard',True)):
                    st,hit=reanchor2(tj,anc,bj,hard)
                    ok = (hit==tgt) if truth=='SURVIVED' else (hit is None)
                    if hit is None and truth=='SURVIVED': cls='LOUD'
                    elif ok: cls='correct'
                    else: cls='WRONG'
                    t[f'{lab}:{cls}']+=1
                    if cls=='WRONG': t[f'{lab}:WRONG:{ty}']+=1
                    if cls=='WRONG' and wrongs is not None:
                        wrongs.append((lab, st, ty, truth, f, cs[start], cs[start+gap],
                                       anc['quote'], None if hit is None else bj[hit]['content'],
                                       None if tgt is None else bj[tgt]['content']))
    return t,pairs


def cmd_anchors(a, corpora):
    typer = make_typer(a.frontmatter_type)
    gaps = [int(g) for g in a.gaps.split(",")]
    failed = False
    for name, repo, pathspec, files in corpora:
        total_pairs = 0
        for gap in gaps:
            wrongs = [] if a.show_wrong else None
            try: t,p=run(repo,files,gap,typer,wrongs=wrongs)
            except Exception as e:
                print(name,pathspec,gap,'ERR',e); failed = True; continue
            total_pairs += p
            ev=t['EV']
            if ev<50: print(f"### {name} {pathspec} gap={gap}: too few ({ev})"); continue
            print(f"\n### {name} {pathspec} gap={gap}  pairs={p}  oracle-confident anchors={ev}")
            print("   block types: "+" ".join(f"{k[3:]}={v}" for k,v in sorted(t.items()) if k.startswith('TY:')))
            for lab in ('naive','hard'):
                print(f"   {lab:<6} correct {100*t[lab+':correct']/ev:5.1f}%   LOUD-refusal {100*t[lab+':LOUD']/ev:5.1f}%   SILENT-WRONG {100*t[lab+':WRONG']/ev:5.2f}%  (n={t[lab+':WRONG']})"
                      + ("  by type: "+" ".join(f"{k.split(':')[2]}={v}" for k,v in sorted(t.items()) if k.startswith(lab+':WRONG:')) if t[lab+':WRONG'] else ""))
            for lab, st, ty, truth, f, ci, cj, q, got, want in (wrongs or []):
                print(f"   WRONG {lab} status={st} type={ty} oracle={truth} {f} {ci[:10]}..{cj[:10]}")
                print(f"     quote    {q[:160]!r}")
                print(f"     resolved {got if got is None else got[:160]!r}")
                print(f"     oracle   {want if want is None else want[:160]!r}")
        if total_pairs == 0:
            die(f"{name}: no version pair evaluated at any gap -- nothing was read", 2)
    if failed:
        sys.exit(1)


# ---------------------------------------------------------------- uniqueness
# Copied from e4_uniqueness.py's top-level loop. Changes: the corpus list, the
# file list, typer(text, b) for btype(content), and the unreadable-file count,
# which the original dropped silently and is printed here only when non-zero.

def cmd_uniqueness(a, corpora):
    blocks = D8.blocks
    typer = make_typer(a.frontmatter_type)
    MINLEN = a.minlen
    for name, repo, pathspec, files in corpora:
        per_file_dup=Counter(); corpus=Counter(); tot=Counter(); nfiles=0; unreadable=0
        texts = {}
        for f in files:
            try: t=open(os.path.join(repo,f),encoding='utf-8').read()
            except Exception: unreadable+=1; continue
            nfiles+=1; texts[f]=t
            bs=[b for b in blocks(t) if len(b['content'])>=MINLEN]
            c=Counter(b['content'] for b in bs)
            for b in bs:
                ty=typer(t,b); tot[ty]+=1
                if c[b['content']]>1: per_file_dup[ty]+=1
                corpus[b['content']]+=1
        cross=Counter()
        for f, t in texts.items():
            for b in blocks(t):
                if len(b['content'])>=MINLEN and corpus[b['content']]>1: cross[typer(t,b)]+=1
        print(f"\n### {name}  files={nfiles}  blocks>={MINLEN}ch={sum(tot.values())}")
        if unreadable:
            print(f"unreadable files skipped: {unreadable}")
        print(f"{'type':<9}{'n':>7}{'dup in same file':>19}{'dup anywhere in corpus':>25}")
        for ty in sorted(tot):
            n=tot[ty]
            print(f"{ty:<9}{n:>7}{per_file_dup[ty]:>10} ({100*per_file_dup[ty]/n:4.1f}%){cross[ty]:>14} ({100*cross[ty]/n:5.1f}%)")
        if nfiles == 0 or not tot:
            die(f"{name}: read {nfiles} files and {sum(tot.values())} blocks -- nothing measured")


# ---------------------------------------------------------------- selection census

def cmd_select(a, corpora, excluded_by):
    for name, repo, pathspec, files in corpora:
        ex = excluded_by[name]
        print(f"### {name}  pathspec={pathspec!r}  included={len(files)}  "
              f"excluded-as-generated={len(ex)}")
        if a.list:
            for f in files:
                print(f"  + {f}")
        for f in ex:
            print(f"  - {f}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("command", choices=("anchors", "uniqueness", "select"))
    ap.add_argument("--d8-dir", required=True,
                    help="kindspec/research experiments/D8-identity, unmodified")
    ap.add_argument("--corpus", nargs=4, action="append", required=True,
                    metavar=("NAME", "REPO", "PIN", "PATHSPEC"))
    ap.add_argument("--exclude-generated", action="store_true")
    ap.add_argument("--frontmatter-type", action="store_true")
    ap.add_argument("--minlen", type=int, default=20)
    ap.add_argument("--gaps", default="5,25")
    ap.add_argument("--show-wrong", action="store_true",
                    help="anchors: print every silent-wrong (quote, resolved, oracle)")
    ap.add_argument("--list", action="store_true", help="select: also list every included path")
    a = ap.parse_args()
    load_d8(a.d8_dir)
    corpora, excluded_by = [], {}
    for name, repo, pin, pathspec in a.corpus:
        check_corpus(name, repo, pin)
        files, excluded = select_files(name, repo, pathspec, a.exclude_generated)
        corpora.append((name, repo, pathspec, files))
        excluded_by[name] = excluded
    {"anchors": cmd_anchors, "uniqueness": cmd_uniqueness}.get(
        a.command, lambda a, c: cmd_select(a, c, excluded_by))(a, corpora)


if __name__ == "__main__":
    main()
