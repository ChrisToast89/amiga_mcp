#!/usr/bin/env python3
"""annotate.py - render numbered callouts + a legend onto a screenshot.

  annotate.py SPEC.json [SPEC.json ...]

SPEC (paths relative to the spec file):
{
  "image":  "../os4-dashboard.png",
  "output": "../os4-dashboard-annotated.png",      # default: <image>-annotated.png
  "title":  "DevBench — Dashboard",                # legend heading
  "subtitle": "AmigaOS 4 PPC · profile qemu-os4",  # optional
  "legend": "right" | "bottom",                    # default: right (bottom if image is wide+short)
  "items": [ {"box": [x, y, w, h], "label": "Profile badge", "text": "one-line explanation"}, ... ]
}
Boxes are in image pixels (CSS px × deviceScaleFactor). Items are numbered in order.
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

ACCENT = (255, 210, 63)        # callout yellow
ACCENT_DARK = (20, 20, 28)     # outline halo / badge text
LEGEND_BG = (250, 249, 245)
LEGEND_FG = (28, 30, 38)
LEGEND_DIM = (96, 100, 112)
RULE = (222, 220, 212)
HELV = "/System/Library/Fonts/Helvetica.ttc"
SFNS = "/System/Library/Fonts/SFNS.ttf"


def font(size, bold=False):
    """SF Pro (variable) when present - it has arrows/dashes Helvetica lacks; Helvetica otherwise."""
    try:
        f = ImageFont.truetype(SFNS, size)
        f.set_variation_by_name("Bold" if bold else "Regular")
        return f
    except (OSError, ValueError):
        pass
    try:
        return ImageFont.truetype(HELV, size, index=1 if bold else 0)
    except OSError:
        return ImageFont.load_default()


def wrap(draw, text, fnt, width):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width or not cur:
            cur = trial
        else:
            lines.append(cur); cur = word
    if cur:
        lines.append(cur)
    return lines


def badge(draw, cx, cy, r, n):
    draw.ellipse([cx - r - 3, cy - r - 3, cx + r + 3, cy + r + 3], fill=ACCENT_DARK)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=ACCENT)
    f = font(int(r * 1.15), bold=True)
    s = str(n)
    tw = draw.textlength(s, font=f)
    bb = f.getbbox(s)
    draw.text((cx - tw / 2, cy - (bb[1] + bb[3]) / 2), s, font=f, fill=ACCENT_DARK)


def render(spec_path):
    base = os.path.dirname(os.path.abspath(spec_path))
    spec = json.load(open(spec_path))
    img_path = os.path.join(base, spec["image"])
    out = os.path.join(base, spec["output"]) if spec.get("output") else img_path[:-4] + "-annotated.png"
    shot = Image.open(img_path).convert("RGB")
    W, H = shot.size
    u = max(1.0, W / 1600)                 # unit: 1 at 1x, 2 at 2x captures
    items = spec["items"]

    # Dim everything outside the callout boxes slightly so the boxes read first.
    shade = Image.new("L", (W, H), 70)
    sd = ImageDraw.Draw(shade)
    for it in items:
        x, y, w, h = it["box"]
        sd.rounded_rectangle([x, y, x + w, y + h], radius=int(6 * u), fill=0)
    shot = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), shot, shade)

    d = ImageDraw.Draw(shot)
    lw = int(3 * u)
    for it in items:
        x, y, w, h = it["box"]
        d.rounded_rectangle([x - lw, y - lw, x + w + lw, y + h + lw], radius=int(7 * u), outline=ACCENT_DARK, width=lw * 2 + 2)
        d.rounded_rectangle([x - lw / 2, y - lw / 2, x + w + lw / 2, y + h + lw / 2], radius=int(6 * u), outline=ACCENT, width=lw)
    # Badges after all boxes so none is overdrawn; nudge to avoid overlaps.
    r = int(15 * u)
    placed = []
    for n, it in enumerate(items, 1):
        x, y, w, h = it["box"]
        cx, cy = x - r * 0.15, y - r * 0.15
        cx = min(max(cx, r + 4), W - r - 4); cy = min(max(cy, r + 4), H - r - 4)
        for _ in range(12):
            if all((cx - px) ** 2 + (cy - py) ** 2 > (2.3 * r) ** 2 for px, py in placed):
                break
            cx += 2.3 * r
            if cx > W - r - 4:
                cx, cy = x + r, cy + 2.3 * r
        placed.append((cx, cy))
        badge(d, cx, cy, r, n)

    # Legend panel
    pos = spec.get("legend") or "right"
    pad = int(28 * u)
    fh, fl, ft, fs = font(int(22 * u), True), font(int(15.5 * u), True), font(int(15.5 * u)), font(int(13 * u))
    lr = int(13 * u)
    if pos == "right":
        LW = int(520 * u)
    else:
        LW = W
    text_x0 = pad + 2 * lr + int(12 * u)
    col_w = LW - text_x0 - pad
    scratch = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    blocks = []
    for it in items:
        lines = wrap(scratch, it["label"], fl, col_w)
        body = wrap(scratch, it.get("text", ""), ft, col_w)
        blocks.append((lines, body))
    line_h = int(21 * u)
    head_h = pad + int(30 * u) + (int(22 * u) if spec.get("subtitle") else 0) + int(18 * u)
    if pos == "right" and not spec.get("legend"):
        need = head_h + sum((len(a) + len(b)) * line_h + int(16 * u) for a, b in blocks) + pad
        if need > H:          # legend would overhang the screenshot: move it underneath
            pos, LW = "bottom", W
    if pos == "bottom":
        # two columns at the bottom
        ncol = 2
        col_w2 = (LW - pad * (ncol + 1)) // ncol
        text_w = col_w2 - 2 * lr - int(12 * u)
        blocks = [(wrap(scratch, it["label"], fl, text_w), wrap(scratch, it.get("text", ""), ft, text_w)) for it in items]
        heights = [(len(a) + len(b)) * line_h + int(16 * u) for a, b in blocks]
        per = (len(items) + 1) // 2
        colh = [sum(heights[:per]), sum(heights[per:])]
        LH = head_h + max(colh) + pad
        canvas = Image.new("RGB", (W, H + LH), LEGEND_BG)
        canvas.paste(shot, (0, 0))
        cd = ImageDraw.Draw(canvas)
        ox, oy = 0, H
    else:
        heights = [(len(a) + len(b)) * line_h + int(16 * u) for a, b in blocks]
        LH = head_h + sum(heights) + pad
        canvas = Image.new("RGB", (W + LW, max(H, LH)), LEGEND_BG)
        canvas.paste(shot, (0, 0))
        cd = ImageDraw.Draw(canvas)
        ox, oy = W, 0
    y = oy + pad
    cd.text((ox + pad, y), spec.get("title", ""), font=fh, fill=LEGEND_FG)
    y += int(30 * u)
    if spec.get("subtitle"):
        cd.text((ox + pad, y), spec["subtitle"], font=fs, fill=LEGEND_DIM)
        y += int(22 * u)
    cd.line([ox + pad, y + int(6 * u), ox + LW - pad, y + int(6 * u)], fill=RULE, width=max(1, int(u)))
    y += int(18 * u)

    def draw_block(n, bx, by, blk):
        lines, body = blk
        badge(cd, bx + lr, by + lr - int(2 * u), lr, n)
        tx = bx + 2 * lr + int(12 * u)
        for ln in lines:
            cd.text((tx, by), ln, font=fl, fill=LEGEND_FG); by += line_h
        for ln in body:
            cd.text((tx, by), ln, font=ft, fill=LEGEND_DIM); by += line_h
        return by + int(16 * u)

    if pos == "bottom":
        per = (len(items) + 1) // 2
        for c in range(2):
            bx = ox + pad + c * ((LW - pad * 3) // 2 + pad)
            by = y
            for k in range(c * per, min(len(items), (c + 1) * per)):
                by = draw_block(k + 1, bx, by, blocks[k])
    else:
        by = y
        for k, blk in enumerate(blocks):
            by = draw_block(k + 1, ox + pad, by, blk)
    canvas.save(out, optimize=True)
    return out


if __name__ == "__main__":
    for p in sys.argv[1:]:
        print("wrote", render(p))
