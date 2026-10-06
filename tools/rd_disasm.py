#!/usr/bin/env python3
"""Recursive-descent disassembler for THAID.COM (DOS COM, 16-bit real mode).
Memory address = file offset + 0x100 (COM load segment offset)."""
import capstone, sys, json
from collections import deque

DATA = open('THAID.COM', 'rb').read()
BASE = 0x100            # COM image starts at offset 0x100 in the segment
SIZE = len(DATA)

md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_16)
md.detail = True

def f2m(foff):  # file offset -> memory address
    return foff + BASE

def m2f(addr):  # memory address -> file offset
    return addr - BASE

def read_at(addr, n):
    fo = m2f(addr)
    if 0 <= fo <= SIZE - n:
        return DATA[fo:fo+n]
    return b''

insns = {}          # addr -> capstone insn
targets = set()     # branch targets (labels)
calltargets = set() # call targets (functions)
ints_used = {}      # int number -> [addresses]
ports = []          # (addr, insn string)
indirect = []       # unresolved indirect jumps/calls
queue = deque()

def seed(addr, note=''):
    if addr not in insns and 0 <= m2f(addr) < SIZE:
        queue.append((addr, note))

seed(0x6FB9, 'entry point (first JMP of file)')

# Known code regions seen in hex (referenced as data/installed handlers) - seeded later
while queue:
    addr, note = queue.popleft()
    if addr in insns:
        continue
    # disassemble linearly until unconditional terminator or hit of already-seen
    a = addr
    while True:
        if a in insns:
            break
        fo = m2f(a)
        if fo < 0 or fo >= SIZE:
            break
        try:
            i = next(md.disasm(DATA[fo:fo+16], a))
        except StopIteration:
            break
        insns[a] = i
        if i.mnemonic.startswith('j') or i.mnemonic == 'loop':
            # branch
            if len(i.operands) == 1 and i.operands[0].type == capstone.x86.X86_OP_IMM:
                t = i.operands[0].imm
                targets.add(t)
                queue.append((t, 'branch'))
            else:
                indirect.append((a, i.mnemonic + ' ' + i.op_str))
        elif i.mnemonic == 'call':
            if len(i.operands) == 1 and i.operands[0].type == capstone.x86.X86_OP_IMM:
                t = i.operands[0].imm
                calltargets.add(t)
                targets.add(t)
                queue.append((t, 'call'))
            else:
                indirect.append((a, 'call ' + i.op_str))
        elif i.mnemonic in ('ret', 'retf', 'iret', 'iretd'):
            break
        elif i.mnemonic.startswith('int'):
            if len(i.operands) == 1 and i.operands[0].type == capstone.x86.X86_OP_IMM:
                n = i.operands[0].imm
                ints_used.setdefault(n, []).append(a)
        elif i.mnemonic in ('in', 'out'):
            ports.append((a, i.mnemonic + ' ' + i.op_str))
        elif i.mnemonic.startswith('jmp'):
            if len(i.operands) == 1 and i.operands[0].type == capstone.x86.X86_OP_IMM:
                t = i.operands[0].imm
                targets.add(t)
                queue.append((t, 'jmp'))
            else:
                indirect.append((a, 'jmp ' + i.op_str))
            break
        a += i.size

code_addrs = sorted(insns.keys())
lo, hi = code_addrs[0], code_addrs[-1]
coverage = sum(i.size for i in insns.values())
print(f"file size        : {SIZE} (0x{SIZE:X})")
print(f"code discovered  : {len(insns)} instructions, {coverage} bytes (0x{coverage:X})")
print(f"address range    : {lo:04X} .. {hi:04X}")
print(f"branch targets   : {len(targets)}, call targets: {len(calltargets)}")
print(f"indirect flows   : {len(indirect)}")
for a, s in indirect[:40]:
    print(f"   {a:04X}: {s}")
print("interrupts used  :", {f"{k:02X}h": len(v) for k, v in sorted(ints_used.items())})
print("ports used       :")
for a, s in ports:
    print(f"   {a:04X}: {s}")
print("\ncall targets (functions):")
for t in sorted(calltargets):
    print(f"   {t:04X}")

# gaps -> data regions
data_regions = []
prev = None
covered = set()
for i in insns.values():
    for b in range(i.address, i.address + i.size):
        covered.add(b)
out_of_code = [a for a in range(BASE, BASE + SIZE) if a not in covered]
# collapse to ranges
runs = []
start = None
last = None
for a in out_of_code:
    if start is None:
        start = last = a
    elif a == last + 1:
        last = a
    else:
        runs.append((start, last)); start = last = a
if start is not None:
    runs.append((start, last))
print(f"\ndata/unreached regions: {len(runs)}")
for s, e in runs[:80]:
    print(f"   {s:04X}-{e:04X} ({e-s+1} bytes)")

json.dump({
    'insn_bytes': {hex(a): i.size for a, i in insns.items()},
    'targets': sorted(hex(t) for t in targets),
    'calls': sorted(hex(t) for t in calltargets),
    'ints': {f"{k:02X}": v for k, v in ints_used.items()},
}, open('rd_map.json', 'w'))
print("\nsaved rd_map.json")
