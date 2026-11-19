#!/usr/bin/env python3
"""Draw the GTA 6 launch-week meme for make.fun bounty gta6-meme-x-01.

Original art, drawn programmatically with PIL: a Vice City synthwave sunset,
palm-tree silhouettes, a skyline with a neon make.fun sign, and make.fun's
ghost mascot front and centre, holding its magenta star coin up like a
trophy. Caption: 13 YEARS. 2 DELAYS. 1 SICK DAY. / WORTH IT.

Output: meme.png, 1080x1080 (drawn at 2x and downscaled for smooth edges).
"""
import math
import random
from PIL import Image, ImageDraw, ImageFont

SS = 2                      # supersample factor
W, H = 1080, 1080           # final size
CW, CH = W * SS, H * SS     # canvas size

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(size):
    return ImageFont.truetype(BOLD, size * SS)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ---- sky gradient (Vice City sunset), sky spans y 0..800 -------------------
SKY_STOPS = [
    (0.00, (24, 10, 58)),
    (0.30, (94, 26, 92)),
    (0.52, (186, 38, 110)),
    (0.70, (255, 88, 62)),
    (0.86, (255, 158, 79)),
    (1.00, (255, 196, 107)),
]
SKY_BOTTOM = 800


def sky_color(y):
    t = max(0.0, min(1.0, y / SKY_BOTTOM))
    for i in range(len(SKY_STOPS) - 1):
        t0, c0 = SKY_STOPS[i]
        t1, c1 = SKY_STOPS[i + 1]
        if t0 <= t <= t1:
            return lerp(c0, c1, (t - t0) / (t1 - t0))
    return SKY_STOPS[-1][1]


def draw_gradient(d):
    for y in range(0, SKY_BOTTOM, 2):
        d.rectangle([0, y * SS, CW, (y + 2) * SS], fill=sky_color(y))


def star4_points(cx, cy, r_out, r_in):
    pts = []
    for i in range(8):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(-90 + i * 45)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def star5_points(cx, cy, r_out, r_in):
    pts = []
    for i in range(10):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(-90 + i * 36)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def bezier(p0, p1, p2, n=24):
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
        pts.append((x * SS, y * SS))
    return pts


def text_centred(d, cx, y, s, fnt, fill, outline=(10, 6, 24), sw=5):
    """Draw text centred on cx. bbox is measured in canvas pixels, so the
    width is converted back to final-image pixels before centring."""
    bbox = d.textbbox((0, 0), s, font=fnt)
    w1 = (bbox[2] - bbox[0]) / SS
    x0 = (cx - w1 / 2 - bbox[0] / SS) * SS
    d.text((x0, y * SS), s, font=fnt, fill=fill,
           stroke_width=sw * SS, stroke_fill=outline)


# ---- canvas -----------------------------------------------------------------
img = Image.new("RGB", (CW, CH), (24, 10, 58))
d = ImageDraw.Draw(img)
draw_gradient(d)

# sun with synthwave slats, left of the ghost so it stays visible
SUN = (330, 400, 140)
d.ellipse([(SUN[0] - SUN[2]) * SS, (SUN[1] - SUN[2]) * SS,
           (SUN[0] + SUN[2]) * SS, (SUN[1] + SUN[2]) * SS],
          fill=(255, 233, 168))
for yy, hh in [(448, 6), (468, 8), (490, 11), (514, 14)]:
    half = math.sqrt(max(0, SUN[2] ** 2 - (yy - SUN[1]) ** 2))
    d.rectangle([(SUN[0] - half) * SS, yy * SS,
                 (SUN[0] + half) * SS, (yy + hh) * SS],
                fill=sky_color(yy))

# birds (small arcs, PIL angles run clockwise from 3 o'clock, so 200..340
# passes through 270 = straight up: a shallow cap)
for bx, by, s in [(180, 230, 16), (255, 185, 12), (770, 215, 14)]:
    d.arc([(bx - s) * SS, (by - s // 2) * SS, (bx + s) * SS, (by + s // 2) * SS],
          200, 340, fill=(30, 12, 55), width=3 * SS)

# ---- skyline ----------------------------------------------------------------
random.seed(6)
SKYLINE_BASE = 800
BLDG = (26, 9, 48)
buildings = []
x = -10
while x < W + 10:
    bw = random.randint(64, 132)
    bh = random.randint(60, 180)
    top = SKYLINE_BASE - bh
    d.rectangle([x * SS, top * SS, (x + bw) * SS, SKYLINE_BASE * SS], fill=BLDG)
    for _ in range(random.randint(6, 16)):
        wx = x + random.randint(6, max(7, bw - 12))
        wy = top + random.randint(10, max(11, bh - 16))
        d.rectangle([wx * SS, wy * SS, (wx + 5) * SS, (wy + 7) * SS],
                    fill=(255, 215, 106))
    buildings.append((x, top, bw))
    x += bw + random.randint(2, 10)

# ---- palm trees -------------------------------------------------------------
def palm(d, base_x, base_y, height, lean, color):
    top_x, top_y = base_x + lean, base_y - height
    d.line(bezier((base_x, base_y), (base_x + lean * 0.4, base_y - height * 0.6),
                  (top_x, top_y)), fill=color, width=16 * SS, joint="curve")
    for ang in (-155, -125, -95, -65, -35, -5, 25):
        rad = math.radians(ang)
        ex = top_x + math.cos(rad) * 110
        ey = top_y + math.sin(rad) * 46 + 38
        mx = top_x + math.cos(rad) * 62
        my = top_y + math.sin(rad) * 8 - 28
        d.line(bezier((top_x, top_y), (mx, my), (ex, ey)), fill=color,
               width=11 * SS, joint="curve")


PALM = (18, 7, 36)
palm(d, 80, 806, 300, 40, PALM)
palm(d, 1045, 806, 330, -35, PALM)

# neon make.fun sign on a wide building left of the ghost, clear of the palms
sign_building = None
for bx, btop, bw in buildings:
    if 120 <= bx <= 300 and bw >= 100:
        sign_building = (bx, btop, bw)
        break
if sign_building is None:
    sign_building = (830, 660, 150)
sx, stop, sbw = sign_building
sign_font = font(52)
for glow in range(3):
    d.text(((sx + sbw / 2) * SS, (stop + 26) * SS), "make.fun", font=sign_font,
           fill=(255, 79, 216), anchor="ma",
           stroke_width=(6 - glow) * SS, stroke_fill=(255, 79, 216))
d.text(((sx + sbw / 2) * SS, (stop + 26) * SS), "make.fun", font=sign_font,
       fill=(255, 220, 245), anchor="ma")

# ---- foreground -------------------------------------------------------------
d.rectangle([0, SKYLINE_BASE * SS, CW, CH], fill=(16, 7, 38))
d.rectangle([0, SKYLINE_BASE * SS, CW, (SKYLINE_BASE + 4) * SS],
            fill=(255, 79, 216))

# ---- the make.fun ghost -----------------------------------------------------
# Local coords: body 300 wide, 580 tall; drawn at origin (390, 300).
GX, GY = 390, 300


def ghost_body_points(inset):
    """Ghost outline: a dome on top (arc bulging UP, so y uses -sin), straight
    sides, and three downward scallops along the hem. Traced clockwise from
    the top-left, so the polygon fills correctly."""
    pts = []
    cx, cy, r = 150, 150, 150 - inset
    for a in range(180, -1, -6):
        rad = math.radians(a)
        pts.append((cx + r * math.cos(rad), cy - r * math.sin(rad)))
    pts.append((300 - inset, 430))
    for k in (2, 1, 0):  # hem scallops, right to left
        scx = 50 + 100 * k + inset * 0.5
        scr = 50 - inset * 0.6
        for a in range(0, 181, 12):
            rad = math.radians(a)
            pts.append((scx + scr * math.cos(rad), 430 + scr * math.sin(rad)))
    pts.append((inset, 430))
    pts.append((inset, 150))
    return [(GX + px, GY + py) for px, py in pts]


def draw_poly(points, fill):
    d.polygon([(px * SS, py * SS) for px, py in points], fill=fill)


# thick black outline, then white body
draw_poly(ghost_body_points(0), (8, 5, 20))
draw_poly(ghost_body_points(14), (255, 255, 255))

# little round hand on the left side
d.ellipse([(GX - 6) * SS, (GY + 300) * SS, (GX + 42) * SS, (GY + 348) * SS],
          fill=(255, 255, 255), outline=(8, 5, 20), width=5 * SS)

# raised right arm, holding the coin up (coords are canvas pixels: * SS)
d.line([((GX + 258) * SS, (GY + 330) * SS), ((GX + 318) * SS, (GY + 214) * SS)],
       fill=(8, 5, 20), width=36 * SS, joint="curve")
d.line([((GX + 258) * SS, (GY + 330) * SS), ((GX + 318) * SS, (GY + 214) * SS)],
       fill=(255, 255, 255), width=24 * SS, joint="curve")
# round little hand at the end of the arm
d.ellipse([(GX + 296) * SS, (GY + 178) * SS, (GX + 344) * SS, (GY + 226) * SS],
          fill=(255, 255, 255), outline=(8, 5, 20), width=5 * SS)

# magenta coin with a white star, held above the hand
COIN = (GX + 330, GY + 128, 54)
d.ellipse([(COIN[0] - COIN[2]) * SS, (COIN[1] - COIN[2]) * SS,
           (COIN[0] + COIN[2]) * SS, (COIN[1] + COIN[2]) * SS],
          fill=(255, 46, 154), outline=(8, 5, 20), width=6 * SS)
d.polygon([(px * SS, py * SS) for px, py in
           star5_points(COIN[0], COIN[1], 36, 15)], fill=(255, 255, 255))

# two black four-pointed sparkle eyes
for ex in (GX + 108, GX + 192):
    d.polygon([(px * SS, py * SS) for px, py in
               star4_points(ex, GY + 196, 26, 9)], fill=(8, 5, 20))

# sparkles around the coin
for sx_, sy_, sr in [(GX + 420, GY + 90, 16), (GX + 250, GY + 60, 12)]:
    d.polygon([(px * SS, py * SS) for px, py in
               star4_points(sx_, sy_, sr, sr * 0.35)], fill=(255, 255, 255))

# ---- captions ---------------------------------------------------------------
text_centred(d, 540, 52, "13 YEARS. 2 DELAYS.", font(74),
             (255, 255, 255), sw=5)
text_centred(d, 540, 142, "1 SICK DAY.", font(74), (255, 255, 255), sw=5)
text_centred(d, 540, 918, "WORTH IT.", font(118), (255, 233, 168), sw=6)

img = img.resize((W, H), Image.LANCZOS)
img.save("meme.png", optimize=True)
print("saved meme.png", img.size)
