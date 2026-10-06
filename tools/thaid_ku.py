#!/usr/bin/env python3
"""ถอดรหัสสตริงภายในของ THAID.COM (internal code / "KU-THAID")

ตารางครบทั้ง 256 ค่าได้จาก binary ตรง ๆ แล้ว (tools/codeset.py: record TIS ที่ 0x33C,
ตาราง [6A2h] internal -> app code) ไม่ต้องเดาจากการ align เมนูอีก:
  80-AD พยัญชนะ ก..ฮ เรียงพจนานุกรม | AF ะ B0 า B1 ำ B2 เ B3 แ | B4-BD เลขไทย ๐-๙
  BE ๆ BF ฿ C0 ฯ | C3-CA สระบน/ล่าง ั ิ ี ึ ื ุ ู ฺ | CB ็ CC ํ CD-D1 ่ ้ ๊ ๋ ์
  D2-DE เส้นกรอบ | DF โ E0 ใ E1 ไ | E2-F6 สระบน+วรรณยุกต์ผสมสำเร็จ | FE = ช่องว่าง (A0)
กฎ: สระนำ เ แ โ ใ ไ เก็บหน้าพยัญชนะ (ลำดับการพิมพ์ปกติ)

ใช้: python tools/thaid_ku.py            -> ตัวอย่างที่ยืนยันแล้ว
     python tools/thaid_ku.py --olsf     -> ถอดโซนข้อความ OLSF ทั้งหมด (0x3834-0x4580)
"""
import sys
from codeset import Image

IMG = Image()
_I2A, _, _ = IMG.codesets()['TIS']

# สระบน+วรรณยุกต์ที่ผสมสำเร็จ (routine 0x131B / ตาราง 0F17h): E2.. = ั่ ั้ ั๊ ั๋ ิ่ ...
PRECOMP = {}
for v, base, top in ((0xC3, 0xE2, 0xD0), (0xC4, 0xE6, 0xD1), (0xC5, 0xEB, 0xD0),
                     (0xC6, 0xEF, 0xD0), (0xC7, 0xF3, 0xD0)):
    for t in range(0xCD, top + 1):
        PRECOMP[base + t - 0xCD] = (v, t)

KU2TH = {}
for c in range(0x80, 0x100):
    t = _I2A[c]
    if t >= 0xA1 and t != 0xFF:
        KU2TH[c] = bytes([t]).decode('cp874', errors='replace')
KU2TH[0xFE] = ' '
BOX = {c: '┼' for c in range(0xD2, 0xDF)}          # เส้นกรอบ (ชิ้นส่วนแบบต่าง ๆ)


def ku_decode(data: bytes, dot_space=True) -> str:
    out = []
    for b in data:
        if b < 0x80:
            out.append('·' if (b == 0x20 and dot_space) else (chr(b) if 0x20 <= b < 0x7F else '¦'))
        elif b in KU2TH:
            out.append(KU2TH[b])
        elif b in BOX:
            out.append(BOX[b])
        elif b in PRECOMP:
            v, t = PRECOMP[b]
            out.append(KU2TH[v] + KU2TH[t])
        else:
            out.append(f'<{b:02X}>')
    return ''.join(out)


if __name__ == '__main__':
    data = IMG.d
    if '--olsf' in sys.argv:
        a, end = 0x3834, 0x4580
        while a < end:
            seg = data[a - 0x100:a - 0x100 + 64]
            print(f'{a:04X}: {ku_decode(seg)}')
            a += 64
        sys.exit()
    samples = [
        (0x4469, 9,  "'บรรทัดที่'"),
        (0x4456, 13, "'รหัสของข้อมูล'"),
        (0x3FFA, 3,  "ปุ่มสถานะ / 'ไทย-ENG'"),
        (0x4484, 5,  "'เพื่อ'"),
        (0x3D3D, 22, "'ภาษาไทยของเครื่องพิมพ์'"),
        (0x38A2, 22, "bottom: 'อังกฤษ ไทย 25 ตัวหนา'"),
    ]
    for addr, n, label in samples:
        seg = data[addr - 0x100: addr - 0x100 + n]
        print(f"{addr:04X} {label:28s}: {ku_decode(seg)}")
