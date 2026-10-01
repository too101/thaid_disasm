#!/usr/bin/env python3
"""จำลอง row renderer ของ THAID (0x16C0-0x18FC) แล้วเรนเดอร์ข้อความไทยเป็น PNG

ใช้ข้อมูลจาก THAID.COM ตรง ๆ ทั้งหมด:
  - ตาราง app->internal จาก record TIS (tools/codeset.py)
  - ตาราง internal -> slice ล่าง [0x1554]
  - ตารางผสมสระบน+วรรณยุกต์ [0x0F17] (routine 0x131B)
  - ตาราง F7-FF -> glyph [0x170D]
  - ฟอนต์ 8x6: block0 (attr bit3=0) = file 0x4CF0, block1 (attr bit3=1) = file 0x52F0
    (ชุดตัวบาง: file 0x58F0 / 0x5EF0)
แต่ละ cell ของแอป -> 3 band (upper/middle/lower) คนละแถว text จริงบนจอ (MaxScan=5)

ใช้: python tools/thaid_render.py "ข้อความ" out.png [--thin] [--comp N]
"""
import sys
from codeset import Image

img = Image()
D = img.d
TIS_I2A, TIS_A2I, _ = img.codesets()['TIS']
LOWER = [img.b(0x1554 + i) for i in range(256)]


def f17(v):
    a = 0x0F17 + 2 * v
    return img.b(a), img.b(a + 1)          # bl (ฐาน glyph ผสม), bh (วรรณยุกต์สูงสุดที่ผสมได้)


S0, CONS, V1, AFTER, CONS2, COMP = 'S0', 'CONS', 'V1', 'AFTER', 'CONS2', 'COMP'


def render_row(codes, comp_space=0, comp_special=0, special=None, comp_box=True, width=None):
    """codes = internal codes ของแถว (หลังแปลง app->internal แล้ว)
    คืน list ของ (upper, mid, lower) — แต่ละตัวเป็น (glyph, block)"""
    out = []
    state = S0
    last_vowel = 0
    comp = None
    src = 0

    def emit(c, upper=0):
        out.append([(upper, 0), (c, 0), (LOWER[c], 1)])

    def fill():                      # 0x189D: เติม FF ให้คอลัมน์กลับมาตรงกับต้นฉบับ
        while len(out) < src - 1:
            out.append([(0xFF, 0), (0xFF, 0), (0xFF, 1)])

    i = 0
    while i < len(codes):
        c = codes[i]; i += 1; src = i
        while True:                               # loop = "reprocess" (jmp กลับ dispatcher)
            if state == S0:                       # 0x1736
                if c < 0x80 or 0xAE <= c < 0xC3:
                    emit(c)
                elif c < 0xAE:
                    state = CONS; emit(c)
                elif c < 0xD2:
                    out.append([(0, 0), (c, 0), (0, 0)])   # 0x1749 สระลอย: วางแถวกลาง
                else:
                    state = high(c, out, emit, fill, comp_box, state)
                break
            if state in (CONS, CONS2):            # 0x179A / 0x17A4
                if c < 0xC3 or c >= 0xD2:
                    state = S0 if state == CONS else AFTER
                    continue
                if c < 0xCA:
                    last_vowel = c; state = V1
                else:
                    state = AFTER
                attach(out, c)
                break
            if state == V1:                       # 0x17E7
                if c == 0xCC and last_vowel == 0xC8:
                    state = AFTER; attach(out, c); break
                if 0xCD <= c < 0xD2:
                    bl, bh = f17(last_vowel)      # 0x131B
                    if c <= bh:
                        state = AFTER; attach(out, c - 0xCD + bl); break
                state = AFTER
                continue
            if state == COMP:                     # 0x186A
                if c == comp[0]:
                    comp[1] -= 1
                    if comp[1] == 0:
                        emit(0x20 if c == 0xFE else c); fill(); state = S0
                    else:
                        emit(0x20 if c == 0xFE else c)
                    break
                state = AFTER
                continue
            if state == AFTER:                    # 0x176C
                n = comp_space if c == 0x20 else (comp_special if c == special else None)
                if n is not None:
                    if n - 1 == 0:
                        emit(0x20 if c == 0xFE else c); fill(); state = S0
                    else:
                        comp = [c, n - 1]; state = COMP; emit(0x20 if c == 0xFE else c)
                    break
                if 0xC3 <= c < 0xD2:
                    out.append([(0, 0), (c, 0), (0, 0)])
                elif c >= 0xD2:
                    state = high(c, out, emit, fill, comp_box, state)
                else:
                    if 0x80 <= c <= 0xAD:
                        state = CONS2
                    emit(c)
                break
    while width and len(out) < width:
        out.append([(0, 0), (0, 0), (0, 1)])
    return out


def attach(out, c):
    """ผสมเข้ากับ cell ก่อนหน้า (ไม่กินคอลัมน์)"""
    if not out:
        return
    cell = out[-1]
    if 0xC8 <= c <= 0xCA:                         # 0x17C4: สระล่าง -> OR เข้า slice ล่าง
        g, blk = cell[2]
        cell[2] = (g | ((c - 0xC7) << 5), blk)
    else:                                         # 0x17DC: สระบน/วรรณยุกต์ -> band บน
        cell[0] = (c, 0)


def high(c, out, emit, fill, comp_box, state):   # 0x180D
    if c < 0xDF:                                  # D2-DE เส้นกรอบ (0x18B8)
        if comp_box:
            fill()
        up, lo = c, c - 0x68
        if c < 0xDC:
            up, lo = 0xDB, 0x77
            if 0xD5 <= c <= 0xD7: up = 0
        if c <= 0xD4: lo = 0
        out.append([(up, 0), (c, 0), (lo, 1)])
    elif c < 0xE2:                                # โ ใ ไ: หัว band บน + ลำ AE + เท้า 66
        out.append([(c, 0), (0xAE, 0), (0x66, 1)])
    elif c < 0xF7:
        emit(0xDE)
    else:
        emit(img.b(0x170D + c))
    return state


def to_internal(text):
    return [TIS_A2I[b] if b >= 0x80 else b for b in text.encode('cp874')]


def draw(rows, path, thin=False, scale=3):
    from PIL import Image as PI
    fonts = (0x58F0, 0x5EF0) if thin else (0x4CF0, 0x52F0)
    w = max(len(r) for r in rows) * 8
    h = len(rows) * 18
    im = PI.new('L', (w, h), 0)
    px = im.load()
    for ry, row in enumerate(rows):
        for cx, cell in enumerate(row):
            for band, (g, blk) in enumerate(cell):
                base = fonts[blk] + g * 6
                for r in range(6):
                    bits = D[base + r]
                    for k in range(8):
                        if bits & (0x80 >> k):
                            px[cx * 8 + k, ry * 18 + band * 6 + r] = 255
    im = im.resize((w * scale, h * scale), PI.NEAREST)
    im.save(path)


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    thin = '--thin' in sys.argv
    lines = args[0].split('\\n') if args else ['กุ่ ที่ ไม่ เพื่อ ฎีกา ญาติ ปู่ น้ำ']
    out = args[1] if len(args) > 1 else 'render.png'
    rows = [render_row(to_internal(t)) for t in lines]
    draw(rows, out, thin)
    print('wrote', out)
