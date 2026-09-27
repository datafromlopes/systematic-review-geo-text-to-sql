# Systematic review: LLM-based text-to-SQL for geospatial data and Brazilian Portuguese.
# Author: Diego Lopes. Part of the pipeline documented in ../README.md.
# All paths are relative to the repository root; run the scripts from there.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *  # noqa: F401,F403
import xlrd, json, re, collections, unicodedata

def norm_title(t):
    t = unicodedata.normalize('NFKD', t or '')
    t = ''.join(c for c in t if not unicodedata.combining(c))
    t = t.lower()
    t = re.sub(r'[^a-z0-9]+', ' ', t).strip()
    return t

def norm_doi(d):
    d = (d or '').strip().lower()
    d = re.sub(r'^https?://(dx\.)?doi\.org/', '', d)
    d = re.sub(r'^doi:\s*', '', d)
    return d.strip()

wb = xlrd.open_workbook(PARSIFAL_XLS)
s = wb.sheet_by_index(0)
hdr = [c.value for c in s.row(0)]
rows = [dict(zip(hdr, [c.value for c in s.row(r)])) for r in range(1, s.nrows)]
for r in rows:
    r['year'] = str(r['year']).split('.')[0]

bib = json.load(open(W('bib_entries.json')))
by_doi = {}
by_title = {}
for b in bib:
    d = norm_doi(b.get('doi',''))
    if d: by_doi.setdefault(d, b)
    t = norm_title(b.get('title',''))
    if t: by_title.setdefault(t, b)

acc = [r for r in rows if r['status'] == 'Accepted']
matched = 0
for r in acc:
    d = norm_doi(r.get('doi',''))
    b = by_doi.get(d) or by_title.get(norm_title(r['title']))
    if b:
        r['bib'] = b
        matched += 1
    else:
        r['bib'] = None
print('accepted', len(acc), 'matched to bib', matched)
unm = [r for r in acc if not r['bib']]
for r in unm[:10]:
    print('UNMATCHED:', r['source'], '|', r['title'][:80], '|', r['doi'][:50])
json.dump(acc, open(W('accepted.json'),'w'), ensure_ascii=False)
json.dump(rows, open(W('all_rows.json'),'w'), ensure_ascii=False)