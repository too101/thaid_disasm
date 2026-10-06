#!/usr/bin/env python3
"""วาดแผนภาพ 3 band (upper/middle/lower) ของข้อความหนึ่งแถว ตามที่ THAID ทำ

ใช้ render_row จาก thaid_render.py (จำลอง row renderer 0x16C9-0x1905)
แต่ละ cell แสดงพิกเซลของ 3 band จริงจากฟอนต์ใน THAID.COM
และรหัส U/M/L (glyph ของ band บน/กลาง/ล่าง) ใต้ cell

ใช้ (รันที่ root ของ repo): python tools/ku_bands.py [ข้อความ] [out.png]
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from thaid_render import render_row, to_internal, D
from PIL import Image, ImageDraw, ImageFont

text = sys.argv[1] if len(sys.argv) > 1 else 'ที่นี่มีทุ่งนา'
out = sys.argv[2] if len(sys.argv) > 2 else 'ku_bands.png'
row = render_row(to_internal(text))

S = 5                        # ขยายพิกเซล
CW, BH = 8 * S, 6 * S       # ความกว้าง cell / ความสูง band
LX = 90                      # คอลัมน์ป้ายด้านซ้าย
TOP = 10
W = LX + CW * len(row) + 10
H = TOP + BH * 3 + 85
BG = [(58, 28, 30), (28, 52, 32), (28, 30, 66)]
LBL = ['UPPER', 'MIDDLE', 'LOWER']
try:
    f = ImageFont.truetype('/usr/share/fonts/truetype/lato/Lato-Medium.ttf', 12)
except Exception:
    f = ImageFont.load_default()
im = Image.new('RGB', (W, H), (22, 22, 28))
dr = ImageDraw.Draw(im)
for b in range(3):
    y0 = TOP + b * BH
    dr.rectangle([LX, y0, LX + CW * len(row), y0 + BH], fill=BG[b])
    dr.text((8, y0 + BH // 2 - 6), LBL[b], fill=(220, 220, 220), font=f)
fonts = (0x4CE0, 0x52E0)
for cx, cell in enumerate(row):
    x0 = LX + cx * CW
    for b, (g, blk) in enumerate(cell):
        y0 = TOP + b * BH
        for r in range(6):
            bits = D[fonts[blk] + g * 6 + r]
            for k in range(8):
                if bits & (0x80 >> k):
                    dr.rectangle([x0 + k * S, y0 + r * S, x0 + k * S + S - 1, y0 + r * S + S - 1], fill=(255, 255, 255))
    dr.line([x0, TOP, x0, TOP + BH * 3], fill=(150, 150, 150))
    ty = TOP + BH * 3 + 8
    dr.text((x0 + 3, ty), f'cell {cx}', fill=(220, 220, 220), font=f)
    for i, (n, (g, _)) in enumerate(zip('UML', cell)):
        dr.text((x0 + 3, ty + 16 + i * 14), f'{n}={g:02X}', fill=(235, 190, 70), font=f)
for b in range(4):
    y = TOP + b * BH
    dr.line([LX, y, LX + CW * len(row), y], fill=(230, 80, 80), width=2)
dr.line([LX + CW * len(row), TOP, LX + CW * len(row), TOP + BH * 3], fill=(230, 80, 80), width=2)
im.save(out)
print('wrote', out, len(row), 'cells')
