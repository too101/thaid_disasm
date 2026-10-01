#!/usr/bin/env python3
"""สร้างซอร์สที่ assemble ได้ (GNU as, intel syntax) จาก THAID_disasm.asm แล้วพิสูจน์ว่า build ออกมาเหมือน THAID.COM ทุกไบต์

หลักการ: คำสั่งที่ assembler เข้ารหัสได้เหมือนต้นฉบับทุกไบต์ -> ปล่อยเป็นคำสั่งจริง (มี label แทน address กระโดด)
          คำสั่งที่ assemble ไม่ได้ / เข้ารหัสต่างจากเดิม (เช่น jmp short/near, mov 88/8A, self-modifying) -> .byte พร้อมคอมเมนต์คำสั่งเดิม
ใช้: python tools/gen_source.py   (ต้องมี THAID.COM, THAID_disasm.asm และ binutils: as, ld)
ผล: THAID_src.s  และ build/THAID_rebuilt.COM  (+ เทียบกับ THAID.COM)"""
import os, re, subprocess, sys

ORG = 0x100
COM = open('THAID.COM', 'rb').read()
LINE_I = re.compile(r'^([0-9A-F]{4})  ((?:[0-9a-f]{2})+)\s+(\S.*?)(?:\s+;.*)?$')
LINE_D = re.compile(r'^([0-9A-F]{4})  db  ')

# ---- 1) อ่าน listing: instruction ที่ address -> (len, text) ----
ins = {}
for ln in open('THAID_disasm.asm', encoding='utf-8'):
    ln = ln.rstrip('\n')
    if LINE_D.match(ln):
        continue
    m = LINE_I.match(ln)
    if m:
        a = int(m.group(1), 16)
        b = bytes.fromhex(m.group(2))
        ins[a] = (len(b), m.group(3).strip())

# ---- 2) ลำดับรายการเรียงตาม address ครอบคลุมทั้งไฟล์ (ช่องว่าง = db จากไบต์จริง) ----
items = []            # (addr, kind, payload)  kind: 'i' (instr) / 'd' (bytes)
pos = ORG
end = ORG + len(COM)
for a in sorted(ins):
    if a < pos:
        continue                          # ซ้อนกัน (ไม่ควรเกิด)
    if a > pos:
        items.append((pos, 'd', COM[pos - ORG:a - ORG]))
    n, txt = ins[a]
    if COM[a - ORG:a - ORG + n] != bytes.fromhex(re.search(r'^%04X  ((?:[0-9a-f]{2})+)' % a, '')) if False else False:
        pass
    items.append((a, 'i', (n, txt)))
    pos = a + n
if pos < end:
    items.append((pos, 'd', COM[pos - ORG:]))

starts = {a for a, _, _ in items}
JMP = re.compile(r'^(call|jmp|j[a-z]+|loop[a-z]*|jcxz)\s+(0x[0-9a-fA-F]+)$')

def fix_text(txt):
    """ปรับ syntax capstone -> gas intel"""
    m = JMP.match(txt)
    if m:
        t = int(m.group(2), 16)
        return f"{m.group(1)} A_{t:04X}" if t in starts else None
    txt = re.sub(r'\bptr (cs|ds|es|ss):\[', r'ptr \1:[', txt)
    return txt

fallback = set()      # address ที่ต้อง .byte


def emit():
    out = ['# THAID_src.s -- สร้างอัตโนมัติด้วย tools/gen_source.py (อย่าแก้ที่นี่ ; คอมเมนต์ไทยอยู่ใน THAID_disasm.asm)',
           '# build: as --32 -o THAID.o THAID_src.s && ld -m elf_i386 -Ttext=0x100 --oformat binary -o THAID.COM THAID.o',
           '.code16', '.intel_syntax noprefix', '.text', '.globl _start', '_start:']
    for a, k, p in items:
        out.append(f'A_{a:04X}:')
        if k == 'd':
            for i in range(0, len(p), 16):
                out.append('    .byte ' + ','.join('0x%02x' % x for x in p[i:i + 16]))
        else:
            n, txt = p
            t = None if a in fallback else fix_text(txt)
            if t is None:
                out.append('    .byte ' + ','.join('0x%02x' % x for x in COM[a - ORG:a - ORG + n]) + f'    # {txt}')
            else:
                out.append('    ' + t)
    # label ท้ายไฟล์
    out.append(f'A_{end:04X}:')
    return out


def build(lines):
    os.makedirs('build', exist_ok=True)
    open('build/THAID_src.s', 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    r = subprocess.run(['as', '--32', '-o', 'build/THAID.o', 'build/THAID_src.s'], capture_output=True, text=True)
    return r


def line_to_addr(lines):
    cur = None
    m = {}
    for i, l in enumerate(lines, 1):
        mm = re.match(r'^A_([0-9A-F]{4}):$', l)
        if mm:
            cur = int(mm.group(1), 16)
        m[i] = cur
    return m

for rnd in range(60):
    lines = emit()
    r = build(lines)
    bad = set()
    if r.returncode != 0:
        l2a = line_to_addr(lines)
        for mm in re.finditer(r'THAID_src\.s:(\d+): Error', r.stderr):
            a = l2a.get(int(mm.group(1)))
            if a is not None and a in ins:
                bad.add(a)
        if not bad:
            print(r.stderr[:2000]); sys.exit('assemble error without known line')
    else:
        subprocess.run(['ld', '-m', 'elf_i386', '-Ttext=0x100', '--oformat', 'binary', '-o', 'build/THAID_rebuilt.COM', 'build/THAID.o'], check=True)
        new = open('build/THAID_rebuilt.COM', 'rb').read()
        if new == COM:
            break
        # หาทุกคำสั่งที่ขนาดหรือไบต์ต่างจากต้นฉบับในรอบเดียว (ใช้ตำแหน่ง label ใน object)
        nm = subprocess.run(['nm', 'build/THAID.o'], capture_output=True, text=True).stdout
        pos_of = {}
        for l in nm.splitlines():
            mm = re.match(r'^([0-9a-f]+) \w A_([0-9A-F]{4})$', l)
            if mm:
                pos_of[int(mm.group(2), 16)] = int(mm.group(1), 16)
        addrs = [a for a, _, _ in items] + [end]
        for i in range(len(addrs) - 1):
            a0, a1 = addrs[i], addrs[i + 1]
            if a0 not in ins:
                continue
            want = a1 - a0
            got = pos_of[a1] - pos_of[a0]
            nb = new[pos_of[a0]:pos_of[a1]]
            if got != want:
                bad.add(a0)
            elif not JMP.match(ins[a0][1]) and nb != COM[a0 - ORG:a1 - ORG]:
                bad.add(a0)
        if not bad:
            # เหลือแต่คำสั่งกระโดดที่ไบต์ต่าง (ความยาวเท่ากัน) -> ให้ fallback ทั้งหมดที่ต่าง
            for i in range(len(addrs) - 1):
                a0, a1 = addrs[i], addrs[i + 1]
                if a0 in ins and new[pos_of[a0]:pos_of[a1]] != COM[a0 - ORG:a1 - ORG]:
                    bad.add(a0)
    new_bad = bad - fallback
    if not new_bad:
        sys.exit(f'ไม่คืบหน้า: {sorted(bad)[:5]}')
    fallback |= new_bad
    print(f'round {rnd}: +{len(new_bad)} fallback (total {len(fallback)})')
else:
    sys.exit('ไม่ลู่เข้าใน 60 รอบ')

open('THAID_src.s', 'w', encoding='utf-8').write('\n'.join(emit()) + '\n')
real = len(ins) - len(fallback)
print(f'OK: build/THAID_rebuilt.COM == THAID.COM ({len(COM)} ไบต์) ; คำสั่งจริง {real}/{len(ins)} ({100 * real / len(ins):.1f}%), .byte fallback {len(fallback)}')
