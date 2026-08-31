#!/usr/bin/env python3
"""Composite the Tapset Wear OS screenshot into Samsung's official
Galaxy Watch 8 Classic front render, then lay out the tall gallery canvas.

Source render: images.samsung.com Scene7 gallery for SM-L500 (fmt=png-alpha).
Calibrated for it: dial centre (799, 800), display radius 250, scale 1.0.
Usage: python3 compose_tapset_watch_mockup.py [cx cy r scale]"""
from PIL import Image, ImageDraw, ImageFilter
from collections import deque
import sys

import os
SCRATCH = os.path.dirname(os.path.abspath(__file__))  # renders live next to this script
SHOT = '/Users/uladzislaudziarkach/VibeCodeBoost/VladDer_Projects/Training_app/Play_Store_Assets/wear_screenshots_en/01-set.png'

# Tunables (native render coords, 1600x1600)
CX = int(sys.argv[1]) if len(sys.argv) > 1 else 803
CY = int(sys.argv[2]) if len(sys.argv) > 2 else 775
R  = int(sys.argv[3]) if len(sys.argv) > 3 else 265

im = Image.open(f'{SCRATCH}/galaxy_watch8_classic_front.png').convert('RGBA')
W, H = im.size
px = im.load()

def near_white(p, th=245):
    r, g, b, a = p
    return a > 0 and r >= th and g >= th and b >= th

# 1) Flood-fill white background from the borders -> transparent
seen = [[False]*W for _ in range(H)]
q = deque()
for x in range(W):
    for y in (0, H-1):
        q.append((x, y))
for y in range(H):
    for x in (0, W-1):
        q.append((x, y))
while q:
    x, y = q.popleft()
    if x < 0 or y < 0 or x >= W or y >= H or seen[y][x]:
        continue
    seen[y][x] = True
    p = px[x, y]
    if p[3] == 0 or near_white(p):
        px[x, y] = (0, 0, 0, 0)
        q.extend(((x+1, y), (x-1, y), (x, y+1), (x, y-1)))

# 2) Enclosed flat-white pockets (strap holes, buckle gaps) -> transparent
visited = [[False]*W for _ in range(H)]
for sy in range(H):
    for sx in range(W):
        if visited[sy][sx] or not near_white(px[sx, sy], 250):
            continue
        comp, q2, flat = [], deque([(sx, sy)]), True
        visited[sy][sx] = True
        while q2:
            x, y = q2.popleft()
            comp.append((x, y))
            for nx, ny in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
                if 0 <= nx < W and 0 <= ny < H and not visited[ny][nx] and near_white(px[nx, ny], 250):
                    visited[ny][nx] = True
                    q2.append((nx, ny))
        if len(comp) >= 15:
            for x, y in comp:
                px[x, y] = (0, 0, 0, 0)

# 3) Report the dark disk span on the face row/column for centre sanity check
def span(scan_row=True, at=775):
    dark = [i for i in range(W if scan_row else H)
            if (lambda p: p[3] > 200 and (p[0]+p[1]+p[2])/3 < 60)(px[i, at] if scan_row else px[at, i])
            and 400 < i < 1250]
    return (min(dark), max(dark)) if dark else None
print('row dark span :', span(True, CY))
print('col dark span :', span(False, CX))

# 4) Circle-mask the watch screenshot and paste it over the display
shot = Image.open(SHOT).convert('RGBA').resize((2*R, 2*R), Image.LANCZOS)
mask = Image.new('L', (2*R, 2*R), 0)
ImageDraw.Draw(mask).ellipse((0, 0, 2*R, 2*R), fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(1.2))
im.paste(shot, (CX-R, CY-R), mask)

# 5) Tall gallery canvas: 860x1864, black, watch kept large and cropped to width
CANW, CANH = 860, 1864
scale = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
scaled = im.resize((int(W*scale), int(H*scale)), Image.LANCZOS)
# crop horizontally around the dial centre
left = int(CX*scale) - CANW//2
scaled = scaled.crop((left, 0, left + CANW, scaled.size[1]))
# fade the strap's crop cuts into the background
sw, sh = scaled.size
alpha = scaled.getchannel('A').load()
spx = scaled.load()
bounds = [y for y in range(sh) if any(alpha[x, y] > 10 for x in range(0, sw, 4))]
top, bot = min(bounds), max(bounds)
FADE = 56
for y in range(sh):
    k = 1.0
    if y < top + FADE:
        k = max(0.0, (y - top) / FADE)
    elif y > bot - FADE:
        k = max(0.0, (bot - y) / FADE)
    if k < 1.0:
        for x in range(sw):
            r, g, b, a = spx[x, y]
            spx[x, y] = (r, g, b, int(a * k))

canvas = Image.new('RGBA', (CANW, CANH), (0, 0, 0, 255))
canvas.paste(scaled, ((CANW - sw)//2, (CANH - sh)//2), scaled)
out = canvas.convert('RGB')
out.save(f'{SCRATCH}/../src/assets/screenshots/tapset/wear_os_set.png', optimize=True)
out.resize((430, 932), Image.LANCZOS).save(f'{SCRATCH}/wear_mockup_preview.png')
print('saved', f'{SCRATCH}/../src/assets/screenshots/tapset/wear_os_set.png')
