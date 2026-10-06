#!/usr/bin/env python3
"""วาดฟอนต์ VGA 8x16 หลัง THAID โหมด 3 ("ตัวอักษรไทย ไม่จัดบรรทัด") โหลดฟอนต์ไทยทับ slot 80h..FFh (รูทีน 4D10h)
slot ของ glyph i = ตาราง internal->app ของชุดรหัสที่เลือก [i2a[0x80+i]] (0 = ข้าม, FFh = ไม่มีรหัส -> ลง slot FFh ซ้อนกัน ตัวสุดท้ายชนะ)
slot 00h..7Fh = ฟอนต์ ROM ของการ์ด (ไม่อยู่ในไฟล์ -> วาดช่องว่างสีเทา)
ใช้: python tools/font_vga_loaded.py  -> font_vga_KU.png font_vga_TIS.png"""
import sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, 'tools')
from codeset import Image as CS
D = open('THAID.COM', 'rb').read()
GLYPH = 0x64E0
S, PAD, LM, TM = 3, 6, 40, 44
GW, GH = 8 * S, 16 * S
CW, CH = GW + PAD, GH + PAD
try:
    FT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 11)
    FB = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf', 13)
except Exception:
    FT = FB = ImageFont.load_default()

def build(i2a):
    slots = {}
    for i in range(0x80):
        t = i2a[0x80 + i]
        if t:
            slots[t] = i          # ตัวหลังทับตัวก่อน เหมือน loop ใน 4D10h
    return slots

def render(name, slots):
    im = Image.new('RGB', (LM + 16 * CW + 6, TM + 16 * CH + 6), (18, 18, 22))
    dr = ImageDraw.Draw(im)
    dr.text((8, 6), f'VGA font after THAID mode 3 load, code set {name}  (slot = app code)', fill=(255, 255, 255), font=FB)
    dr.text((8, 24), 'slot = row(left)+column(top) ; 00-7F = card ROM font (not drawn) ; 80-FF = Thai glyphs per code set', fill=(140, 140, 150), font=FT)
    for c in range(16): dr.text((LM + c * CW + GW // 2 - 3, TM - 14), f'{c:X}', fill=(255, 200, 80), font=FT)
    for r in range(16): dr.text((6, TM + r * CH + GH // 2 - 6), f'{r:X}0', fill=(255, 200, 80), font=FT)
    for slot in range(256):
        r, c = divmod(slot, 16)
        x0, y0 = LM + c * CW, TM + r * CH
        bg = (40, 40, 40) if slot < 0x80 else ((30, 30, 42) if r % 2 == 0 else (24, 24, 34))
        dr.rectangle([x0 - 2, y0 - 2, x0 + GW + 1, y0 + GH + 1], fill=bg)
        if slot in slots:
            base = GLYPH + slots[slot] * 16
            for ry in range(16):
                b = D[base + ry]
                for k in range(8):
                    if b & (0x80 >> k):
                        dr.rectangle([x0 + k * S, y0 + ry * S, x0 + k * S + S - 1, y0 + ry * S + S - 1], fill=(255, 255, 255))
    dr.line([LM - 3, TM - 3 + 8 * CH, LM + 16 * CW - 3, TM - 3 + 8 * CH], fill=(200, 80, 80))
    return im

if __name__ == '__main__':
    for name, (i2a, a2i, p) in CS().codesets().items():
        slots = build(i2a)
        render(name, slots).save(f'font_vga_{name}.png')
        print(name, 'glyph slots used:', len(slots), 'missing 80..FF:', sorted(set(range(0x80, 0x100)) - set(slots)).__len__())
