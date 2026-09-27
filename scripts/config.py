"""Shared paths for the review pipeline (all relative to the repository root)."""
import os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(ROOT, 'data')
BIBTEX_DIR = os.path.join(DATA_DIR, 'bibtex_exports')      # raw exports of the five libraries
PARSIFAL_XLS = os.path.join(DATA_DIR, 'articles.xls')       # Parsifal export with the selection status
PDF_DIR = os.path.join(ROOT, 'papers')                       # full texts (not distributed)
TXT_DIR = os.path.join(ROOT, 'work', 'txt')                  # pdftotext output, one folder per source
WORK_DIR = os.path.join(ROOT, 'work')                        # intermediate JSON files
os.makedirs(WORK_DIR, exist_ok=True)
def W(name):
    return os.path.join(WORK_DIR, name)
