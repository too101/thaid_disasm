#!/usr/bin/env python3
"""plot font 8x6 ทั้ง 4 ชุดของ THAID.COM เป็น font map (16x16 = 256 slot ต่อชุด)
ชุด: 0x4CF0 กลาง/ตัวหนา, 0x52F0 ล่าง/ตัวหนา, 0x58F0 บน?/ตัวบาง(กลาง), 0x5EF0 ล่าง/ตัวบาง
ใช้: python tools/font_maps.py  -> font_map_<offset>.png x4 + font_map_all4_grid.png"""
import sys
from PIL import Image, ImageDraw, ImageFont
D = open('THAID.COM', 'rb').read()
SETS = [(0x4CF0, 'A  file 0x4CF0   block 0 BOLD  (upper+middle bands: ASCII, Thai tops, vowels)'),
        (0x52F0, 'B  file 0x52F0   block 1 BOLD  (lower band: descenders, tails, +u/+uu/+phinthu)'),
        (0x58F0, 'C  file 0x58F0   block 0 THIN  (upper+middle bands)'),
        (0x5EF0, 'D  file 0x5EF0   block 1 THIN  (lower band)')]
S = 4                     # scale
GW, GH, PAD = 8 * S, 6 * S, 6
CW, CH = GW + PAD, GH + PAD
LM, TM = 34, 44
try:
    FT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 11)
    FB = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf', 13)
except Exception:
    FT = FB = ImageFont.load_default()

def render(base, title):
    W, H = LM + 16 * CW + 6, TM + 16 * CH + 6
    im = Image.new('RGB', (W, H), (18, 18, 22)); dr = ImageDraw.Draw(im)
    dr.text((8, 6), title, fill=(255, 255, 255), font=FB)
    dr.text((8, 24), 'slot = row(left)+column(top)   8x6 px glyph, 6 bytes each, pitch 0x600   red line = 7F|80', fill=(140, 140, 150), font=FT)
    for c in range(16): dr.text((LM + c * CW + GW // 2 - 3, TM - 14), f'{c:X}', fill=(255, 200, 80), font=FT)
    for r in range(16): dr.text((6, TM + r * CH + GH // 2 - 6), f'{r:X}0', fill=(255, 200, 80), font=FT)
    for slot in range(256):
        r, c = divmod(slot, 16)
        x0, y0 = LM + c * CW, TM + r * CH
        shade = (30, 30, 42) if (r // 2) % 2 == 0 else (24, 24, 34)
        if slot < 0x80: shade = (26, 34, 26) if (r // 2) % 2 == 0 else (22, 28, 22)
        dr.rectangle([x0 - 2, y0 - 2, x0 + GW + 1, y0 + GH + 1], fill=shade)
        for ry in range(6):
            b = D[base + slot * 6 + ry]
            for k in range(8):
                if b & (0x80 >> k):
                    dr.rectangle([x0 + k * S, y0 + ry * S, x0 + k * S + S - 1, y0 + ry * S + S - 1], fill=(255, 255, 255))
    for c in range(0, 17, 1):
        if c in (0, 8, 16): dr.line([LM - 3 + c * CW, TM - 3, LM - 3 + c * CW, TM + 16 * CH - 3], fill=(90, 90, 110))
    dr.line([LM - 3, TM - 3 + 8 * CH, LM + 16 * CW - 3, TM - 3 + 8 * CH], fill=(200, 80, 80))   # เส้นแบ่ง 7F/80
    return im

if __name__ == '__main__':
    ims = []
    for base, title in SETS:
        im = render(base, title); im.save(f'font_map_{base:04X}.png'); ims.append(im)
        print('wrote', f'font_map_{base:04X}.png', im.size)
