#!/usr/bin/env python3
"""ทดสอบตัวตรวจ/โหลด THAID.CFG ของจริง (0x75BA-0x7613) ด้วย unicorn : python tools/emu_check_cfg.py THAID.COM X.CFG"""
import sys
from unicorn import *
from unicorn.x86_const import *
com, cfg = open(sys.argv[1], 'rb').read(), open(sys.argv[2], 'rb').read()
SEG = 0x1000; lin = SEG << 4
mu = Uc(UC_ARCH_X86, UC_MODE_16); mu.mem_map(0x10000, 0x20000)
mu.mem_write(lin + 0x100, com)
mu.mem_write(lin + 0x7618, cfg)
for r in (UC_X86_REG_CS, UC_X86_REG_DS, UC_X86_REG_ES, UC_X86_REG_SS):
    mu.reg_write(r, SEG)
mu.reg_write(UC_X86_REG_SP, 0xFFF0)
mu.reg_write(UC_X86_REG_AX, len(cfg))      # AX = จำนวนไบต์ที่อ่านได้ (ผลของ INT 21h/3Fh)
before = bytes(mu.mem_read(lin + 0x6FB0, 1))[0]
mu.reg_write(UC_X86_REG_IP, 0x75BA)
# ret ที่ 75F5 (ผิด) / ตัวก๊อปบล็อกจบที่ 7613 (ถูก) : ใส่ ret ไว้ที่ 7613 แล้วหยุดที่ 0x7614
try:
    mu.mem_write(lin + 0xFFF0, b'\x14\x76')   # ที่อยู่ย้อนกลับ 7614h
    mu.emu_start(lin + 0x75BA, lin + 0x7614, count=300000)
except UcError as e:
    print('emu error', e)
err = bytes(mu.mem_read(lin + 0x6FB0, 1))[0]
print('[6FB0h] (0=ใช้ได้ 1=ไม่พบไฟล์ 2=ขนาด/checksum ผิด 3=เวอร์ชันผิด)=', err)
if err == 0:
    import struct
    p = 10
    for addr in (0x110, 0x2B0, 0x345C, 0x4BD2):
        n = struct.unpack_from('<H', cfg, p)[0]; p += 2 + n
        got = bytes(mu.mem_read(lin + addr, n)); ref = com[addr - 0x100:addr - 0x100 + n]
        print(f'  {addr:04X}+{n:X}: {"ตรงกับค่าเริ่มต้นในภาพ" if got == ref else "ต่างจากค่าเริ่มต้นในภาพ (%d ไบต์)" % sum(a != b for a, b in zip(got, ref))}')
