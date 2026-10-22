#!/usr/bin/env python3
"""build.py - lay out the 24 x 70 inch portfolio banners and render them in Photoshop.

  build.py                 all banners
  build.py amiga-68k ...   just these (ids from BANNERS below)
  build.py --layout-only   write layouts + assets + a PIL preview, skip Photoshop

For each banner: pre-scales every screenshot to its exact placed size (so Photoshop
places pixels 1:1), paints the backdrop (gradient, glow, perspective grid, scanlines),
measures and wraps all text with the same fonts Photoshop uses, writes
build/<id>/layout.json, then runs render.jsx in Photoshop, which builds a layered PSD
(one group per game: panel, framed shots, text, all with live layer styles) and a
full-resolution JPEG. Output: banners/out/<id>.psd and <id>.jpg.
"""
import json, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.dirname(HERE)                         # portfolio/
BUILD, OUT = os.path.join(HERE, "build"), os.path.join(HERE, "out")
DPI, W, H = 150, 24 * 150, 70 * 150               # 3600 x 10500
M = 180                                           # side margin
GAP = 100                                         # gap between cards
PAD = 70                                          # card padding

FONTS = {  # Photoshop postscript name -> (file, ttc index) for measuring
    "Futura-CondensedExtraBold": ("/System/Library/Fonts/Supplemental/Futura.ttc", 4),
    "AvenirNext-Medium": ("/System/Library/Fonts/Avenir Next.ttc", 5),
    "AvenirNext-DemiBold": ("/System/Library/Fonts/Avenir Next.ttc", 2),
    "AvenirNext-Bold": ("/System/Library/Fonts/Avenir Next.ttc", 0),
    "DINCondensed-Bold": ("/System/Library/Fonts/Supplemental/DIN Condensed Bold.ttf", 0),
}
TITLE, BODY, BODY_B, TAG = "Futura-CondensedExtraBold", "AvenirNext-Medium", "AvenirNext-DemiBold", "DINCondensed-Bold"
_fc = {}


def font(name, size):
    k = (name, size)
    if k not in _fc:
        f, i = FONTS[name]
        _fc[k] = ImageFont.truetype(f, size, index=i)
    return _fc[k]


def text_w(s, name, size, tracking=0):
    return font(name, size).getlength(s) + tracking / 1000 * size * max(len(s) - 1, 0)


def wrap(s, name, size, width):
    lines, cur = [], ""
    for word in s.split():
        t = (cur + " " + word).strip()
        if text_w(t, name, size) <= width or not cur:
            cur = t
        else:
            lines.append(cur); cur = word
    if cur:
        lines.append(cur)
    return lines


def cap_h(name, size):
    b = font(name, size).getbbox("H", anchor="ls")
    return -b[1]


# ---------------------------------------------------------------- content
A68, OS4, ST, TDO = "amiga-68k", "amigaos4-ppc", "atari-st", "3do"


def img(path, crop=None):
    return {"path": os.path.join(P, path), "crop": crop}


def g(section, name, file):
    return img(f"{section}/{name}/{name}-{file}.png")


BANNERS = {
    "amiga-68k": dict(
        title="CLASSIC AMIGA", accent="#ff8a3d", accent2="#ff3d7f",
        kicker="BUILT WITH AMIGA DEVBENCH  +  CLAUDE CODE",
        subtitle="Games in C for the 68000 Amiga, cross-compiled in Docker, deployed, run, tested and debugged live through the AmigaBridge.",
        chips=["MC68020", "AGA CHIPSET", "PAULA AUDIO", "AMIGAOS 3.X", "FS-UAE"],
        hero=dict(name="Terra Strike", tag="68020 · AGA · 3D", images=[g(A68, "terra_strike", "title"), g(A68, "terra_strike", "gameplay-3"), g(A68, "terra_strike", "gameplay")],
                  caption="A Zarch-style landscape shooter over a wrapping fractal island: lift off, destroy tanks, buildings and ships, land to refuel. Fixed-point 3D with a CPU span filler, built and debugged live through DevBench."),
        cards=[
            dict(name="Planet Chomp", tag="68020 · SOFTWARE 3D", main=g(A68, "planet_chomp_68k", "gameplay"), inset=g(A68, "planet_chomp_68k", "title"),
                 caption="A maze that wraps all the way round a tiny planet. Runs the 3DO version's game code unchanged."),
            dict(name="Rolling Steel", tag="68020 · SOFTWARE 3D", main=g(A68, "rolling_steel_68k", "gameplay"), inset=g(A68, "rolling_steel_68k", "title"),
                 caption="Marble racing over six 3D courses against one clock, drawn by a depth-buffered software rasteriser."),
            dict(name="Spectral Keep", tag="ISOMETRIC ADVENTURE", main=g(A68, "spectral_keep", "gameplay"), inset=g(A68, "spectral_keep", "title"),
                 caption="Knight Lore-style flip-screen keeps: three keeps, 24 rooms, carry the relics to the throne."),
            dict(name="Nova Defense", tag="ARCADE SHOOTER", main=g(A68, "nova_defense", "gameplay"), inset=g(A68, "nova_defense", "title"),
                 caption="48 aliens in staggered rows, crystal shields and a passing comet."),
            dict(name="Frank the Frog", tag="PAULA METAL SOUNDTRACK", main=g(A68, "frank_the_frog", "gameplay"), inset=g(A68, "frank_the_frog", "title"),
                 caption="Hop the traffic, ride the river to the ponds, to a heavy-metal track generated in code."),
            dict(name="Jump Quest", tag="PLATFORMER", main=g(A68, "jump_quest", "gameplay"), inset=g(A68, "jump_quest", "title"),
                 caption="RJ and Dale's platformer: three levels, one or two players, chiptunes on Paula."),
            dict(name="Dot Chase", tag="MAZE ARCADE", main=g(A68, "dot_chase", "gameplay"), inset=g(A68, "dot_chase", "title"),
                 caption="A ladybug gathers seeds in a hedge maze while four spiders hunt it."),
            dict(name="Uranus Lander", tag="PROTRACKER MUSIC", main=g(A68, "uranus_lander", "gameplay"), inset=g(A68, "uranus_lander", "title"),
                 caption="Rotate, thrust and land on the pads of Uranus before the fuel runs out."),
        ],
        footer="github.com/geekychris/amiga_games   ·   captured live on FS-UAE"),

    "amigaos4-ppc": dict(
        title="AMIGAOS 4.1", accent="#3dc8ff", accent2="#8a5cff",
        kicker="POWERPC  ·  BUILT WITH AMIGA DEVBENCH  +  CLAUDE CODE",
        subtitle="Games, apps, a Python port and network drivers for AmigaOS 4.1 on PowerPC, cross-compiled with GCC 11 and run on QEMU's sam460ex.",
        chips=["POWERPC 460EX", "AMIGAOS 4.1 FE", "OSMESA 3D", "SANA-II", "QEMU SAM460EX"],
        hero=dict(name="Planet Chomp", tag="PERSPECTIVE 3D · SOFTWARE MESA", images=[img(f"{OS4}/planet_chomp/planet_chomp-title.png", (0, 33, 650, 580)), g(OS4, "planet_chomp", "gameplay")],
                  caption="Real perspective 3D with no 3D hardware: rendered through software Mesa (OSMesa), since QEMU's SM502 has no Warp3D driver."),
        cards=[
            dict(name="TrapezePDF", tag="NATIVE PDF VIEWER", main=img(f"{OS4}/trapezepdf/trapezepdf-page.png", (0, 30, 800, 632)),
                 inset=img(f"{OS4}/trapezepdf/trapezepdf-sticky-note-dialog.png", (0, 30, 800, 632)),
                 caption="MuPDF-based viewer: zoom, rotate, sticky notes, forms, HTTPS URLs and PostScript printing."),
            dict(name="Python 3.12", tag="CPYTHON PORT", main=img(f"{OS4}/python-os4/python-os4-shell.png", (61, 43, 1059, 420)),
                 inset=img(f"{OS4}/python-os4/python-os4-sysmon.png", (140, 90, 650, 406)),
                 caption="CPython 3.12.7 as one static PPC executable: sockets, threads, SQLite and native Intuition GUIs."),
            dict(name="Network drivers", tag="SANA-II · VIRTIO-NET", main=img(f"{OS4}/networking/networking-netsurf-over-e1000.png", (0, 30, 1100, 500)),
                 inset=img(f"{OS4}/networking/networking-virtnet-iperf3.png", (16, 224, 1256, 700)),
                 caption="A from-scratch virtio-net SANA-II driver, a loopback device and an iperf3 client for OS4."),
            dict(name="Rolling Steel", tag="OSMESA · 47 FPS", main=g(OS4, "rolling_steel", "gameplay"), inset=img(f"{OS4}/rolling_steel/rolling_steel-title.png", (0, 33, 650, 548)),
                 caption="Six courses, one clock: orthographic 3D faces with a depth buffer through OSMesa."),
            dict(name="Organizer", tag="NOTES · TASKS · CALENDAR", main=img(f"{OS4}/organizer/organizer-calendar.png", (0, 12, 645, 432)),
                 inset=img(f"{OS4}/python-os4/python-os4-planner.png", (100, 40, 690, 456)),
                 caption="Notes, tasks and a calendar, scriptable from the host through bridge hooks. Inset: the Python planner."),
            dict(name="Spectral Keep", tag="ISOMETRIC ADVENTURE", main=g(OS4, "spectral_keep", "gameplay"), inset=img(f"{OS4}/spectral_keep/spectral_keep-title.png", (0, 33, 648, 548)),
                 caption="Three keeps, 24 rooms: carry the relics to the throne."),
            dict(name="Canyon Rescue", tag="VOXEL FLIGHT", main=g(OS4, "canyon_rescue", "gameplay"), inset=g(OS4, "canyon_rescue", "title"),
                 caption="Fly the fractal valleys and rescue downed pilots, but watch for Mimics."),
            dict(name="Void Trader", tag="3D SPACE TRADING", main=g(OS4, "void_trader", "gameplay"), inset=g(OS4, "void_trader", "title"),
                 caption="Elite-style flat-shaded 3D: fight pirates, trade cargo, earn 5000 credits."),
        ],
        footer="github.com/geekychris   ·   captured live on QEMU sam460ex"),

    "atari-st": dict(
        title="ATARI ST · FALCON", accent="#ff4b4b", accent2="#ffb000",
        kicker="SISTER PROJECT  ·  THE SAME GAMES ON THE ATARI",
        subtitle="The Amiga games ported to the Atari ST, STE and Falcon through layers that emulate the Amiga graphics API, Paula sound and AmigaDOS, run on a scriptable Hatari.",
        chips=["ST", "STE", "FALCON030", "68060 CT60", "HATARI AGENT API"],
        hero=dict(name="Planet Chomp", tag="FALCON + 68060 (CT60)", images=[g(ST, "planet_chomp", "title"), g(ST, "planet_chomp", "gameplay"), g(ST, "planet_chomp", "gameplay-2")],
                  caption="The sphere-wrapped maze chase on an accelerated Falcon: the 3DO game code runs unmodified on the falcon_3do layer."),
        cards=[
            dict(name="Rolling Steel", tag="FALCON + 68060 (CT60)", main=g(ST, "rolling_steel", "gameplay"), inset=g(ST, "rolling_steel", "title"),
                 caption="Software-rasterised 3D marble racing with a depth buffer; game, physics and courses unmodified."),
            dict(name="Spectral Keep", tag="FALCON030", main=g(ST, "spectral_keep", "gameplay"), inset=g(ST, "spectral_keep", "title"),
                 caption="The isometric keeps on the Falcon's true-colour screen."),
            dict(name="Canyon Rescue", tag="FALCON030", main=g(ST, "canyon_rescue", "gameplay-2"), inset=g(ST, "canyon_rescue", "title"),
                 caption="320x240 in 16-bit colour; the game loop is copied verbatim from the Amiga original."),
            dict(name="RJ's Birthday Bash", tag="STE", main=g(ST, "rj_birthday", "gameplay"), inset=g(ST, "rj_birthday", "title"),
                 caption="A party-management arcade game for RJ Mical's 70th: six themed rooms of RJ's house."),
            dict(name="Lunar Rider", tag="STE · BLITTER SCROLLING", main=g(ST, "lunar_rider", "gameplay-2"), inset=g(ST, "lunar_rider", "title"),
                 caption="Jump craters, shoot rocks; mountain layers scrolled by the STE blitter."),
            dict(name="Orb Hunter", tag="STE", main=g(ST, "orb_hunter", "gameplay"), inset=g(ST, "orb_hunter", "title"),
                 caption="Cavern exploration with power-ups and bosses; music on the Paula emulation."),
            dict(name="Nova Defense", tag="ST · PLAYED BY ITS BOT", main=g(ST, "nova_defense", "gameplay"), inset=g(ST, "nova_defense", "title"),
                 caption="Captured while the game's own bot played, driven through the Hatari agent API."),
            dict(name="ST Launcher", tag="ON-ATARI MENU", main=img(f"{ST}/st_launcher/st_launcher-3.png"), inset=img(f"{ST}/st_launcher/st_launcher-1.png"),
                 caption="Every port on one C: drive, with thumbnails, descriptions and controls."),
        ],
        footer="github.com/geekychris/atari_st_games   ·   captured live on Hatari"),

    "3do": dict(
        title="3DO", accent="#ffd23d", accent2="#ff5a3d",
        kicker="SISTER PROJECT  ·  HOMEBREW FOR THE 3DO INTERACTIVE MULTIPLAYER",
        subtitle="C89 for the ARM60 and Portfolio OS: MADAM cels, fixed-point maths, an Amiga compatibility layer, and a patched Opera emulator with its own DevBench and MCP.",
        chips=["ARM60 12.5 MHZ", "PORTFOLIO OS", "MADAM CELS", "OPERA EMULATOR", "MCP"],
        hero=dict(name="3DO Arcade", tag="EVERY GAME ON ONE DISC", images=[img(f"{TDO}/arcade/arcade-menu.png"), img(f"{TDO}/arcade/arcade-game.png"), img(f"{TDO}/demo/demo-2.png")],
                  caption="A game selector that bundles every Amiga-layer game on one CD, plus a cel-engine demo written from scratch for the 3DO."),
        cards=[
            dict(name="Planet Chomp", tag="UNITY › 3DO REWRITE", main=g(TDO, "planet_chomp", "gameplay"), inset=g(TDO, "planet_chomp", "title"),
                 caption="The cube-sphere maze chase, rewritten from a Unity game for the 3DO."),
            dict(name="Rolling Steel", tag="SPLIT-SCREEN 2P", main=g(TDO, "rolling_steel", "gameplay"), inset=g(TDO, "rolling_steel", "twoplayer"),
                 caption="Courses built from the Unity game's own files; a spinning marble with real friction."),
            dict(name="Spectral Keep", tag="Q12 FIXED POINT", main=g(TDO, "spectral_keep", "gameplay-2"), inset=g(TDO, "spectral_keep", "title"),
                 caption="Characters pre-rendered at startup by a small z-buffered rasteriser, 8 facings."),
            dict(name="Void Trader", tag="FILLED 3D WITH CELS", main=g(TDO, "void_trader", "gameplay-2"), inset=g(TDO, "void_trader", "title"),
                 caption="Every shaded triangle is a one-texel MADAM cel mapped onto a quad."),
            dict(name="Orb Hunter", tag="AMIGA CODE, UNCHANGED", main=g(TDO, "orb_hunter", "gameplay-3"), inset=g(TDO, "orb_hunter", "title"),
                 caption="The Amiga game and drawing code runs unchanged through the sdk/amiga layer."),
            dict(name="Jump Quest", tag="AMIGA PORT", main=g(TDO, "jump_quest", "gameplay"), inset=g(TDO, "jump_quest", "title"),
                 caption="graphics.library calls drawn into an offscreen buffer, shown each frame as a cel."),
            dict(name="Canyon Rescue", tag="AMIGA PORT", main=g(TDO, "canyon_rescue", "gameplay"), inset=g(TDO, "canyon_rescue", "title"),
                 caption="Voxel valleys and Mimic pilots, on the 3DO."),
            dict(name="Nova Defense", tag="AMIGA PORT", main=g(TDO, "nova_defense", "gameplay"), inset=g(TDO, "nova_defense", "title"),
                 caption="The alien shooter on the 3DO control pad."),
        ],
        footer="github.com/geekychris/3do-dev   ·   captured live on Opera"),
}

# one game, four machines
FOUR = dict(
    title="ONE GAME · FOUR MACHINES", accent="#b46bff", accent2="#3dc8ff",
    kicker="UNITY  ›  3DO  ›  AMIGA  ·  AMIGAOS 4  ·  ATARI FALCON",
    subtitle="Three Unity games rewritten in C for the 3DO. The same game code then runs on the 68k Amiga, on AmigaOS 4 PowerPC and on the Atari Falcon.",
    chips=["3DO", "AMIGA 68K", "AMIGAOS 4 PPC", "ATARI FALCON"],
    platforms=[("3DO", "#ffd23d"), ("AMIGA 68K", "#ff8a3d"), ("AMIGAOS 4 PPC", "#3dc8ff"), ("ATARI FALCON", "#ff4b4b")],
    games=[
        dict(name="Planet Chomp", caption="A maze that wraps all the way round a tiny planet. Software cels on 68k, OSMesa on OS4, a 68060 Falcon.",
             images=[g(TDO, "planet_chomp", "gameplay"), g(A68, "planet_chomp_68k", "gameplay"), g(OS4, "planet_chomp", "gameplay"), g(ST, "planet_chomp", "gameplay")]),
        dict(name="Rolling Steel", caption="Six floating courses against one clock: the same physics and courses on every machine.",
             images=[g(TDO, "rolling_steel", "gameplay"), g(A68, "rolling_steel_68k", "gameplay"), g(OS4, "rolling_steel", "gameplay"), g(ST, "rolling_steel", "gameplay")]),
        dict(name="Spectral Keep", caption="Knight Lore-style isometric keeps, from the 3DO's Q12 fixed point to a Falcon030.",
             images=[g(TDO, "spectral_keep", "gameplay"), g(A68, "spectral_keep", "gameplay"), g(OS4, "spectral_keep", "gameplay"), g(ST, "spectral_keep", "gameplay")]),
    ],
    footer="github.com/geekychris   ·   3DO on Opera · 68k on FS-UAE · OS4 on QEMU · Falcon on Hatari")

DEVB = dict(
    title="THE DEVBENCHES", accent="#39e0a0", accent2="#3dc8ff",
    kicker="HOW IT WAS BUILT  ·  EMULATORS AN AI AGENT CAN DRIVE",
    subtitle="Each machine gets a host-side bench: build, deploy, launch, log, inspect memory and chips, inject input and debug, from a web UI or over MCP from Claude Code.",
    chips=["MCP", "WEB UI", "AMIGABRIDGE", "HATARI AGENT API", "OPERA HARNESS"],
    hero=dict(name="Amiga DevBench", tag="AMIGAOS 4 · CLASSIC 68K", images=[img("devbench/os4-dashboard.png"), img("devbench/68k-inspect-graphics.png")],
              caption="Dashboard with bridge tri-state, heartbeat, clients and the daemon's command set; the 68k Inspect view with the live palette, copper list and sprites."),
    cards=[
        dict(name="MCP traffic", tag="AMIGA DEVBENCH", main=img("devbench/os4-settings-traffic.png"), inset=None,
             caption="Every MCP call Claude makes, with its request and response."),
        dict(name="Chip-level debug", tag="AMIGA DEVBENCH · 68K", main=img("devbench/68k-inspect-debug.png", (0, 0, 3200, 2000)), inset=None,
             caption="ROM disassembly, decoded custom-chip registers and Paula channels."),
        dict(name="Live logs", tag="AMIGA DEVBENCH · AMIGAOS 4", main=img("devbench/os4-logs.png"), inset=None,
             caption="Bridge clients' log lines with MCP calls and replies, live and filterable."),
        dict(name="Snapshot diff", tag="3DO DEVBENCH", main=img("3do/devbench/os-snapshots.png", (0, 0, 2880, 1800)), inset=None,
             caption="Snapshot Portfolio OS, play, then diff: leaked items and CPU per task."),
        dict(name="3DO DevBench", tag="OPERA HARNESS", main=img("3do/devbench/debug.png", (0, 0, 2880, 1800)), inset=None,
             caption="Stopped at a breakpoint, with SWI snoop and the profiler."),
        dict(name="3DO OS view", tag="PORTFOLIO OS INTROSPECTION", main=img("3do/devbench/os-tasks.png", (0, 0, 2880, 1800)), inset=None,
             caption="Portfolio OS tasks, read straight from emulated RAM."),
        dict(name="Hatari agent console", tag="ATARI", main=img("atari-st/tools/agent-console-debugger.png"), inset=None,
             caption="The agent console's debugger tab with the CPU stopped."),
        dict(name="Game launcher", tag="ATARI · HOST SIDE", main=img("atari-st/tools/game-launcher.png"), inset=None,
             caption="The host-side launcher reading games.ini."),
    ],
    footer="github.com/geekychris   ·   amiga_mcp · hatari_augmented · 3do-dev")

ALL = ["amiga-68k", "amigaos4-ppc", "atari-st", "3do", "four-machines", "devbench"]


# ---------------------------------------------------------------- assets
def hexrgb(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


class Ctx:
    def __init__(self, bid, dry=False):
        self.bid, self.dry = bid, dry
        self.dir = os.path.join(BUILD, bid); os.makedirs(self.dir, exist_ok=True)
        self.n = 0

    def asset(self, im_spec, w, h=None):
        """Crop + scale a screenshot to exactly w x h (h from aspect if None). Returns (file, w, h)."""
        if self.dry:
            return None, w, (h if h is not None else round(w * aspect(im_spec)))
        im = Image.open(im_spec["path"]).convert("RGB")
        if im_spec.get("crop"):
            im = im.crop(im_spec["crop"])
        sw, sh = im.size
        if h is None:
            h = round(w * sh / sw)
        else:  # cover-fit then centre crop
            s = max(w / sw, h / sh)
            im = im.resize((max(w, round(sw * s)), max(h, round(sh * s))), Image.LANCZOS)
            l, t = (im.size[0] - w) // 2, (im.size[1] - h) // 2
            im = im.crop((l, t, l + w, t + h))
        if im.size != (w, h):
            f = w / sw
            # pixel art scaled up by an integer-ish factor keeps hard edges
            res = Image.NEAREST if f >= 2 and abs(f - round(f)) < 0.05 else Image.LANCZOS
            im = im.resize((w, h), res)
        self.n += 1
        out = os.path.join(self.dir, f"a{self.n:02d}.png")
        im.save(out)
        return out, w, h


def aspect(im_spec):
    im = Image.open(im_spec["path"])
    w, h = im.size
    if im_spec.get("crop"):
        c = im_spec["crop"]; w, h = c[2] - c[0], c[3] - c[1]
    return h / w


def backdrop(ctx, accent, accent2):
    """Deep navy gradient, accent glows, a synthwave floor grid, stars and scanlines."""
    sw, sh = W // 4, H // 4
    y = np.linspace(0, 1, sh)[:, None]
    top, mid, bot = np.array([6, 8, 22]), np.array([12, 14, 40]), np.array(hexrgb(accent2)) * 0.18 + np.array([10, 8, 30])
    base = np.where(y < 0.5, top + (mid - top) * (y / 0.5), mid + (bot - mid) * ((y - 0.5) / 0.5))
    img = np.repeat(base[:, None, :], sw, axis=1).astype(np.float32).reshape(sh, sw, 3)
    yy, xx = np.mgrid[0:sh, 0:sw]

    def glow(cx, cy, r, col, k):
        d = np.sqrt(((xx - cx) / r) ** 2 + ((yy - cy) / r) ** 2)
        return np.exp(-d ** 2 * 2.2)[..., None] * np.array(hexrgb(col)) * k
    img += glow(sw * 0.5, sh * 0.06, sw * 0.75, accent, 0.30)
    img += glow(sw * 0.05, sh * 0.42, sw * 0.6, accent2, 0.10)
    img += glow(sw * 0.95, sh * 0.70, sw * 0.6, accent, 0.08)
    img += glow(sw * 0.5, sh * 1.02, sw * 0.9, accent2, 0.22)
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)

    # perspective floor grid in the bottom 1500 px
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    hz, cx = H - 1500, W / 2
    ac = hexrgb(accent)
    for i in range(-24, 25):
        d.line([(cx + i * 40, hz), (cx + i * 520, H)], fill=ac + (60,), width=3)
    for k in range(1, 23):                        # horizontal lines bunch up toward the horizon
        yv = hz + 1500 * (k / 22) ** 2
        d.line([(0, yv), (W, yv)], fill=ac + (int(30 + 40 * (yv - hz) / 1500),), width=3)
    fade = Image.linear_gradient("L").resize((W, 1500))
    mask = Image.new("L", (W, H), 0); mask.paste(fade, (0, hz))
    layer.putalpha(Image.fromarray(np.minimum(np.array(layer.split()[3]), np.array(mask))))
    im = Image.alpha_composite(im.convert("RGBA"), layer)

    # stars in the upper half
    rng = np.random.default_rng(7); st = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(st)
    for _ in range(900):
        x, yv = rng.uniform(0, W), rng.uniform(0, H * 0.75) ** 1.0
        r = rng.choice([1.5, 2, 2.5, 3.5], p=[0.5, 0.3, 0.15, 0.05]); a = int(rng.uniform(60, 200))
        d.ellipse([x - r, yv - r, x + r, yv + r], fill=(220, 230, 255, a))
    im = Image.alpha_composite(im, st.filter(ImageFilter.GaussianBlur(0.8)))

    # fine CRT scanlines
    a = np.array(im.convert("RGB")).astype(np.float32)
    a[::6] *= 0.88; a[1::6] *= 0.94
    out = os.path.join(ctx.dir, "backdrop.png")
    Image.fromarray(a.astype(np.uint8)).save(out)
    return out


# ---------------------------------------------------------------- layout primitives
def T(text, x, y, fnt, size, color, w=None, justify="left", tracking=0, leading=None, fx=None, name=None, opacity=None):
    """Text item. y is the top of the cap height of the first line; JSX gets the baseline."""
    lines = text if isinstance(text, list) else [text]
    lead = leading or round(size * 1.25)
    base = y + cap_h(fnt, size)
    if justify == "center":
        ax = x + w / 2
    elif justify == "right":
        ax = x + w
    else:
        ax = x
    it = {"type": "text", "text": "\n".join(lines), "x": round(ax), "baseline": round(base), "font": fnt, "size": size,
          "color": color, "justify": justify, "tracking": tracking, "leading": lead, "fx": fx, "name": name or lines[0][:40]}
    if opacity is not None: it["opacity"] = opacity
    height = cap_h(fnt, size) + lead * (len(lines) - 1)
    return it, height


def R(x, y, w, h, r, color, fx=None, fill_opacity=None, name="panel", opacity=None):
    it = {"type": "rect", "x": round(x), "y": round(y), "w": round(w), "h": round(h), "r": r, "color": color, "fx": fx, "name": name}
    if fill_opacity is not None: it["fill_opacity"] = fill_opacity
    if opacity is not None: it["opacity"] = opacity
    return it


SHOT_FX = {"stroke": {"size": 7, "color": "#f4f6ff", "position": "outside"},
           "shadow": {"opacity": 75, "distance": 26, "size": 60, "angle": 90}}
INSET_FX = {"stroke": {"size": 9, "color": "#ffffff", "position": "outside"},
            "shadow": {"opacity": 85, "distance": 34, "size": 70, "angle": 90}}
CARD_FX = lambda ac: {"shadow": {"opacity": 70, "distance": 40, "size": 120, "angle": 90},
                      "stroke": {"size": 3, "color": ac, "position": "inside", "opacity": 45}}
NAME_FX = lambda ac: {"shadow": {"opacity": 80, "distance": 6, "size": 12, "angle": 90}, "glow": {"color": ac, "opacity": 35, "size": 40}}


def I(ctx, spec, x, y, w, h=None, fx=SHOT_FX, name="shot", rotate=None):
    f, w, h = ctx.asset(spec, w, h)
    it = {"type": "image", "file": f, "x": round(x), "y": round(y), "fx": fx, "name": name}
    if rotate: it["rotate"] = rotate
    return it, w, h


def header(ctx, b, items):
    ac = b["accent"]
    y = 260
    t, h = T(b["kicker"], M, y, TAG, 78, ac, w=W - 2 * M, justify="center", tracking=200, name="kicker"); items.append(t); y += h + 90
    size = 560
    while text_w(b["title"], TITLE, size, 20) > W - 2 * M - 40: size -= 10
    t, h = T(b["title"], M, y, TITLE, size, "#ffffff", w=W - 2 * M, justify="center", tracking=20, name="title",
             fx={"shadow": {"opacity": 85, "distance": 18, "size": 40, "angle": 90}, "glow": {"color": ac, "opacity": 60, "size": 120, "spread": 4},
                 "stroke": {"size": 4, "color": b["accent2"], "position": "outside", "opacity": 70}}); items.append(t); y += h + 120
    items.append(R(W / 2 - 600, y, 1200, 16, 8, ac, fx={"glow": {"color": ac, "opacity": 70, "size": 40}}, name="rule")); y += 16 + 110
    lines = wrap(b["subtitle"], BODY, 96, W - 2 * M - 300)
    t, h = T(lines, M, y, BODY, 96, "#dfe5ff", w=W - 2 * M, justify="center", leading=136, name="subtitle",
             fx={"shadow": {"opacity": 70, "distance": 4, "size": 10, "angle": 90}}); items.append(t); y += h + 120
    # spec chips
    cs, padx, ch = 70, 52, 120
    ws = [text_w(c, TAG, cs, 120) + 2 * padx for c in b["chips"]]
    total = sum(ws) + 40 * (len(ws) - 1)
    x = (W - total) / 2
    for c, cw in zip(b["chips"], ws):
        items.append(R(x, y, cw, ch, ch / 2, "#0b0f26", fill_opacity=85, name=f"chip {c}",
                       fx={"stroke": {"size": 4, "color": ac, "position": "inside", "opacity": 90}, "shadow": {"opacity": 60, "distance": 10, "size": 24, "angle": 90}}))
        t, _ = T(c, x, y + (ch - cap_h(TAG, cs)) / 2 + 2, TAG, cs, "#ffffff", w=cw, justify="center", tracking=120, name=c); items.append(t)
        x += cw + 40
    return y + ch + 160


def footer(b, items, y_hint=None):
    t, _ = T(b["footer"], M, H - 230, BODY_B, 68, "#aab4e0", w=W - 2 * M, justify="center", tracking=60, name="footer"); items.append(t)


def name_block(x, y, w, b, name, tag, caption, cap_size=58):
    """Tag (DIN), name (Futura), caption (Avenir). Returns items, height."""
    ac, out = b["accent"], []
    t, h1 = T(tag, x, y, TAG, 62, ac, tracking=160, name="tag"); out.append(t)
    y2 = y + h1 + 40
    nsize = 150
    while text_w(name, TITLE, nsize) > w and nsize > 90: nsize -= 6
    t, h2 = T(name, x, y2, TITLE, nsize, "#ffffff", fx=NAME_FX(ac), name=name); out.append(t)
    y3 = y2 + h2 + 46
    lines = wrap(caption, BODY, cap_size, w)
    t, h3 = T(lines, x, y3, BODY, cap_size, "#c9d1f0", leading=round(cap_size * 1.38), name="caption"); out.append(t)
    return out, (y3 + h3) - y


def hero_card(ctx, b, y, scale=1.0):
    hc = b["hero"]; ac = b["accent"]
    cw = W - 2 * M
    n = len(hc["images"]); gap = 60
    iw = round((cw - 2 * PAD - gap * (n - 1)) // n * scale)
    asp = max(aspect(s) for s in hc["images"])
    ih = round(iw * min(asp, 0.8))
    inner = []
    # text: name + tag on one row, caption under
    tx = M + PAD
    nb, nh = name_block(tx, y + PAD, cw - 2 * PAD, b, hc["name"], hc["tag"], hc["caption"], cap_size=64)
    iy = y + PAD + nh + 70
    x0 = M + (cw - (n * iw + (n - 1) * gap)) // 2
    for k, s in enumerate(hc["images"]):
        it, _, _ = I(ctx, s, x0 + k * (iw + gap), iy, iw, ih, name=f"{hc['name']} {k + 1}")
        inner.append(it)
    ch = (iy + ih + PAD + 10) - y
    panel = R(M, y, cw, ch, 56, "#11152e", fill_opacity=88, fx=CARD_FX(ac), name="panel")
    return {"type": "group", "name": hc["name"], "items": [panel] + inner + nb}, ch


def compact_card(ctx, b, x, y, cw, c, row_h=None, scale=1.0):
    ac = b["accent"]; items = []
    mw = round((cw - 2 * PAD) * scale)
    mx = x + (cw - mw) // 2
    mh = round(mw * min(aspect(c["main"]), 0.82))
    main, _, _ = I(ctx, c["main"], mx, y + PAD, mw, mh, name=c["name"] + " gameplay")
    items.append(main)
    if c.get("inset"):
        ia = aspect(c["inset"])
        iw = round((560 if ia < 0.9 else 440) * scale); ih = round(iw * min(ia, 0.9))
        ix, iy = x + cw - iw + 30, y - 50
        ins, _, _ = I(ctx, c["inset"], ix, iy, iw, ih, fx=INSET_FX, name=c["name"] + " title", rotate=3)
    nb, nh = name_block(x + PAD, y + PAD + mh + 70, cw - 2 * PAD, b, c["name"], c["tag"], c["caption"])
    ch = PAD + mh + 70 + nh + PAD + 10
    if row_h: ch = row_h
    panel = R(x, y, cw, ch, 48, "#11152e", fill_opacity=88, fx=CARD_FX(ac), name="panel")
    out = [panel] + items + nb
    if c.get("inset"): out.append(ins)
    return {"type": "group", "name": c["name"], "items": out}, ch


def grid_banner(ctx, b, scale=1.0):
    items = [{"type": "image", "file": None if ctx.dry else backdrop(ctx, b["accent"], b["accent2"]), "x": 0, "y": 0, "name": "backdrop"}]
    y = header(ctx, b, items)
    g_, h = hero_card(ctx, b, y, scale); items.append(g_); y += h + GAP + 40
    cw = (W - 2 * M - GAP) // 2
    cards = b["cards"]
    for r in range(0, len(cards), 2):
        pair = cards[r:r + 2]
        rh = max(compact_card(Ctx(ctx.bid, dry=True), b, 0, 0, cw, c, scale=scale)[1] for c in pair)
        for k, c in enumerate(pair):
            g_, _ = compact_card(ctx, b, M + k * (cw + GAP), y, cw, c, row_h=rh, scale=scale)
            items.append(g_)
        y += rh + GAP
    footer(b, items)
    return items, y


def four_banner(ctx, b, scale=1.0):
    items = [{"type": "image", "file": None if ctx.dry else backdrop(ctx, b["accent"], b["accent2"]), "x": 0, "y": 0, "name": "backdrop"}]
    y = header(ctx, b, items)
    cw = W - 2 * M
    gap = 60
    iw = round((cw - 2 * PAD - gap) // 2 * scale)
    ih = round(iw * 0.75)
    for gm in b["games"]:
        inner = []
        nb, nh = name_block(M + PAD, y + PAD, cw - 2 * PAD, b, gm["name"], "SAME CODE · FOUR MACHINES", gm["caption"], cap_size=64)
        iy0 = y + PAD + nh + 70
        for k, (s, (pname, pcol)) in enumerate(zip(gm["images"], b["platforms"])):
            ix = M + (cw - 2 * iw - gap) // 2 + (k % 2) * (iw + gap)
            iy = iy0 + (k // 2) * (ih + 150)
            it, _, _ = I(ctx, s, ix, iy, iw, ih, name=f"{gm['name']} {pname}")
            inner.append(it)
            lw = text_w(pname, TAG, 64, 140) + 90
            inner.append(R(ix + 30, iy + ih - 40, lw, 104, 52, "#0b0f26", fill_opacity=92, name=f"label {pname}",
                           fx={"stroke": {"size": 5, "color": pcol, "position": "inside"}, "shadow": {"opacity": 70, "distance": 12, "size": 26, "angle": 90}}))
            t, _ = T(pname, ix + 30, iy + ih - 40 + (104 - cap_h(TAG, 64)) / 2 + 2, TAG, 64, pcol, w=lw, justify="center", tracking=140, name=pname)
            inner.append(t)
        ch = (iy0 + 2 * ih + 150 + 10) - y
        panel = R(M, y, cw, ch, 56, "#11152e", fill_opacity=88, fx=CARD_FX(b["accent"]), name="panel")
        items.append({"type": "group", "name": gm["name"], "items": [panel] + inner + nb})
        y += ch + GAP
    footer(b, items)
    return items, y


def preview(items, path):
    """Rough PIL render of the layout (no effects) to check fit before Photoshop."""
    im = Image.new("RGB", (W, H), "black"); d = ImageDraw.Draw(im)

    def walk(its):
        for it in its:
            if it["type"] == "group": walk(it["items"]); continue
            if it["type"] == "image":
                a = Image.open(it["file"]).convert("RGB")
                if it.get("rotate"): a = a.rotate(-it["rotate"], expand=True, fillcolor=(0, 0, 0))
                im.paste(a, (it["x"], it["y"]))
            elif it["type"] == "rect":
                d.rounded_rectangle([it["x"], it["y"], it["x"] + it["w"], it["y"] + it["h"]], radius=it["r"], fill=it["color"], outline="#556")
            elif it["type"] == "text":
                f = font(it["font"], it["size"]); y = it["baseline"]
                for ln in it["text"].split("\n"):
                    w = f.getlength(ln); x = it["x"] - (w / 2 if it["justify"] == "center" else w if it["justify"] == "right" else 0)
                    d.text((x, y), ln, font=f, fill=it["color"], anchor="ls"); y += it["leading"]
    walk(items)
    im.resize((W // 6, H // 6), Image.LANCZOS).save(path)


def run(bid, layout_only=False):
    fn, b = {"four-machines": (four_banner, FOUR), "devbench": (grid_banner, DEVB)}.get(bid, (grid_banner, BANNERS.get(bid)))
    limit = H - 330                               # keep clear of the footer
    scale = 1.0
    while scale > 0.7 and fn(Ctx(bid, dry=True), b, scale)[1] > limit:
        scale = round(scale - 0.01, 2)
    ctx = Ctx(bid)
    items, yend = fn(ctx, b, scale)
    print(f"{bid}: scale {scale}")
    os.makedirs(OUT, exist_ok=True)
    spec = {"name": f"banner-{bid}", "width": W, "height": H, "dpi": DPI, "items": items,
            "out_psd": os.path.join(OUT, f"banner-{bid}.psd"), "out_jpg": os.path.join(OUT, f"banner-{bid}.jpg")}
    lp = os.path.join(ctx.dir, "layout.json")
    json.dump(spec, open(lp, "w"), indent=1)
    preview(items, os.path.join(ctx.dir, "preview.png"))
    print(f"{bid}: content ends at y={yend} of {H} (footer at {H - 230})", "OVERFLOW" if yend > H - 300 else "")
    if layout_only:
        return
    jsx = os.path.join(HERE, "render.jsx")
    r = subprocess.run(["osascript", "-e", "with timeout of 3600 seconds",
                        "-e", f'tell application "Adobe Photoshop 2026" to do javascript file (POSIX file "{jsx}") with arguments {{"{lp}"}}',
                        "-e", "end timeout"], capture_output=True, text=True)
    print(bid, (r.stdout + r.stderr).strip())


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    for bid in (args or ALL):
        run(bid, layout_only="--layout-only" in sys.argv)
