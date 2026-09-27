# Aggregate statistics over the included studies (the counts reported in the chapter).
import os, sys, json, collections, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *  # noqa

e = [r for r in json.load(open(W('extraction.json'))) if r['has_text']]
inc = [r for r in e if r['qa_total'] >= 3.0]
N = len(inc)
print(f'with full text: {len(e)} | included (score >= 3.0): {N} | excluded by quality: {len(e) - N}')
print('years:', sorted(collections.Counter(r['year'] for r in inc).items()))
print('study types:', collections.Counter(r['study_type'] for r in inc).most_common())
def dist(field, top=25):
    c = collections.Counter()
    for r in inc: c.update(r.get(field, []))
    print(f'--- {field.upper()} (share of the {N} included studies; multi-valued) ---')
    for k, v in c.most_common(top): print(f'  {k:38s} {v:4d}  {100 * v / N:5.1f}%')
for f in ['approaches', 'models', 'datasets', 'metrics', 'langs', 'domains', 'dbms']: dist(f)
print('--- quality checklist ---')
for q in ['QA1', 'QA2', 'QA3', 'QA4', 'QA5', 'QA6', 'QA7']:
    c = collections.Counter(r['qa'][q] for r in e)
    print(f'  {q}: yes={c[1.0]:3d} partial={c[0.5]:3d} no={c[0.0]:3d}')
print('mean score', round(statistics.mean(r['qa_total'] for r in inc), 2),
      '| median', statistics.median(r['qa_total'] for r in inc),
      '| >= 6.0:', sum(1 for r in inc if r['qa_total'] >= 6.0))
print('QA1 candidates (spatial extension, automatic):', sum(1 for r in inc if r["qa"]["QA1"] == 1.0),
      '-- each was verified manually; see README.')
