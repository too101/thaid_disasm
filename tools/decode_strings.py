#!/usr/bin/env python3
"""ดึงสตริงจาก THAID.COM: ASCII + ถอด TIS-620 (CP874) เป็น Unicode
เตือน: byte ช่วง 80h-DFh ในโซน code ส่วนใหญ่เป็น FONT BITMAP ไม่ใช่ข้อความ
       ข้อความ UI ของโปรแกรมเก็บด้วยรหัสภายใน KU-THAID (ไม่ใช่ KU/TIS) -> ถอดในส่วนที่ 3 ของผลลัพธ์"""
import sys
sys.stdout.reconfigure(encoding='utf-8', newline='\n')  # ไม่ให้ Windows แปลงเป็น CRLF เวลา redirect > THAID_strings.txt

path = sys.argv[1] if len(sys.argv) > 1 else 'THAID.COM'
BASE = 0x100  # COM: ที่อยู่ memory = file offset + 0x100
DATA = open(path, 'rb').read()[:0x7528]   # image จริงจบที่ address 0x7627 (ส่วนท้ายไฟล์ไม่ถูกเรียกใช้ ไม่ดึงสตริง)

def tis_decode(b):
    return b.decode('cp874', 'replace')

print("=== ASCII strings (>=6 chars) ===")
out = []
i = 0
while i < len(DATA):
    j = i
    while j < len(DATA) and 0x20 <= DATA[j] <= 0x7E:
        j += 1
    if j - i >= 6:
        out.append(f"{i+BASE:04X}: {DATA[i:j].decode('ascii')}")
    i = max(j, i + 1)
print("\n".join(out))

print("\n=== สตริงที่มีอักขระไทย (ถอดแบบ CP874/TIS-620, >=4 ตัวไทย) ===")
i = 0
while i < len(DATA):
    j = i
    thai = 0
    while j < len(DATA):
        b = DATA[j]
        if 0x20 <= b <= 0x7E or 0xA1 <= b <= 0xFB:
            if 0xA1 <= b <= 0xFB:
                thai += 1
            j += 1
        else:
            break
    if j - i >= 6 and thai >= 4:
        txt = tis_decode(DATA[i:j]).strip()
        print(f"{i+BASE:04X}: {txt[:100]}")
    i = max(j, i + 1)

# ---------------------------------------------------------------------------
# ส่วนที่ 3: ข้อความไทยในรหัสภายในของ THAID ("KU-THAID": ก=80h..ฮ=ADh เรียงพจนานุกรม ไม่ใช่ KU/TIS)
# ถอดผ่านตารางในไฟล์เอง (tools/codeset.py -> thaid_ku.py) ; จำกัดเฉพาะโซนข้อความเมนู OLSF
# (นอกโซนนี้ไบต์ 80h-F6h ส่วนใหญ่เป็นโค้ด/ฟอนต์ จะได้ตัวมั่ว)
# ---------------------------------------------------------------------------
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from thaid_ku import ku_decode  # noqa: E402

print("\n=== ข้อความเมนู OLSF (รหัสภายใน KU-THAID ถอดด้วยตารางของโปรแกรม; 0x3844-0x4590) ===")
_OK = set(range(0x20, 0x7F)) | set(range(0x80, 0xAE)) | set(range(0xAF, 0xC1)) | set(range(0xC3, 0xD2)) \
    | set(range(0xDF, 0xF7)) | {0xFE}
_THAI = _OK - set(range(0x20, 0x7F))
i, end = 0x3844 - BASE, 0x4590 - BASE
while i < end:
    j = i
    while j < end and DATA[j] in _OK:
        j += 1
    seg = DATA[i:j]
    if len(seg) >= 3 and sum(1 for b in seg if b in _THAI) >= 2:
        print(f"{i+BASE:04X}: {ku_decode(seg, False)}")
    i = max(j, i + 1)
