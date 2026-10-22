#!/bin/bash
# shot68k.sh OUT.png — capture the FS-UAE window (true colours, copper + sprites),
# title bar cropped off, scaled to 1024 wide.
set -e
T="$(cd "$(dirname "$0")" && pwd)"
id=$("$T/winid" fs-uae); [ "$id" != 0 ] || { echo "no FS-UAE window" >&2; exit 1; }
tmp=$(mktemp -t shot68k).png
screencapture -x -o -l "$id" "$tmp"
python3 - "$tmp" "$1" <<'PY'
import sys
from PIL import Image
im = Image.open(sys.argv[1]).convert("RGB"); w, h = im.size
bar = round(h * 28 / 800)          # macOS title bar (28 pt of an 800 pt window)
im = im.crop((0, bar, w, h)).resize((1024, round((h - bar) * 1024 / w)), Image.LANCZOS)
im.save(sys.argv[2]); print("saved", sys.argv[2], im.size)
PY
rm -f "$tmp"
