#!/bin/bash
# shotos4.sh OUT.png — QEMU HMP screendump of the OS4 guest's display (1280x720).
set -e
tmp=$(mktemp -t shotos4).ppm; rm -f "$tmp"
printf 'screendump %s\n' "$tmp" | nc -w 2 127.0.0.1 2348 >/dev/null
for _ in 1 2 3 4 5 6 7 8 9 10; do [ -s "$tmp" ] && break; sleep 0.3; done
python3 -c "import sys; from PIL import Image; Image.open(sys.argv[1]).convert('RGB').save(sys.argv[2]); print('saved', sys.argv[2])" "$tmp" "$1"
rm -f "$tmp"
