#!/usr/bin/env python3
"""เรนเดอร์ glyph จากฟอนต์ 8x16 ใน THAID.COM เป็น ASCII art
FONT A = mem 4B90h (ครึ่งบน/ตัวอักษรหลัก), FONT B = mem 5B90h (ครึ่งล่าง/เส้นกรอบ)
slot = รหัสอักขระ (ตัวอย่าง: A1h = ก)
"""
import sys

DATA = open(sys.argv[1] if len(sys.argv) > 1 else 'THAID.COM', 'rb').read()

def render(font_mem, code, label):
    fo = font_mem - 0x100 + code * 16
    rows = DATA[fo:fo + 16]
    print(f"{label} slot {code:02X}h (mem {font_mem + code*16:04X})")
    for i, b in enumerate(rows):
        mark = '  <- ครึ่งล่าง' if i == 8 else ''
        print('  ' + ''.join('#' if b & (0x80 >> k) else '.' for k in range(8)) + mark)
    print()

if __name__ == '__main__':
    codes = [int(c, 16) for c in sys.argv[2:]] or [0xA1, 0xD1, 0xE7]
    for c in codes:
        render(0x4B90, c, 'FONT A')
        render(0x5B90, c, 'FONT B')
