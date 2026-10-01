#!/usr/bin/env python3
"""ดึงตารางรหัส (code set) KU / TIS ที่ฝังใน THAID.COM แบบถอดจาก binary ตรง ๆ

โครงสร้าง (พิสูจน์จากโค้ด init 0x59C และตัวถอด RLE 0x9EF):
  record = ชื่อ 5 ไบต์ (label บรรทัดสถานะ เช่น " KU  ", " TIS ")
         + chunk1 -> 262 ไบต์ : [0x6A2] internal -> app code (256) + params 6 ไบต์
         + chunk2 -> 256 ไบต์ : [0x7A2] app code -> internal
  chunk  = [len][ข้อมูลเข้ารหัส len ไบต์]
           F1 n v  -> v, v+1, ..., v+n-1   (run เพิ่มทีละ 1)
           F0 n v  -> v ซ้ำ n ครั้ง
           F1 F1 / F0 F0 -> ไบต์ F1 / F0 ตามตัว
  record เริ่มที่ 0x2B0 (KU) ต่อด้วย 0x33C (TIS); ไบต์ 00 = จบรายการ
  ตาราง [0x59C] (internal -> รหัสเครื่องพิมพ์) ถอดจาก chunk1 ของ record ที่เลือกเป็นรหัสเครื่องพิมพ์
  (0x949) — โค้ด init ที่ 0x59C ถูกเขียนทับเป็นตารางหลังติดตั้ง
"""
import sys

BASE = 0x100


class Image:
    def __init__(self, path='THAID.COM'):
        self.d = open(path, 'rb').read()

    def b(self, a):
        return self.d[a - BASE]

    def chunk(self, si):
        out = []
        cx = self.b(si); si += 1
        while cx > 0:
            al = self.b(si); si += 1; cx -= 1
            if al in (0xF0, 0xF1):
                nx = self.b(si); si += 1; cx -= 1
                if nx == al:
                    out.append(al); continue
                v = self.b(si); si += 1; cx -= 1
                for k in range(nx):
                    out.append((v + (k if al == 0xF1 else 0)) & 0xFF)
            else:
                out.append(al)
        return out, si

    def codesets(self):
        """คืน dict name -> (i2a[256], a2i[256], params[6])"""
        sets = {}
        p = 0x2B0
        while self.b(p) != 0:
            name = bytes(self.d[p - BASE:p - BASE + 5]).decode('ascii').strip()
            i2a, si = self.chunk(p + 5)
            a2i, si = self.chunk(si)
            sets[name] = (i2a[:256], a2i[:256], i2a[256:262])
            p = si
        return sets


def internal_names(img=None):
    """internal code -> ข้อความอธิบาย (ตัวอักษรไทย ถ้ามี) ใช้ TIS เป็นตัวอ้างอิง"""
    img = img or Image()
    i2a, a2i, _ = img.codesets()['TIS']
    names = {}
    for c in range(256):
        t = i2a[c]
        if c < 0x80:
            names[c] = chr(c)
        elif t >= 0xA1 and t != 0xFF:
            names[c] = bytes([t]).decode('cp874', errors='replace')
        else:
            names[c] = None
    return names


if __name__ == '__main__':
    img = Image(sys.argv[1] if len(sys.argv) > 1 else 'THAID.COM')
    sets = img.codesets()
    ku = sets['KU']; tis = sets['TIS']
    print('| internal | TIS | KU | อักษร |')
    print('|---|---|---|---|')
    for c in range(0x80, 0x100):
        t, k = tis[0][c], ku[0][c]
        ch = bytes([t]).decode('cp874', errors='replace') if t >= 0xA1 and t != 0xFF else ''
        print(f'| {c:02X} | {t:02X} | {k:02X} | {ch} |')
    for n, (_, _, prm) in sets.items():
        print(f'params {n}: ' + ' '.join(f'{x:02X}' for x in prm))
