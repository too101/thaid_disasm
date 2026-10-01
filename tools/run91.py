from unicorn import *
from unicorn.x86_const import *
th=open('/mnt/user-data/uploads/thaid_disasm/THAID.COM','rb').read()
t=open('T91.COM','rb').read()
mu=Uc(UC_ARCH_X86,UC_MODE_16);mu.mem_map(0,0x100000)
TS=0x2000
mu.mem_write(TS*16+0x100,th)
mu.mem_write(TS*16+0x13e,(0x3000).to_bytes(2,'little'))
mu.mem_write(0x1000*16+0x100,t)
mu.mem_write(0x1000*16+0xfff0,b'\xf4')
out=[]
def intr(u,n,_):
    ax=u.reg_read(UC_X86_REG_AX);ah=ax>>8
    cs=u.reg_read(UC_X86_REG_CS);ip=u.reg_read(UC_X86_REG_IP)
    if n==0x16 and ah==0x0f:
        u.reg_write(UC_X86_REG_BX,TS)
    elif n==0x21:
        if ah==9:
            ds=u.reg_read(UC_X86_REG_DS);dx=u.reg_read(UC_X86_REG_DX)
            s=b'';a=ds*16+dx
            while True:
                c=u.mem_read(a,1)[0]
                if c==36:break
                s+=bytes([c]);a+=1
            out.append(s.decode('latin1'))
        elif ah==2: out.append(chr(u.reg_read(UC_X86_REG_DX)&0xff))
    elif n==0x10:
        sp=u.reg_read(UC_X86_REG_SP);ss=u.reg_read(UC_X86_REG_SS)
        for v in (0x202,cs,ip):
            sp-=2;u.mem_write(ss*16+sp,v.to_bytes(2,'little'))
        u.reg_write(UC_X86_REG_SP,sp)
        u.reg_write(UC_X86_REG_CS,TS);u.reg_write(UC_X86_REG_IP,0x1e40)
    elif n==0x5f:
        a=ax&0xff;u.reg_write(UC_X86_REG_AX,(ax&0xff00)|th[0x1554-0x100+a])
mu.hook_add(UC_HOOK_INTR,intr)
for r,v in((UC_X86_REG_CS,0x1000),(UC_X86_REG_DS,0x1000),(UC_X86_REG_ES,0x1000),(UC_X86_REG_SS,0x1000),(UC_X86_REG_SP,0xfff0)):mu.reg_write(r,v)
mu.mem_write(0x1000*16+0xfff0,b'\xf4\xf4')
mu.mem_write(0x1000*16+0xffee,(0xfff0).to_bytes(2,'little'));mu.reg_write(UC_X86_REG_SP,0xffee)
try: mu.emu_start(0x1000*16+0x100,0x1000*16+0xfff0,count=200000)
except UcError as e: print('err',e)
print(''.join(out))
