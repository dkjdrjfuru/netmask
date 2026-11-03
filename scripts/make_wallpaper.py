#!/usr/bin/env python3
"""Generate the Netmask OS branding assets:
  - netmask_logo.png  (1920x1080 wallpaper, used as desktop background)
  - netmask_icon.png  (256x256 transparent emblem)

Brand: bg #0D0D1A, accent #00D9FF, accent2 #E94560
Reproducible: python3 make_wallpaper.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

BG = (13, 13, 26)        # 0D0D1A
BG_LIGHT = (21, 21, 43)  # 15152B
CYAN = (0, 217, 255)     # 00D9FF
RED = (233, 69, 96)      # E94560
GREY = (122, 122, 150)   # 7A7A96
DIM = (62, 62, 94)       # 3E3E5E

W, H = 1920, 1080
CX, CY = W // 2, 400

PROJ = Path("/home/z/my-project/download/netmask-os")
NF_BOLD = PROJ / "mkosi.extra/usr/share/fonts/truetype/netmask/FiraCodeNerdFont-Bold.ttf"
NF_REG = PROJ / "mkosi.extra/usr/share/fonts/truetype/netmask/FiraCodeNerdFont-Regular.ttf"


def load_font(candidates, size):
    for p in candidates:
        if p and Path(p).exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default(size)


def font_any(size):
    return load_font([NF_BOLD, "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"], size)


def radial_mask(w, h, invert=False):
    """L mask: bright center -> dark edges (or inverse)."""
    g = Image.radial_gradient("L").resize((w, h))
    if g.getpixel((w // 2, h // 2)) > g.getpixel((0, 0)):
        g = g.point(lambda v: 255 - v)
    if invert:
        g = g.point(lambda v: 255 - v)
    return g


def eye_shape(s, center_x, angle):
    """An angled eye slit: 88x30 rounded bar rotated by `angle` degrees."""
    ew, eh = 88 * s, 30 * s
    eye = Image.new("RGBA", (int(ew + 40 * s), int(eh + 40 * s)), (0, 0, 0, 0))
    ed = ImageDraw.Draw(eye)
    o = 20 * s
    ed.rounded_rectangle([o, o, o + ew, o + eh], radius=13 * s, fill=CYAN + (255,))
    eye = eye.rotate(angle, resample=Image.BICUBIC, expand=True)
    pos = (int(center_x - eye.width / 2), int(CY - eye.height / 2))
    return eye, pos


def draw_eyes(layer, s):
    for cx_eye, ang in ((CX - 100 * s, -12), (CX + 100 * s, 12)):
        eye, pos = eye_shape(s, cx_eye, ang)
        layer.alpha_composite(eye, pos)


def draw_mask_emblem(scale=1.0, glow=True):
    """Return an RGBA layer with the netmask emblem centered at (CX, CY)."""
    s = scale
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    # --- glow (blur of the outline + eyes) ---
    if glow:
        gl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(gl)
        gd.rounded_rectangle(
            [CX - 190 * s, CY - 115 * s, CX + 190 * s, CY + 115 * s],
            radius=52 * s, outline=CYAN + (255,), width=max(1, int(10 * s)),
        )
        draw_eyes(gl, s)
        gl = gl.filter(ImageFilter.GaussianBlur(26 * s))
        gl.putalpha(gl.split()[3].point(lambda v: int(v * 0.55)))
        layer.alpha_composite(gl)

    # --- body ---
    d.rounded_rectangle(
        [CX - 190 * s, CY - 115 * s, CX + 190 * s, CY + 115 * s],
        radius=52 * s, fill=(16, 16, 42, 215), outline=CYAN + (255,), width=max(1, int(10 * s)),
    )

    # --- eyes (angled slits) ---
    draw_eyes(layer, s)

    # --- red accent slash, top-right ---
    p1 = (CX + 150 * s, CY - 168 * s)
    p2 = (CX + 252 * s, CY - 108 * s)
    d.line([p1, p2], fill=RED + (255,), width=max(1, int(7 * s)))
    r = max(1, int(3.5 * s))
    for p in (p1, p2):
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=RED + (255,))
    return layer


def tracked_text(d, xy, text, font, tracking, fill, anchor_center_x=None):
    """Draw text with letter spacing; optionally center on anchor_center_x."""
    widths = [d.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = (anchor_center_x - total / 2) if anchor_center_x is not None else xy[0]
    y = xy[1]
    for ch, w in zip(text, widths):
        d.text((x, y), ch, font=font, fill=fill)
        x += w + tracking
    return total


def make_wallpaper():
    img = Image.new("RGB", (W, H), BG)

    # soft center glow + corner vignette
    glow = Image.new("RGB", (W, H), BG_LIGHT)
    img = Image.composite(glow, img, radial_mask(W, H))
    vig = Image.new("RGB", (W, H), (9, 9, 18))
    img = Image.composite(vig, img, radial_mask(W, H, invert=True).point(lambda v: int(v * 0.75)))

    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    # subnet grid
    d = ImageDraw.Draw(ov)
    for x in range(0, W + 1, 64):
        a = 20 if x % 320 == 0 else 10
        d.line([(x, 0), (x, H)], fill=CYAN + (a,), width=1)
    for y in range(0, H + 1, 64):
        a = 20 if y % 320 == 0 else 10
        d.line([(0, y), (W, y)], fill=CYAN + (a,), width=1)
    img = Image.alpha_composite(img.convert("RGBA"), ov)

    # emblem
    img.alpha_composite(draw_mask_emblem(1.0))

    # wordmark: NETMASK in cyan, OS in red — both parts of one centered line
    d = ImageDraw.Draw(img)
    f_big = font_any(96)
    gap = 30
    nm_w = sum(d.textlength(c, font=f_big) for c in "NETMASK") + 14 * (len("NETMASK") - 1)
    os_w = sum(d.textlength(c, font=f_big) for c in "OS")
    total = nm_w + gap + os_w
    start = CX - total / 2
    tracked_text(d, (start, 636), "NETMASK", f_big, 14, CYAN + (255,))
    tracked_text(d, (start + nm_w + gap, 636), "OS", f_big, 14, RED + (255,))

    # divider
    d.rectangle([CX - 230, 772, CX + 230, 774], fill=CYAN + (70,))

    # tagline
    f_tag = font_any(28)
    tracked_text(d, (0, 800), "i3 · polybar · kitty · zsh", f_tag, 6, GREY + (255,), anchor_center_x=CX)

    # corners
    f_small = font_any(22)
    tracked_text(d, (44, 36), "255.255.255.0", f_small, 8, DIM + (255,))
    f_disc = font_any(24)
    tracked_text(d, (0, H - 56), "discord.gg/netmask", f_disc, 4, GREY + (255,), anchor_center_x=W - 190)

    out = PROJ / "mkosi.extra/usr/share/backgrounds/netmask/netmask_logo.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out, "PNG", optimize=True)
    print(f"wrote {out} {out.stat().st_size//1024} KiB")
    return out


def make_icon():
    global W, H, CX, CY
    W0, H0, CX0, CY0 = W, H, CX, CY
    W, H, CX, CY = 256, 256, 128, 128
    s = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    s.alpha_composite(draw_mask_emblem(0.62))
    W, H, CX, CY = W0, H0, CX0, CY0

    out = PROJ / "assets/netmask_icon.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    s.save(out, "PNG", optimize=True)
    print(f"wrote {out} {out.stat().st_size//1024} KiB")
    return out


if __name__ == "__main__":
    make_wallpaper()
    make_icon()
