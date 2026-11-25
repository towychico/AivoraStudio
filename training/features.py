"""Referencia de extracción léxica ligera; espejo de engine/src/lib.rs."""
from collections import Counter
from math import sqrt
KEYWORDS=set(b'False None True and as assert async await break class continue def del elif else except finally for from global if import in is lambda nonlocal not or pass raise return try while with yield'.split())
OPS=[b'**=',b'//=',b'<<=',b'>>=',b'...',b'==',b'!=',b'<=',b'>=',b'**',b'//',b'<<',b'>>',b':=',b'->',b'+=',b'-=',b'*=',b'/=',b'%=',b'&=',b'|=',b'^=',b'@=']
def letter(x): return 65<=x<=90 or 97<=x<=122 or x==95 or x>=128
def digit(x): return 48<=x<=57
def represent(s):
    b=s.encode('utf-8'); n=len(b); i=0; t=[]; raw=[]; lines=[]; indent=[]; line=[]; start=True; level=0
    def finish():
        if line: lines.append(tuple(line)); indent.append(level)
        line.clear()
    while i<n:
        c=b[i]
        if c==10 or c==13:
            finish(); start=True; level=0; i+=1; continue
        if c in (32,9,12):
            if start: level+=4 if c==9 else 1
            i+=1; continue
        if c==35:
            while i<n and b[i] not in (10,13): i+=1
            continue
        start=False; j=i
        if c in (34,39):
            q=bytes([c]); delim=q*3 if b[i:i+3]==q*3 else q; i+=len(delim)
            while i<n:
                if b[i:i+len(delim)]==delim: i+=len(delim); break
                if b[i]==92: i=min(i+2,n)
                elif len(delim)==1 and b[i] in (10,13): break
                else: i+=1
            token=b'STRING'; r=token
        elif letter(c):
            i+=1
            while i<n and (letter(b[i]) or digit(b[i])): i+=1
            r=b[j:i]; token=r if r in KEYWORDS else b'IDENT'
        elif digit(c):
            i+=1
            while i<n and (digit(b[i]) or letter(b[i]) or b[i]==46): i+=1
            token=b'NUMBER'; r=token
        else:
            r=next((op for op in OPS if b.startswith(op,i)),bytes([c])); i+=len(r); token=r
        t.append(token); raw.append(r); line.append(token)
    finish()
    return t,raw,lines,indent,n

def cos(a,b):
    a,b=Counter(a),Counter(b); aa=sum(x*x for x in a.values()); bb=sum(x*x for x in b.values())
    return sum(v*b.get(k,0) for k,v in a.items())/sqrt(aa*bb) if aa and bb else 0.0

def jac(a,b):
    a,b=set(a),set(b); return len(a&b)/len(a|b) if a or b else 1.0

def grams(t,n): return [tuple(t[i:i+n]) for i in range(len(t)-n+1)]
def diff(a,b): return abs(a-b)/max(1,a,b)
NAMES=['token_cosine','bigram_cosine','trigram_cosine','token_jaccard','bigram_jaccard','raw_bigram_cosine','line_cosine','indent_cosine','byte_difference','token_difference','line_difference']
def features(a,b):
    t,r,l,i,n=a; u,s,m,j,o=b
    return [cos(t,u),cos(grams(t,2),grams(u,2)),cos(grams(t,3),grams(u,3)),jac(t,u),jac(grams(t,2),grams(u,2)),cos(grams(r,2),grams(s,2)),cos(l,m),cos(i,j),diff(n,o),diff(len(t),len(u)),diff(len(l),len(m))]
