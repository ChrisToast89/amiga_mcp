# Portfolio banners (24 x 70 in)

Six vertical banners, 3600 x 10500 px at 150 ppi (24 x 70 inches), made in Photoshop 2026.

| File | Shows |
|---|---|
| `out/banner-amiga-68k` | Classic Amiga: Terra Strike plus 8 games |
| `out/banner-amigaos4-ppc` | AmigaOS 4.1 PPC: Planet Chomp (OSMesa), TrapezePDF, Python 3.12, network drivers, games |
| `out/banner-atari-st` | Atari ST / STE / Falcon ports |
| `out/banner-3do` | 3DO: the Arcade disc, demo and ports |
| `out/banner-four-machines` | Planet Chomp, Rolling Steel and Spectral Keep on 3DO, Amiga 68k, AmigaOS 4 and Atari Falcon |
| `out/banner-devbench` | The devbenches: Amiga DevBench, 3DO DevBench, Hatari agent tools |

Each has a layered `.psd` (one layer group per game; panels, shot frames, text glow and
shadows are live layer styles, text is editable) and a full-resolution `.jpg`.

Rebuild: `python3 build.py [banner-id ...]` (needs Photoshop 2026 running). `build.py` holds
the content (picks, crops, captions), lays the banner out, pre-scales the screenshots to
their placed size and paints the backdrop; `render.jsx` builds the PSD in Photoshop.
`--layout-only` writes `build/<id>/preview.png` without Photoshop.
