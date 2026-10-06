# thaid_disasm

ถอดรหัส (disassembly) โปรแกรม **ThaiD v2.3.88** (August 1993) — Thai Driver ของ MicroWiz
สำหรับ DOS: จัดการแสดงผลจอ (ไทย 3 ระดับ + บรรทัดสถานะ 26), เครื่องพิมพ์ และคีย์บอร์ด
เพื่อ**การศึกษา**เท่านั้น — binary ลิขสิทธิ์ MicroWiz (ไม่ commit `THAID.COM` ไว้ใน repo — ไฟล์ที่วิเคราะห์ขนาด 29,976 ไบต์ เป็นภาพโปรแกรมล้วนไม่มีส่วนต่อท้าย ; `tools/T91.COM` เป็นโปรแกรมทดสอบที่เขียนเอง)

## ไฟล์

| ไฟล์ | คำอธิบาย |
|---|---|
| [THAID_ANALYSIS.md](THAID_ANALYSIS.md) | รายงานถอดรหัสฉบับเต็ม (ภาษาไทย) — แผนที่ไฟล์, interrupt hooks, กลไกจอ 3 ระดับ, Mark & Release ของ TurboPower, รหัส KU/TIS |
| [THAID_disasm.asm](THAID_disasm.asm) | Full annotated listing (org 100h, ~7,700 บรรทัด / ~5,300 instruction, คำอธิบายภาษาไทยทุกส่วนที่เป็นโค้ด, label รูป `L1AD3` = ที่อยู่ CS:offset) |
| THAID_strings.txt | สตริงที่ดึงได้ : (1) ASCII (2) ไทยแบบ CP874 (ส่วนใหญ่อ่านไม่ออก เพราะไฟล์ใช้รหัสภายใน) (3) ข้อความเมนู OLSF ถอดด้วยรหัสภายใน KU-THAID อ่านได้ |
| `tools/rd_disasm.py` | Recursive-descent disassembler (capstone) |
| `tools/gen_listing.py` | สร้าง listing — แก้ `SEEDS` เพื่อเจาะโซนที่สนใจ (ไม่ disassemble ต่อหลัง `int 27h`) |
| `tools/gen_source.py` | สร้าง `THAID_src.s` (GNU as, intel syntax) จาก listing แล้ว build เป็น COM ที่**เหมือน THAID.COM ทุกไบต์** (คำสั่งจริง ~91%, ที่เหลือ `.byte` เพราะ assembler เลือกรหัสต่าง) — ผลลัพธ์ไม่ commit (เทียบเท่า binary) |
| `tools/annotations.py` | คำอธิบายภาษาไทยทั้งหมด (BLOCK / INLINE / LABELS) ที่ gen_listing.py ฝังลง listing — **แก้คำอธิบายที่นี่ ไม่ใช่ใน .asm** |
| `tools/emu_check_1f1b.py`, `tools/run91.py` | ทดสอบด้วย unicorn (`pip install unicorn`) : INT 10h AH=91h |
| `tools/TT.BAT` | รัน TKEY แล้ว TCUR ต่อกันโดยไม่ผ่านพรอมต์ของ shell — ใช้แยกว่ารูปร่าง cursor เปลี่ยนตอนโปรแกรมจบหรือตอนรับบรรทัดคำสั่ง |
| `tools/tkey.s`, `tools/TKEY.COM` | รอคีย์ 1 ตัวด้วย DOS (AH=08h) แล้วพิมพ์ค่า CRTC/BIOS ของ cursor — แยกว่า cursor หายเพราะการพิมพ์ที่ prompt ของ shell หรือไม่ |
| `tools/tcur.s`, `tools/TCUR.COM` | พิมพ์ค่า CRTC 09/0A/0B/0E/0F และตำแหน่ง/รูปร่าง cursor ใน BIOS data — ใช้ตอนวินิจฉัยอาการ cursor หาย |
| `tools/t16.s`, `tools/T16.COM` | ทดสอบมาโคร ั้ ของ INT 16h : เฟส 1 อ่านด้วย AH=00h, เฟส 2 อ่านด้วย AH=10h แล้วพิมพ์ AX (ฐาน 16) |
| `tools/t91.s`, `tools/T91.COM` | โปรแกรมทดสอบ AH=91h สำหรับรันใน DOSBox-X หลังติดตั้ง THAID (ดู §13.2–13.3) |
| `tools/thaid_cfg.py`, `tools/emu_check_cfg.py` | ถอด/สร้างไฟล์ THAID.CFG และทดสอบตัวโหลดจริงด้วย unicorn (โครงสร้างดู THAID_ANALYSIS.md §16) |
| `tools/decode_strings.py` | ดึง/ถอดสตริง TIS-620 |
| `tools/codeset.py` | ถอดตารางรหัส KU/TIS (internal ↔ app) จาก binary |
| `tools/olsf_dump.py` | ถอดโครงสร้างเมนู OLSF (ข้อความ/รายการ/ตัวแปร/ข้อความช่วย) |
| `tools/thaid_ku.py` | ถอดสตริง internal code (`--olsf` = โซนเมนูทั้งหมด) |
| `tools/font_map_16.py` | วาดฟอนต์ไทย 8×16 ที่ 0x64E0 → `font_map_64E0.png` |
| `tools/font_vga_loaded.py` | จำลองการโหลดฟอนต์ไทยโหมด 3 ตามชุดรหัส KU/TIS → `font_vga_KU.png`, `font_vga_TIS.png` |
| `tools/thaid_render.py` | จำลอง renderer 3 band + ฟอนต์จริง → PNG |
| `tools/ku_bands.py` | วาดแผนภาพ 3 band ต่อ cell พร้อมรหัส U/M/L → `ku_bands.png` (`python tools/ku_bands.py "ข้อความ" out.png`) |
| `tools/font_maps.py` | วาดฟอนต์ 8×6 ทั้ง 4 ชุด (0x4CE0/52E0/58E0/5EE0) → `font_map_*.png` |
| `tools/render_font.py` | เรนเดอร์ glyph 8×16 เป็น ASCII art — **ยังอิงโมเดลฟอนต์แบบเก่า (FONT A/B ใน §14 ที่ถูกแทนที่แล้ว)** ใช้กับฟอนต์ที่ 0x64E0 ได้ผ่าน `tools/font_map_16.py` แทน |
| OLSF_menu_structure.txt | โครงสร้างเมนู OLSF ที่ถอดแล้ว (ตัวแปร [38xx] ↔ ข้อความ ↔ ข้อความช่วย) |
| OLSF_strings_decoded.txt | ข้อความเมนู OLSF ที่ถอดจากไฟล์ด้วยตารางครบ |

## การใช้งาน

วาง `THAID.COM` ไว้ที่ root ของ repo (ถูก .gitignore ไว้เพื่อลิขสิทธิ์) แล้ว:

```bash
python tools/gen_listing.py     # สร้าง THAID_disasm.asm ใหม่
python tools/decode_strings.py THAID.COM > THAID_strings.txt
```

ต้องการ Python 3 กับ `capstone` (`pip install capstone`)

สร้างซอร์สที่ assemble ได้และ build กลับเป็น COM: `python tools/gen_source.py` (ต้องมี binutils `as`/`ld`/`nm`) -> `THAID_src.s`, `build/THAID_rebuilt.COM`

ทดสอบ AH=91h: รัน `THAID` ใน DOSBox-X แล้วรัน `T91` (ดู THAID_ANALYSIS.md §13.2–13.3)

## จุดเริ่มสืบค้นที่แนะนำ

- `0x6FB9` entry point (ไฟล์เริ่มด้วย `JMP 6FB9`)
- `0x4B80` รูทีนการ์ด VGA / `0x0A3E` ตัวรับคำสั่งฝัง `9B`+ตัวอักษร / `0x2E46` ตัวขับเครื่องพิมพ์ / `0x3450` OLSF
- `0x1AE3` INT 10h hook / `0x251F` INT 9 / `0x2699` INT 16h / `0x2D7D` INT 17h / `0x251` INT 21h / `0x1227` INT 8
- `0x115E` แผนที่บรรทัดตรรกะ → 3 ระดับ, `0x165E` row renderer (state machine, SMC jmp `0x16F8`), `0x155D` ตาราง slice ล่าง, `0x1C1C` ตารางแถว 25 ช่อง
- `0x7083` TurboPower TSR parameter block (`M2.6`) — ถอนการติดตั้งด้วย RELEASE.EXE (TurboPower RELEASE 2.6)
- `0x7614–0x7617` ท้ายภาพโปรแกรม (ไบต์ ASCII `88` = ส่วนท้ายเลขรุ่น) — ไฟล์จบที่ 0x7617
