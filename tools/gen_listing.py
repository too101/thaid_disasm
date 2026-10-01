#!/usr/bin/env python3
"""Generate annotated full disassembly listing for THAID.COM"""
import capstone
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from collections import deque

DATA = open('THAID.COM', 'rb').read()
BASE = 0x100
SIZE = len(DATA)
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_16)
md.detail = True

SEEDS = [
    (0x6FC9, 'ENTRY: THAID.COM main (file starts with E9 C6 6E -> jmp 6FC9)'),
    (0x756A, 'install-check / config loader (find THAID.CFG, checksum, reload tables)'),
    (0xC0,   'INT A8h handler (code translate via table at 0040h; lives in PSP, copied from 6E70h)'),
    (0x251,  'INT 21h hook - DOS filter'),
    (0x8D2,  'INT 5Dh private API'),
    (0x8D6,  'INT 5Eh private API'),
    (0x8DA,  'INT 5Fh private API'),
    (0x8DE,  'INT 60h private API'),
    (0x1227, 'INT 8 timer hook - screen refresh / clock'),
    (0x250F, 'INT 9 keyboard hook - hotkey + Thai key dispatch'),
    (0x1AD3, 'INT 10h video hook - dispatcher'),
    (0x1B50, 'INT 10h part 2 (mode/set/write)'),
    (0x1B2B, 'INT 10h AH=9/A write char/attr own path'),
    (0x1C50, 'INT 10h AH=6 scroll'),
    (0x1D53, 'INT 10h AH=E teletype'),
    (0x2689, 'INT 16h keyboard hook'),
    (0x2D6D, 'INT 17h printer hook - Thai printer driver'),
    (0x1155, 'cursor -> CRTC remap helper'),
    (0x115E, 'cursor compose helper (3-level line scan)'),
    (0x11E0, 'char level classifier helper'),
    (0x1116, 'cursor position update / CRTC write'),
    (0x120C, 'timer tick work'),
    (0x126F, 'timer: rebuild 25 physical rows'),
    (0x1655, 'row renderer: compare virtual vs physical, compose'),
    (0x146C, 'render helper (option flag 0x120)'),
    (0x14FD, '3-level cell composition'),
    (0x1931, 'CRTC start-address / mode refresh'),
    (0x19BF, 'clear virtual buffer page'),
    (0x19D7, 'clear render buffer page'),
    (0x19E5, 'set mode / page switch'),
    (0x1BDC, 'read CRTC cursor regs'),
    (0x1BFC, 'write CRTC start/end regs'),
    (0x1E40, 'INT10 private AH=90h-98h dispatcher'),
    (0x1EDE, 'private: write Thai string to screen'),
    (0x1EF2, 'private: write raw/codepage string'),
    (0x4A25, 'OLSF menu entry (called on Ctrl+Ins)'),
    (0x2174, 'Ctrl+F2 cycle display mode'),
    (0x219B, 'Ctrl+F3 switch screen code set'),
    (0x21B0, 'Ctrl+F1 toggle box auto-adjust'),
    (0x21BA, 'Ctrl+F5 toggle [11Dh] bit1'),
    (0x21D0, 'Ctrl+F4 toggle status labels/beep'),
    (0x0A8E, '9B-command handler'),
    (0x0AD6, '9B-command handler'),
    (0x0B5F, '9B-command handler'),
    (0x0B74, '9B-command handler'),
    (0x0BA5, '9B-command handler'),
    (0x0BC7, '9B-command handler'),
    (0x0C27, '9B-command handler'),
    (0x0C4A, '9B-command handler'),
    (0x0C69, '9B-command handler'),
    (0x0C91, '9B-command handler'),
    (0x0CAF, '9B-command handler'),
    (0x0CB7, '9B-command handler'),
    (0x0CC6, '9B-command handler'),
    (0x0CED, '9B-command handler'),
    (0x0D3F, '9B-command handler'),
    (0x0D66, '9B-command handler'),
    (0x0E20, '9B-command handler'),
    (0x1E24, 'private video entry (INT A8h?)'),
    (0x48FA, 'OLSF: prev item'),
    (0x4935, 'OLSF: next item'),
    (0x4968, 'OLSF: decrease'),
    (0x4987, 'OLSF: increase/toggle'),
    (0x49D9, 'OLSF: enter'),
    (0x4AE6, 'OLSF: no-op'),
    (0x4AE7, 'OLSF: Esc'),
    (0x4B58, 'OLSF: send printer setup'),
    (0x4B90, 'VGA card routine (XTRA mode)'),
    (0x4C4C, 'VGA: full mode reprogram'),
    (0x4D00, 'VGA: write register table'),
    (0x4D12, 'VGA: font copy rows'),
    (0x4D20, 'VGA: font copy from ext ptr'),
    (0x4D7C, 'VGA: load Thai font to plane 2'),
    (0x2E36, 'printer driver'),
    (0x2E75, 'printer driver'),
    (0x2EF6, 'printer driver'),
    (0x2F07, 'printer driver'),
    (0x2F18, 'printer driver'),
    (0x2F2D, 'printer driver'),
    (0x2F36, 'printer driver'),
    (0x2F3D, 'printer driver'),
    (0x2F4B, 'printer driver'),
    (0x2F51, 'printer driver'),
    (0x2F97, 'printer driver'),
    (0x2FBC, 'printer driver'),
    (0x2FDE, 'printer driver'),
    (0x2FE8, 'printer driver'),
    (0x3014, 'printer driver'),
    (0x301C, 'printer driver'),
    (0x3038, 'printer driver'),
    (0x3047, 'printer driver'),
    (0x305F, 'printer driver'),
    (0x3079, 'printer driver'),
    (0x308E, 'printer driver'),
    (0x309D, 'printer driver'),
    (0x30B5, 'printer driver'),
    (0x30BF, 'printer driver'),
    (0x30C6, 'printer driver'),
    (0x30C9, 'printer driver'),
    (0x30D1, 'printer driver'),
    (0x30E3, 'printer driver'),
    (0x3103, 'printer driver'),
    (0x3116, 'printer driver'),
    (0x3131, 'printer driver'),
    (0x3146, 'printer driver'),
    (0x3150, 'printer driver'),
    (0x315A, 'printer driver'),
    (0x3161, 'printer driver'),
    (0x316C, 'printer driver'),
    (0x3173, 'printer driver'),
    (0x3189, 'printer driver'),
    (0x3192, 'printer driver'),
    (0x319B, 'printer driver'),
    (0x31A4, 'printer driver'),
    (0x31CC, 'printer driver'),
    (0x3230, 'printer driver'),
    (0x323D, 'printer driver'),
    (0x3244, 'printer driver'),
    (0x325C, 'printer driver'),
    (0x3264, 'printer driver'),
    (0x3286, 'printer driver'),
    (0x3296, 'printer driver'),
    (0x32A8, 'printer driver'),
    (0x330C, 'printer driver'),
    (0x3333, 'printer driver'),
    (0x33B3, 'printer driver'),
    (0x341E, 'printer driver'),
    (0x1E5C, 'INT10 private'),
    (0x1E65, 'INT10 private'),
    (0x1E9A, 'INT10 private'),
    (0x1F17, 'INT10 private'),
    (0x1F1D, 'INT10 private'),
    (0x7546, 'init: abort file size error'),
    (0x0A3E, 'in-band 9Bh command recogniser idle'),
    (0x0A61, 'in-band 9Bh command wait-command'),
    (0x1ACC, 'INT 10h AH=9/A: 9Bh swallowed path'),
    (0x268E, 'INT 16h normal state'),
    (0x26E1, 'INT 16h second-char pending state'),
    (0x2D72, 'INT 17h main path'),
    (0x2DB1, 'INT 17h filter idle state'),
    (0x2DBD, 'INT 17h filter collect state'),
    (0x2ECE, "internal printer driver byte-out"),
    (0x2EC1, "INT 17h alt driver"),
    (0x32BA, 'printer char translate'),
    (0x2436, 'mode-change status redraw'),
    (0x24C8, 'timer status work'),
    (0x2142, 'hotkey 2 check'),
    (0x219,  'low-level copy helper (jmp from 70D8)'),
    (0x70DB, 'init: locate THAID.CFG data / EMS probe'),
    (0x7109, 'init: save IVT copy + BIOS data'),
    (0x714C, 'init: font setup + get BIOS font'),
    (0x71BC, 'init: install INT 9'),
    (0x71F0, 'init: install INT 16h/17h'),
    (0x723B, 'init: install INT 21h + 5Dh-60h + A8h + INT 8'),
    (0x72A5, 'init: clear buffers, call 6EF7, set video'),
    (0x72E0, 'init: banner messages + TSR terminate (int 27h / retf 0x7A3F)'),
    (0x733A, 'int 27h site'),
    (0x7452, 'exit: file size error path'),
    (0x7541, 'print $-string helper'),
    (0x7546, 'exit: virus/size error'),
    (0x754D, 'exit: version mismatch'),
    (0x7554, 'exit: already installed'),
    (0x7559, 'exit common'),
    (0x7606, 'install-check ok: load 4 tables from THAID.CFG'),
    (0x761E, 'copy length-prefixed block helper'),
    # --- renderer state machine (self-modifying jmp at 16EFh, operand 16F0h) ---
    (0x12B0, 'INT 8 state 007Fh: partial rebuild around cursor (SMC target of call at 122Eh)'),
    (0x1232, 'INT 8 state 0001h: cursor sync (SMC target of call at 122Eh)'),
    (0x120C, 'INT 8 initial state FFDBh (SMC target of call at 122Eh)'),
    (0x1736, 'render state S0: line start / no column lost yet'),
    (0x179A, 'render state CONS: after consonant (from S0)'),
    (0x17A4, 'render state CONS2: after consonant (from AFTER)'),
    (0x17E7, 'render state V1: consonant + first vowel C3h-C9h (tone may stack)'),
    (0x176C, 'render state AFTER: columns lost -> vowel compensation active'),
    (0x186A, 'render state COMP: counting run of space/special char'),
    (0x172F, 'render: reset state S0 + reprocess'),
    (0x1765, 'render: set state AFTER + reprocess'),
    (0x131B, 'vowel+tone precompose via table 0F17h'),
    (0x1335, 'box-drawing connectivity lookup (table 0E2Eh)'),
    (0x134A, 'box auto-fix path (SMC jmp 142Eh)'),
    (0x138E, 'box auto-fix path (SMC jmp 142Eh)'),
    (0x1373, 'box auto-fix: walk run of line chars'),
    (0x13E0, 'box auto-fix: per-char check'),
    (0x1A2B, 'SMC target of jmp 1AB0h'),
    (0x1B0E, 'SMC target of jmp 1AB0h'),
    (0x09EF, 'code-set RLE decoder (F1=ascending run, F0=repeat)'),
    (0x0949, 'select printer code set -> table 59Ch'),
    (0x08E5, 'select screen code set -> tables 6A2h/7A2h + status label'),
]

insns = {}
queue = deque(SEEDS)
while queue:
    addr, note = queue.popleft()
    if addr in insns:
        continue
    a = addr
    while True:
        if a in insns:
            break
        fo = a - BASE
        if fo < 0 or fo >= SIZE:
            break
        try:
            i = next(md.disasm(DATA[fo:fo+16], a))
        except StopIteration:
            break
        insns[a] = i
        m = i.mnemonic
        if m in ('ret', 'retf', 'iret'):
            break
        if len(i.operands) == 1 and i.operands[0].type == capstone.x86.X86_OP_IMM:
            t = i.operands[0].imm
            if 0x100 <= t < SIZE + BASE:
                queue.append((t, 'flow'))
                if m in ('ret', 'retf', 'iret'):
                    break
        if m.startswith('jmp'):
            break
        if m == 'int' and len(i.operands) == 1 and i.operands[0].imm == 0x27:
            break   # INT 27h = terminate-and-stay-resident, never returns
        a += i.size

covered = {}
for a, i in insns.items():
    covered[a] = i.size

OUT = open('THAID_disasm.asm', 'w', encoding='utf-8')
W = OUT.write

def label(a):
    return f"L{a:04X}"

# annotate known labels
ANN = {
    0x6FC9: 'ENTRY POINT (COM header jmp 6FC9)',
    0x251: 'INT 21h handler (hooked AH=25h, al=21h)',
    0x8D2: 'INT 5Dh', 0x8D6: 'INT 5Eh', 0x8DA: 'INT 5Fh', 0x8DE: 'INT 60h',
    0xC0: 'INT A8h code translate (PSP)',
    0x1227: 'INT 8 handler (hooked)', 0x250F: 'INT 9 handler (hooked)',
    0x1AD3: 'INT 10h handler (hooked)', 0x2689: 'INT 16h handler (hooked)',
    0x2D6D: 'INT 17h handler (hooked)',
    0x733F: 'TSR: int 27h terminate',
    0x7541: 'PRINT $-STRING',
    0x16EF: 'SMC: jmp <state>  (operand word at 16F0h = state - 16F2h)',
    0x09EF: 'code-set RLE decoder',
}

W("; =====================================================================\n")
W("; THAID.COM - ThaiD v2.3, MicroWiz (c) 1988-1992\n")
W("; Full annotated disassembly for EDUCATIONAL study (8086 real mode, COM)\n")
W("; Generated by recursive-descent disassembler (capstone), seeds = entry +\n")
W(";   all interrupt vector targets + manually traced functions.\n")
W("; Memory address = file offset + 100h (COM convention, org 100h).\n")
W("; NOTE: region 7624h-B110h is unused tail data (never referenced or executed;\n")
W(";   the real image ends at 7627h) - shown as hex data.\n")
W("; =====================================================================\n\n")
W("        org     100h\n\nstart:\n")

sections = [
    (0x100,  0x1C7,  'HEADER: version "Version 2.3", KU/TIS char-order tables,\n;         default config blocks ("KU  F", "TIS E"), copyright'),
    (0x1C7,  0x21E,  'RESIDENT: common prologues (PSQRW = pushed regs)'),
    (0x21E,  0x59C,  'RESIDENT: INT 21h filter + helpers'),
    (0x59C,  0x637,  'INIT-ONLY: build code-set record list [590h] (KU @2B0h, TIS @33Ch);\n;         overwritten after install by printer table [59Ch] (internal -> printer code)'),
    (0x637,  0x8E2,  'TABLES: [6A2h] internal -> app code, [7A2h] app code -> internal (filled at runtime)\n;         + INT 5Dh-60h lookup helpers'),
    (0x8E2,  0xA2F,  'RESIDENT: private INT 5Dh-60h API bodies'),
    (0xA2F,  0xC7,   None),
    (0xA2F,  0x10BA, 'RESIDENT: "MicroWizSSF" area, helpers, level tables (0F09h = upper-vowel set)'),
    (0x10BA, 0x1227, 'RESIDENT: CRTC cursor/page tables + cursor remap (row table 1C0Ch)'),
    (0x1227, 0x1554, 'RESIDENT: INT 8 timer - row rebuild, cursor fix, box auto-fix pre-pass'),
    (0x1554, 0x1655, 'TABLE 1554h: internal code -> LOWER-band glyph (font block 1, attr bit3=1)\n;         consonant tails 80h-95h; OR 20h/40h/60h = +sara u/uu/phinthu'),
    (0x1655, 0x1910, 'RESIDENT: row renderer - state machine via self-modifying jmp 16EFh\n;         app cell -> 3 bands: [di-0A2h]=upper, [di]=middle, [di+9Eh]=lower'),
    (0x1910, 0x19BF, 'RESIDENT: INT10 dispatch table + CRTC refresh'),
    (0x19BF, 0x1AD3, 'RESIDENT: buffer clears + mode switch'),
    (0x1AD3, 0x1C0C, 'RESIDENT: INT 10h dispatcher + AH=9/A/6/E paths + CRTC wr'),
    (0x1C0C, 0x1E40, 'RESIDENT: ROW TABLE (25 entries: row -> offset*160) + scroll/teletype + CRTC'),
    (0x1E40, 0x1FBC, 'RESIDENT: private INT10 AH=90h-98h + string width (zero-width chars C3h-D1h)'),
    (0x1FBC, 0x2142, 'RESIDENT: "MicroWizKBD" id, BORDER/ENG status templates, Kedmanee key tables'),
    (0x2142, 0x2689, 'RESIDENT: INT 9 helpers (hotkeys, status line)'),
    (0x2689, 0x2D6D, 'RESIDENT: INT 16h handler'),
    (0x2D6D, 0x2E36, 'RESIDENT: INT 17h printer hook'),
    (0x2E36, 0x3460, 'RESIDENT: key translation tables + helpers'),
    (0x3460, 0x4B90, 'RESIDENT: OLSF "OnLine Setup Facility" menu (Ctrl-Ins) + printer setup strings'),
    (0x4B90, 0x6DF0, 'VGA card routine + tables (4B90-4DEF), then FONT BITMAPS 4DF0-6DEF (four 8x6 sets + Thai 8x16 set,\n;         copied to card RAM at install; ends exactly at resident cut 6DF0h)'),
    (0x6DF0, 0x6E81, 'CONFIG defaults (145-byte template copied to 40:40h...) + install sigs'),
    (0x6E81, 0x6EF7, 'Version banner: "X T R A  MEGA V DRIVER", RAM-BIOS v1.0'),
    (0x6EF7, 0x6FC9, 'INIT: video mode detect, banner print'),
    (0x6FC9, 0x7624, 'INIT: main + option parse (/o/m/v/r/h) + vector install + TSR terminate\n;         + messages (virus warning, THAID.CFG, already-installed...)'),
    (0x7624, 0xB110, 'UNUSED TAIL DATA (not referenced; real image ends at 7627h)'),
]

SEEDNOTE = {x: n for x, n in SEEDS if n != 'flow'}
emitted = set()
COVERED_SORTED = sorted(covered)
import bisect
from annotations import BLOCK, INLINE, LABELS


def next_covered(a, limit):
    """ที่อยู่ instruction ตัวถัดไปที่ > a (ไม่เกิน limit)"""
    i = bisect.bisect_right(COVERED_SORTED, a)
    return min(COVERED_SORTED[i], limit) if i < len(COVERED_SORTED) else limit


def emit_blocks(lo, hi):
    """พิมพ์ block comment ที่ชี้เข้าช่วง [lo, hi)"""
    for k in sorted(BLOCK):
        if lo <= k < hi and k not in emitted_blocks:
            emitted_blocks.add(k)
            W("\n")
            for line in BLOCK[k].strip('\n').split('\n'):
                W(f"; {line}\n" if line else ";\n")


emitted_blocks = set()
for s, e, title in sections:
    if title:
        W(f"\n; ---------------------------------------------------------------------\n; {title}\n; ---------------------------------------------------------------------\n")
    a = s
    while a < e:
        if a in covered and a not in emitted:
            i = insns[a]
            emitted.add(a)
            emit_blocks(a, a + i.size)
            ann = ANN.get(a, '') or SEEDNOTE.get(a, '') or LABELS.get(a, '')
            lbl = f"{label(a)}:" if a in SEEDNOTE or a in LABELS or ann else ''
            if lbl:
                W(f"\n{lbl:<22}; {ann}\n" if ann else f"\n{lbl}\n")
            line = f"{i.address:04X}  {i.bytes.hex():<16} {i.mnemonic} {i.op_str}"
            note = INLINE.get(a)
            W(f"{line:<52}; {note}\n" if note else line + "\n")
            a += i.size
        else:
            n = next_covered(a, min(a + 16, e)) - a       # อย่าให้ db ทับ instruction ที่ตามมา
            emit_blocks(a, a + n)
            fo = a - BASE
            chunk = DATA[fo:fo + n]
            W(f"{a:04X}  db  " + ", ".join(f"{b:02X}h" for b in chunk) + "\n")
            a += n

# ตรวจว่า annotation ทุกตัวชี้ไปที่ที่อยู่ที่ถูกพิมพ์จริง
_bad = [hex(k) for k in INLINE if k not in emitted]
_badb = [hex(k) for k in BLOCK if k not in emitted_blocks]
if _bad or _badb:
    print("WARNING annotation ไม่ตรง instruction:", _bad, "block:", _badb)
OUT.close()
print("written THAID_disasm.asm,", len(insns), "instructions")
