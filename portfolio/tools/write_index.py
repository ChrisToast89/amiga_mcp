#!/usr/bin/env python3
"""write_index.py — regenerate portfolio/README.md from the per-entry markdown files."""
import glob, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def entry(md):
    txt = open(md).read()
    title = txt.splitlines()[0].lstrip("# ").strip()
    typ = (re.search(r"\*\*Type:\*\* ([a-z ]+)", txt) or [None, ""])[1].strip()
    paras = [p for p in txt.split("\n\n")[1:] if p.strip() and not p.startswith(("**", "#", "!"))]
    blurb = re.split(r"(?<=[.!?])\s", paras[0].replace("\n", " "))[0] if paras else ""
    imgs = re.findall(r"!\[[^\]]*\]\(([^)]+\.png)\)", txt)
    pick = next((i for i in imgs if "gameplay" in i), imgs[0] if imgs else None)
    d = os.path.relpath(os.path.dirname(md), ROOT)
    return title, typ, blurb, d, os.path.basename(md), pick, len(imgs)

def table(section):
    rows = ["| | Program | Type | About |", "|---|---|---|---|"]
    es = sorted((entry(m) for m in glob.glob(f"{ROOT}/{section}/*/*.md") if m.split("/")[-2] not in ("tools", "devbench")), key=lambda e: (e[1] != "game", e[0].lower()))
    for t, typ, blurb, d, md, img, n in es:
        thumb = f'<img src="{d}/{img}" width="200">' if img else ""
        rows.append(f"| {thumb} | [{t}]({d}/{md}) | {typ} | {blurb} ({n} image{'s' if n != 1 else ''}) |")
    return "\n".join(rows), len(es)

t68, n68 = table("amiga-68k"); tppc, nppc = table("amigaos4-ppc")
tst, nst = table("atari-st"); t3do, n3do = table("3do")
dev = sorted(glob.glob(f"{ROOT}/devbench/*.md"))
devrows = "\n".join(f"- [{open(m).readline().lstrip('# ').strip()}](devbench/{os.path.basename(m)})"
                    for m in dev if not m.endswith("README.md"))
open(f"{ROOT}/README.md", "w").write(f"""# Amiga DevBench portfolio

Screenshots and write-ups of everything built with Amiga DevBench, captured from the real
emulators: classic 68k AmigaOS 3.x on FS-UAE (AmiKit), AmigaOS 4.1 PowerPC on QEMU sam460ex,
and the sister projects' Atari ST/STE/Falcon (Hatari) and 3DO (Opera) ports.
Each program has its own folder with its PNGs and one markdown file describing every image.
Captured 2026-10-20.

- [Classic Amiga 68k](#classic-amiga-68k) — {n68} programs
- [AmigaOS 4.1 PowerPC](#amigaos-41-powerpc) — {nppc} entries
- [DevBench web UI](devbench/README.md) — {len(dev) - 1} screens, each plain and annotated
- [Atari ST / STE / Falcon ports](atari-st/README.md) — {nst} entries (Hatari), plus annotated agent tooling
- [3DO ports](3do/README.md) — {n3do} entries (Opera), plus the [3DO devbench](3do/devbench/README.md), annotated

## Classic Amiga 68k

{t68}

Not captured: `aga3d` and `ham_raster` (both fail to open their 8-bit LORES screen on this AmiKit setup).

## AmigaOS 4.1 PowerPC

{tppc}

## Atari ST / STE / Falcon

Sister project: the same games ported to the Atari through Amiga-API shim layers, run on a patched Hatari with an agent API. See [atari-st/README.md](atari-st/README.md) and [atari-st/tools](atari-st/tools/README.md).

{tst}

## 3DO

Sister project: the games on the 3DO Interactive Multiplayer (ARM60, Portfolio OS), run on a patched, scriptable Opera emulator with its own devbench. See [3do/README.md](3do/README.md) and [3do/devbench](3do/devbench/README.md).

{t3do}

## DevBench web UI

The host side: web UI + MCP server that builds, deploys, launches, logs, inspects and drives
both emulators. See [devbench/README.md](devbench/README.md).

{devrows}

## How these were captured

`tools/` holds the capture scripts: `shot68k.sh` (FS-UAE window grab, true colour incl. copper
and sprites), `shotos4.sh` (QEMU HMP screendump), `mcp.py` (DevBench MCP calls to launch
programs and inject keys), `capture_devbench.py` + `annotate.py` (headless-Chrome web UI shots
and callout rendering), `write_index.py` (this page).
""")
print("README.md written:", n68, nppc, len(dev) - 1)
