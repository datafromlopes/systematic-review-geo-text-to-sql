# Systematic review: LLM-based text-to-SQL for geospatial data and Brazilian Portuguese.
# Author: Diego Lopes. Part of the pipeline documented in ../README.md.
# All paths are relative to the repository root; run the scripts from there.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *  # noqa: F401,F403
import json, re, glob, unicodedata, collections, os

def norm(t):
    t = unicodedata.normalize('NFKD', t or '')
    t = ''.join(c for c in t if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+', ' ', t.lower()).strip()

def clean_title(t):
    t = re.sub(r'<[^>]+>', ' ', t); t = re.sub(r'\$\$.*?\$\$', ' ', t)
    return re.sub(r';\s*\[.*$', '', t)

acc = json.load(open(W('accepted.json')))
for r in acc: r['pdf'] = None; r['pdf_span'] = None
SRC = {'ACM Digital Library':'acm_papers','IEEE Digital Library':'ieee_papers',
       'Science@Direct':'science_direct','Scopus':'scopus','Springer Link':'springer_link'}
texts = {f: norm(open(f, encoding='utf-8', errors='replace').read())
         for d in SRC.values() for f in glob.glob(os.path.join(TXT_DIR, d, '*.txt'))}
VOL = {f for f, t in texts.items() if len(t) > 250000}
print('proceedings volumes:', len(VOL))
HEAD = {f: t[:6000] for f, t in texts.items()}

taken = set()
def try_assign(i, files, mode):
    r = acc[i]; nt = norm(clean_title(r['title']))
    if len(nt) < 12: return False
    for f in files:
        if f in taken and f not in VOL: continue
        if mode == 'head':
            p = HEAD[f].find(nt)
            if p >= 0:
                r['pdf'], r['pdf_span'] = f, p; taken.add(f); return True
        else:  # volume full-text, prefer occurrence followed by 'abstract'
            occ = [m.start() for m in re.finditer(re.escape(nt), texts[f])]
            best = None
            for o in occ:
                sc = (1 if ' abstract ' in texts[f][o:o+2500] else 0, -o)
                if best is None or sc > best[0]: best = (sc, o)
            if best:
                r['pdf'], r['pdf_span'] = f, best[1]; taken.add(f); return True
    return False

order = lambda r: [SRC[r['source']]] + [v for v in SRC.values() if v != SRC[r['source']]]
# pass A: exact title in head, own source then others
for i, r in enumerate(acc):
    for d in order(r):
        fs = [f for f in texts if f.startswith(os.path.join(TXT_DIR, d) + os.sep) and f not in VOL]
        if try_assign(i, fs, 'head'): break
print('after A:', sum(1 for r in acc if r['pdf']))
# pass B: proceedings volumes
for i, r in enumerate(acc):
    if r['pdf']: continue
    try_assign(i, sorted(VOL), 'vol')
print('after B:', sum(1 for r in acc if r['pdf']))
# pass C: fuzzy on heads
free = [f for f in texts if f not in taken and f not in VOL]
cands = []
for i, r in enumerate(acc):
    if r['pdf']: continue
    toks = set(w for w in norm(clean_title(r['title'])).split() if len(w) > 3)
    if not toks: continue
    for f in free:
        sc = sum(1 for w in toks if w in HEAD[f]) / len(toks)
        if sc >= 0.9: cands.append((sc, i, f))
cands.sort(reverse=True)
ti, tf = set(), set()
for sc, i, f in cands:
    if i in ti or f in tf: continue
    acc[i]['pdf'], acc[i]['pdf_span'] = f, 0; ti.add(i); tf.add(f)
    print(f'  fuzzy {sc:.2f}', acc[i]['title'][:55], '=>', os.path.basename(f)[:45])
print('after C:', sum(1 for r in acc if r['pdf']), '/', len(acc))
for src in SRC:
    sub = [r for r in acc if r['source'] == src]
    print(' ', src, sum(1 for r in sub if r['pdf']), '/', len(sub))
json.dump(acc, open(W('accepted.json'),'w'), ensure_ascii=False)