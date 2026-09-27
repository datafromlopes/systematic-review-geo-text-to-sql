# Export the per-study extraction table (one row per study with retrievable full text).
import os, sys, json, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *  # noqa

e = [r for r in json.load(open(W('extraction.json'))) if r['has_text']]
e.sort(key=lambda r: (r['year'], r['title']))
out = os.path.join(DATA_DIR, 'studies_extraction.csv')
cols = ['citation_key', 'title', 'year', 'venue', 'source', 'doi', 'study_type', 'included',
        'QA1', 'QA2', 'QA3', 'QA4', 'QA5', 'QA6', 'QA7', 'quality_score',
        'approaches', 'models', 'datasets', 'metrics', 'languages', 'dbms', 'domains']
with open(out, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(cols)
    for r in e:
        w.writerow([r['key'], r['title'], r['year'], str(r['venue'])[:120], r['source'], r['doi'],
                    r['study_type'], 'yes' if r['qa_total'] >= 3.0 else 'no',
                    *[r['qa'][q] for q in ['QA1', 'QA2', 'QA3', 'QA4', 'QA5', 'QA6', 'QA7']], r['qa_total'],
                    '; '.join(r['approaches']), '; '.join(r['models']), '; '.join(r['datasets']),
                    '; '.join(r['metrics']), '; '.join(r['langs']), '; '.join(r['dbms']),
                    '; '.join(r['domains'])])
print('rows written:', len(e), '->', out)
