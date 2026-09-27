# Systematic review: LLM-based text-to-SQL for geospatial data and Brazilian Portuguese.
# Author: Diego Lopes. Part of the pipeline documented in ../README.md.
# All paths are relative to the repository root; run the scripts from there.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *  # noqa: F401,F403
import json, re, glob, unicodedata, collections

def norm(t):
    t = unicodedata.normalize('NFKD', t or '')
    t = ''.join(c for c in t if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+', ' ', t.lower()).strip()

def clean_title(t):
    t = re.sub(r'<[^>]+>', ' ', t); t = re.sub(r'\$\$.*?\$\$', ' ', t)
    return re.sub(r';\s*\[.*$', '', t)

acc = json.load(open(W('accepted.json')))
texts = {f: norm(open(f, encoding='utf-8', errors='replace').read())
         for d in ['acm_papers','ieee_papers','science_direct','scopus','springer_link']
         for f in glob.glob(os.path.join(TXT_DIR, d, '*.txt'))}
byfile = collections.defaultdict(list)
for i, r in enumerate(acc):
    if r['pdf']: byfile[r['pdf']].append(i)

AFFIL = re.compile(r'\b(universit\w+|institut\w*|department|departamento|school of|laborator\w+|academy of|college of|corporation|research cent\w+)\b')
def score_occ(T, o):
    w = T[o:o+3500]
    has_abs = ' abstract ' in w
    affil = bool(AFFIL.search(T[o:o+900]))
    return (has_abs and affil, affil, has_abs, -o)

corpus, fixed = {}, 0
for f, idxs in byfile.items():
    T = texts[f]
    if len(T) <= 250000 and len(idxs) == 1:
        corpus[str(idxs[0])] = T; continue
    starts = {}
    for i in idxs:
        nt = norm(clean_title(acc[i]['title']))
        occ = [m.start() for m in re.finditer(re.escape(nt), T)] if len(nt) > 12 else []
        if not occ:
            toks = [w for w in nt.split() if len(w) > 3][:8]
            occ = [m.start() for m in re.finditer(re.escape(' '.join(toks)), T)] if toks else []
        starts[i] = max(occ, key=lambda o: score_occ(T, o)) if occ else (acc[i]['pdf_span'] or 0)
        if occ and starts[i] != min(occ): fixed += 1
    allstarts = sorted(set(starts.values()))
    for i, st in starts.items():
        nxt = [s for s in allstarts if s > st + 5000]
        end = min(nxt[0] if nxt else len(T), st + 130000)
        corpus[str(i)] = T[st:end]
print('corpus', len(corpus), '| occurrences relocated:', fixed)
print('short(<6k):', sum(1 for v in corpus.values() if len(v) < 6000))
json.dump(corpus, open(W('corpus.json'),'w'))