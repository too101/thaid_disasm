# ตรวจ INT 10h AH=91h (1F02h) ด้วย unicorn: AL=FFh เทียบ AL!=FFh (AL!=FFh เรียก INT 60h = แอป->internal ; ในการจำลองนี้ตั้งให้ INT 60h เป็น identity เพราะตาราง [7A2h] ถูกเติมตอนติดตั้ง) ; รัน: pip install unicorn ; python tools/emu_check_1f1b.py (ที่โฟลเดอร์รากของ repo)
from unicorn import *
from unicorn.x86_const import *
d=open('THAID.COM','rb').read()
def run(al,ch,ah=0x07,di=0x200):
    mu=Uc(UC_ARCH_X86,UC_MODE_16)
    mu.mem_map(0,0x100000)
    cs=0x1000; base=cs*16
    mu.mem_write(base+0x100,d)
    es=0x3000
    mu.mem_write(base+0x13e,es.to_bytes(2,'little'))
    mu.mem_write(base+0x1e74,b'\0')
    mu.mem_write(base+0x500,b'\xf4')           # hlt stub? use ip 0x500 as return
    mu.mem_write(base+0x2000-0x10, bytes([ch])) # string at DS:SI
    # stack
    ss=0x2000; sp=0xFFF0
    mu.reg_write(UC_X86_REG_SS,ss);mu.reg_write(UC_X86_REG_SP,sp-2)
    mu.mem_write(ss*16+sp-2,(0x4FF).to_bytes(2,'little'))
    mu.mem_write(base+0x4FF,b'\xf4')
    for r,v in((UC_X86_REG_CS,cs),(UC_X86_REG_DS,cs),(UC_X86_REG_ES,es)):mu.reg_write(r,v)
    mu.reg_write(UC_X86_REG_SI,0x2000-0x10);mu.reg_write(UC_X86_REG_CX,1)
    mu.reg_write(UC_X86_REG_DI,di)
    mu.reg_write(UC_X86_REG_AX,(ah<<8)|al)
    calls=[]
    def intr(u,n,_):
        calls.append(n)
        if n==0x60:
            pass            # แอป->internal เป็น identity ในการจำลองนี้ (AL คงเดิม)
        if n==0x5f:
            a=u.reg_read(UC_X86_REG_AX)&0xff
            v=d[0x155D-0x100+a]
            u.reg_write(UC_X86_REG_AX,(u.reg_read(UC_X86_REG_AX)&0xff00)|v)
    mu.hook_add(UC_HOOK_INTR,intr)
    try: mu.emu_start(0x1F02,base+0x4FF-base+0 if False else 0x4FF,timeout=1000000,count=2000)
    except UcError as e: print('err',e, hex(mu.reg_read(UC_X86_REG_IP)))
    out=bytes(mu.mem_read(es*16+di-0xa2,0x200+0x20))
    return calls,out
for al,ch in((0xff,0x67),(0x00,0x67),(0xff,0x80),(0x00,0x80)):
    c,o=run(al,ch)
    # print written cells: upper(di-0xa2.. ), middle di.., lower di+0x9e
    base=0xa2
    print(f"AL={al:02X} ch={ch:02X} ints={c}  mid={o[base:base+4].hex()} low={o[base+0x9e:base+0xa2].hex()} up={o[0:6].hex()}")
