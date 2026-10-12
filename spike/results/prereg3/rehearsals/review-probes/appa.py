import hashlib,sys
t=open(sys.argv[1],encoding='utf-8').read()
a=t.index("## Appendix A — the tierer's prompt, verbatim"); b=t.index("## Appendix B",a)
s=t[a:b].rstrip("\n")+"\n"
lines=[ln for ln in s.splitlines() if ln.startswith(">")]
p="\n".join(ln[2:] if ln.startswith("> ") else ln[1:] for ln in lines)+"\n"
print(hashlib.sha256(p.encode()).hexdigest())
