# Systematic review: LLM-based text-to-SQL for geospatial data and Brazilian Portuguese.
# Author: Diego Lopes. Part of the pipeline documented in ../README.md.
# All paths are relative to the repository root; run the scripts from there.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *  # noqa: F401,F403
import re, glob, json, os

def strip_braces(s):
    s = s.strip()
    while s.startswith('{') and s.endswith('}'):
        s = s[1:-1].strip()
    if s.startswith('"') and s.endswith('"'):
        s = s[1:-1].strip()
    return s

def parse_bib(path):
    txt = open(path, encoding='utf-8', errors='replace').read()
    entries = []
    # find entry starts
    for m in re.finditer(r'@(\w+)\s*\{\s*([^,]+),', txt):
        etype, key = m.group(1), m.group(2).strip()
        # find matching closing brace
        i = m.end() - 1  # at the comma; go back to opening brace of entry
        ob = txt.index('{', m.start())
        depth = 0
        j = ob
        while j < len(txt):
            if txt[j] == '{': depth += 1
            elif txt[j] == '}':
                depth -= 1
                if depth == 0: break
            j += 1
        body = txt[m.end():j]
        fields = {}
        # naive field splitting respecting braces
        k = 0
        while k < len(body):
            fm = re.match(r'\s*(\w+)\s*=\s*', body[k:])
            if not fm:
                k += 1
                continue
            k += fm.end()
            name = fm.group(1).lower()
            if k < len(body) and body[k] == '{':
                d = 0; st = k
                while k < len(body):
                    if body[k] == '{': d += 1
                    elif body[k] == '}':
                        d -= 1
                        if d == 0:
                            k += 1; break
                    k += 1
                val = body[st:k]
            elif k < len(body) and body[k] == '"':
                st = k; k += 1
                while k < len(body) and body[k] != '"': k += 1
                k += 1
                val = body[st:k]
            else:
                st = k
                while k < len(body) and body[k] not in ',\n': k += 1
                val = body[st:k]
            fields[name] = strip_braces(val)
            # skip to next comma
            while k < len(body) and body[k] != ',': k += 1
            k += 1
        entries.append({'type': etype, 'key': key, 'source_file': os.path.basename(path), **fields})
    return entries

if __name__ == '__main__':
    all_e = []
    for f in sorted(glob.glob(os.path.join(BIBTEX_DIR, '*.bib'))):
        e = parse_bib(f)
        print(os.path.basename(f), len(e))
        all_e += e
    json.dump(all_e, open(W('bib_entries.json'),'w'), ensure_ascii=False)
    print('total', len(all_e))
    print(json.dumps(all_e[0], ensure_ascii=False)[:600])