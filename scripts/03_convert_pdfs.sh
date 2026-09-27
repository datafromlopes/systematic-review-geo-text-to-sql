#!/usr/bin/env bash
# Convert every downloaded full text to plain text with pdftotext (poppler), keeping the
# layout. Input: papers/<source>/*.pdf  Output: work/txt/<source>/*.txt
set -euo pipefail
cd "$(dirname "$0")/.."
for src in acm_papers ieee_papers science_direct scopus springer_link; do
  mkdir -p "work/txt/$src"
  for pdf in papers/$src/*.pdf; do
    [ -e "$pdf" ] || continue
    out="work/txt/$src/$(basename "${pdf%.pdf}").txt"
    [ -s "$out" ] || pdftotext -layout "$pdf" "$out" || echo "FAILED: $pdf" >&2
  done
  echo "$src: $(ls work/txt/$src | wc -l) text files"
done
