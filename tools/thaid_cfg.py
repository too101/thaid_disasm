#!/usr/bin/env python3
"""THAID.CFG: อ่าน/ตรวจ/สร้างไฟล์ตั้งค่า (โครงสร้างถอดจากตัวโหลดที่ 0x755A-0x7613)

  python tools/thaid_cfg.py dump THAID.CFG            ถอดโครงสร้างไฟล์ cfg
  python tools/thaid_cfg.py make THAID.COM out.CFG    สร้าง cfg จากค่าเริ่มต้นในภาพโปรแกรม

โครงสร้าง (offset ในไฟล์ cfg):
  +0  5 ไบต์   "THAID" (ตัวโหลดไม่ตรวจ ; ไฟล์ต้นฉบับใช้ข้อความนี้)
  +5  word     เวอร์ชัน ต้องเท่า word ที่ [0119h] ในภาพโปรแกรม (= 0203h : 03 02)
  +7  word     ขนาดไฟล์ทั้งหมด ต้องเท่าจำนวนไบต์ที่อ่านได้
  +9  byte     checksum = ผลรวมไบต์ทั้งไฟล์ (นับ +9 เป็น 0) mod 256
  (ไฟล์ต้นฉบับ 978 ไบต์ : บล็อกยาว 112, 729, 13, 106)
  +10 บล็อก 4 บล็อกต่อกัน แต่ละบล็อก = [ความยาว word][ข้อมูล] ก๊อปไปที่ (ที่อยู่ใน CS):
       1 -> 0110h  ค่าตั้งต้น/ตารางโหมด (ยาว 0x70 = 0110-017F)
       2 -> 02B0h  record ชุดรหัส (KU, TIS)  (ยาว 729 = 02B0-0588)
       3 -> 345Ch  ตารางสี OLSF + รหัส ESC/P ของ OLSF (ยาว 13 = 345C-3468 เฉพาะตารางสี)
       4 -> 4BD2h  ตารางการ์ด VGA (palette/sequencer/CRTC/GC) (ยาว 106 = 4BD2-4C3B)
ความยาวบล็อกที่ตัวโหลดยอมรับเป็นค่าใดก็ได้ ; ค่าข้างบนตรงกับไฟล์ THAID.CFG ต้นฉบับ
"""
import sys, struct
BASE = 0x100
BLOCKS = [(0x110, 0x70), (0x2B0, 0x2D9), (0x345C, 13), (0x4BD2, 0x6A)]  # ความยาวตามไฟล์ THAID.CFG ต้นฉบับ

def checksum(b):
    c = bytearray(b); c[9] = 0
    return sum(c) & 0xFF

def parse(b):
    ver, size, ck = struct.unpack_from('<HHB', b, 5)
    ok = {'size': size == len(b), 'checksum': ck == checksum(b)}
    blocks = []; p = 10
    for i in range(4):
        if p + 2 > len(b): break
        n = struct.unpack_from('<H', b, p)[0]
        blocks.append((p + 2, n)); p += 2 + n
    return ver, size, ck, ok, blocks, p

def make(com):
    d = open(com, 'rb').read()
    body = b''
    for addr, n in BLOCKS:
        body += struct.pack('<H', n) + d[addr - BASE: addr - BASE + n]
    ver = d[0x119 - BASE] | d[0x11A - BASE] << 8
    out = bytearray(b'THAID' + struct.pack('<HHB', ver, 10 + len(body), 0) + body)
    out[9] = checksum(out)
    return bytes(out)

if __name__ == '__main__':
    if len(sys.argv) >= 3 and sys.argv[1] == 'dump':
        b = open(sys.argv[2], 'rb').read()
        ver, size, ck, ok, blocks, end = parse(b)
        print(f'ไฟล์ {len(b)} ไบต์ | version word={ver:04X} | size field={size} {"OK" if ok["size"] else "ไม่ตรง"} | '
              f'checksum={ck:02X} {"OK" if ok["checksum"] else "ผิด (ควร %02X)" % checksum(b)}')
        for i, (off, n) in enumerate(blocks):
            print(f'  block {i+1}: file+{off:04X} ยาว {n} -> CS:{BLOCKS[i][0]:04X}  {b[off:off+16].hex(" ")} ...')
        if end != len(b): print(f'  ไบต์เกินท้ายบล็อกที่ 4: {len(b)-end}')
    elif len(sys.argv) >= 4 and sys.argv[1] == 'make':
        open(sys.argv[3], 'wb').write(make(sys.argv[2])); print('wrote', sys.argv[3])
    else:
        print(__doc__)
