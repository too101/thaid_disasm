#!/usr/bin/env python3
"""plot ฟอนต์ไทย 8x16 (16 ไบต์/glyph) ที่ file offset 0x64F0..0x6CEF (128 glyph; 0x6CF0..0x6DEF ไม่ใช่ glyph) ของ THAID.COM
ใช้: python tools/font_map_16.py [base] [count] -> font_map_64F0.png (16 glyph ต่อแถว, ป้ายแถว = ลำดับ glyph เลขฐาน 16)"""
import sys
from PIL import Image, ImageDraw, ImageFont
D = open('THAID.COM', 'rb').read()
base = int(sys.argv[1], 16) if len(sys.argv) > 1 else 0x64F0
count = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0x80
S, PAD, LM, TM = 3, 6, 40, 44
GW, GH = 8 * S, 16 * S
CW, CH = GW + PAD, GH + PAD
rows = (count + 15) // 16
try:
    FT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 11)
    FB = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf', 13)
except Exception:
    FT = FB = ImageFont.load_default()
im = Image.new('RGB', (LM + 16 * CW + 6, TM + rows * CH + 6), (18, 18, 22))
dr = ImageDraw.Draw(im)
dr.text((8, 6), f'file 0x{base:04X}  8x16 Thai font ({count} glyphs, 16 bytes each, ends 0x{base + count * 16 - 1:04X})', fill=(255, 255, 255), font=FB)
dr.text((8, 24), 'glyph index = row(left)+column(top) ; offset = base + index*16', fill=(140, 140, 150), font=FT)
for c in range(16):
    dr.text((LM + c * CW + GW // 2 - 3, TM - 14), f'{c:X}', fill=(255, 200, 80), font=FT)
for r in range(rows):
    dr.text((4, TM + r * CH + GH // 2 - 6), f'{r * 16:02X}', fill=(255, 200, 80), font=FT)
for i in range(count):
    r, c = divmod(i, 16)
    x0, y0 = LM + c * CW, TM + r * CH
    dr.rectangle([x0 - 2, y0 - 2, x0 + GW + 1, y0 + GH + 1], fill=(30, 30, 42) if r % 2 == 0 else (24, 24, 34))
    for ry in range(16):
        b = D[base + i * 16 + ry]
        for k in range(8):
            if b & (0x80 >> k):
                dr.rectangle([x0 + k * S, y0 + ry * S, x0 + k * S + S - 1, y0 + ry * S + S - 1], fill=(255, 255, 255))
im.save(f'font_map_{base:04X}.png')
print('wrote', f'font_map_{base:04X}.png', im.size)
