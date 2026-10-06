#!/usr/bin/env python3
"""ถอดโครงสร้างเมนู OLSF (บล็อกที่เรียกด้วย 0x4716)

รูปแบบที่อ่านจากโค้ด 0x4716 / 0x45F7 / 0x46EC / 0x465C / 0x483D :
  บล็อกเมนู  : [word ตำแหน่งจอ DI][byte CL][byte BL] (กรอบ)
               ตามด้วยระเบียนกรอบ 4 ไบต์ [อักขระ][attr][word pos] (ใช้ถมพื้น 0x23 คำ) ... จบด้วย attr=00 (0x45F7)
               ตามด้วยระเบียนข้อความ [attr][word pos][ข้อความ internal-KU จบด้วย 00] ... จบด้วย 1Ah (0x46EC)
               ตามด้วยตารางรายการ 10 ไบต์ จบด้วยไบต์ flags = 00
  รายการ 10 ไบต์ : +0 flags (01 ตัวนับวนตามจำนวนตัวเลือก, 02 บิตมาสก์ xor, 04 ทางเข้าเมนูย่อย, 08 กด ENTER เรียกฟังก์ชัน, 80 = รายการนี้ขึ้นกับรายการก่อนหน้า (ถูกข้ามตอนเลื่อนถ้าสวิตช์ของรายการก่อนหน้า var&mask = 0), 40 = กลับขั้ว (ใช้ได้เมื่อรายการก่อนหน้า = 0))
                   +1 word ตำแหน่งจอ  +3 word ชี้ "สเปกค่า" (FFh = ตัวเลข ; อื่น ๆ = ชุดข้อความตัวเลือก)
                   +5 word ที่อยู่ตัวแปร  +7 byte มาสก์  +8 word ชี้ข้อความช่วยเหลือ (ไบต์แรก = ความยาว)
  attr : <=7 = ดัชนีสี (ตาราง [345Ch]) ; >7 = แอตทริบิวต์ตัวอักษรตรง ๆ (เช่น C1, C2, FC) -- ไม่ใช่รหัสอักขระ
ใช้: python tools/olsf_dump.py [addr ...]   (ปริยาย: เมนูหลัก 0x442C และเมนูย่อย 0x3FB1 0x414F 0x420F 0x42EC)
"""
import sys
from thaid_ku import ku_decode, IMG
D = IMG.d
def b(a): return D[a - 0x100]
def w(a): return b(a) | (b(a + 1) << 8)
def cstr(a):
    s = a
    while b(a): a += 1
    return D[s - 0x100:a - 0x100], a + 1

def dump(a):
    print(f'== block {a:04X}')
    print(f'  head: di={w(a):04X} cl={b(a+2):02X} bl={b(a+3):02X}'); a += 4
    # กรอบ: 4607 อ่าน word attr, word pos, ข้าม 4 ไบต์ จนกว่าไบต์แรก = 0
    while b(a):
        print(f'  fill  ch={b(a):02X} attr={b(a+1):02X} pos={w(a+2):04X}'); a += 4
    a += 1
    while b(a) != 0x1A:
        s, n = cstr(a + 3)
        print(f'  text  attr={b(a):02X} pos={w(a+1):04X} {ku_decode(s, False)!r}')
        a = n
    a += 1
    print(f'  items @ {a:04X}')
    while b(a):
        f, pos, spec, var, mask, hlp = b(a), w(a+1), w(a+3), w(a+5), b(a+7), w(a+8)
        hs = D[hlp-0x100+1:hlp-0x100+1+b(hlp)]
        sp = D[spec-0x100:spec-0x100+8].hex(' ')
        names = [n for bit, n in ((0x80, 'dep' if not f & 0x40 else 'dep-inv'), (0x08, 'enter'), (0x04, 'submenu'), (0x02, 'mask'), (0x01, 'list')) if f & bit]
        print(f'  item fl={f:02X}({"+".join(names)}) pos={pos:04X} spec@{spec:04X}[{sp}] var={var:04X} mask={mask:02X} help={ku_decode(hs, False)!r}')
        a += 10
    print(f'  end @ {a:04X}')

if __name__ == '__main__':
    for x in (sys.argv[1:] or ['0x442C', '0x3FB1', '0x414F', '0x420F', '0x42EC']):
        try: dump(int(x, 16))
        except Exception as e: print('ERR', x, e)
