# Systematic review: LLM-based text-to-SQL for geospatial data and Brazilian Portuguese.
# Author: Diego Lopes. Part of the pipeline documented in ../README.md.
# All paths are relative to the repository root; run the scripts from there.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *  # noqa: F401,F403
import json, re

acc = json.load(open(W('accepted.json')))
ext = {r['idx']: r for r in json.load(open(W('extraction.json')))}

# idx -> final citation key. Keys already present in bibliografia-dissertacao.bib are reused.
EXISTING = {72:'Nascimento2025-sc', 248:'10.1007/978-3-031-68309-1_8', 299:'gao2023texttosqlempoweredlargelanguage',
            412:'GS-SQL', 237:'mRAT-SQL-GAP', 320:'nan-etal-2023-enhancing', 293:'EnhancingText2SQLFinancial'}
RENAME = {233:'Jose2022278', 68:'Jose2023015', 360:'Aktas2026155', 369:'Fuerst2024158'}

CITED = [
 # geospatial
 243, 412, 13, 168, 281, 384, 34, 280, 362, 423, 86,
 # real-world databases
 154, 415, 72, 248, 167, 211, 192, 369, 209, 70, 181, 141, 48, 366, 328, 377, 97,
 # datasets and benchmarks
 190, 308, 246, 150, 271, 383, 304, 25, 340, 299, 164,
 # multilingual / portuguese
 237, 233, 68, 80, 411, 5, 187, 344, 55, 360, 401, 406, 421, 37, 54, 205, 331, 336, 278, 105, 409, 375,
 # fine-tuning and compact models
 419, 115, 408, 291, 252, 3, 326, 179, 405, 144, 253,
 # surveys / other
 204, 267,
]
DROP = {'abstract','keywords','author_keywords','affiliations','affiliation','correspondence_address',
        'source','document_type','language','abbrev_source_title','publication_stage','open_access',
        'funding_details','funding_text 1','funding_text 2','coden','pubmed_id','art_number','type',
        'issue_date','numpages','location','series','note','month','chemicals_cas','tradenames',
        'manufacturers','references','editor','isbn'}
ORDER = ['author','title','year','journal','booktitle','volume','number','pages','articleno',
         'publisher','address','doi','url','issn']

def esc(v):
    v = v.replace('\n', ' ')
    v = re.sub(r'<[^>]+>', '', v)
    v = re.sub(r'\$\$[^$]*\$\$', '', v)
    v = re.sub(r';\s*\[.*$', '', v)
    v = re.sub(r'\s+', ' ', v)
    return v.strip()

seen, out = set(), []
for idx in CITED:
    b = acc[idx]['bib']
    key = EXISTING.get(idx) or RENAME.get(idx) or b['key']
    if idx in EXISTING:      # already in the dissertation bibliography: do not duplicate
        continue
    if key in seen:
        print('DUPLICATE KEY', key, idx); continue
    seen.add(key)
    fields = {k: esc(v) for k, v in b.items()
              if k not in DROP and k not in ('type','key','source_file') and isinstance(v, str) and v.strip()}
    etype = b['type'].lower()
    etype = {'inproceedings':'InProceedings','article':'Article','incollection':'InCollection',
             'book':'Book','misc':'Misc','conference':'InProceedings'}.get(etype, 'Article')
    lines = [f'@{etype}{{{key},']
    for f in ORDER:
        if f in fields:
            lines.append(f'  {f} = {{{fields[f]}}},')
    lines[-1] = lines[-1].rstrip(',')
    lines.append('}')
    out.append('\n'.join(lines))

hdr = ('% Supplementary bibliography for Chapter 3 (Systematic Literature Review).\n'
       '% Entries were taken verbatim from the raw exports in papers_bibtex/ and reduced to the\n'
       '% fields needed for citation. Studies already present in bibliografia-dissertacao.bib\n'
       '% (Nascimento2025-sc, 10.1007/978-3-031-68309-1_8, gao2023texttosqlempoweredlargelanguage,\n'
       '% GS-SQL, mRAT-SQL-GAP, nan-etal-2023-enhancing, EnhancingText2SQLFinancial) are NOT repeated here.\n\n')
open(os.path.join(DATA_DIR, 'references_included_studies.bib'),'w').write(hdr + '\n\n'.join(out) + '\n')
print('entries written:', len(out))
print('keys:', sorted(seen))