# TCUR: พิมพ์ค่าที่เกี่ยวกับ cursor ตอนนั้น : CRTC reg 09,0A,0B,0E,0F (ฐาน 16) + BIOS 40:50 (ตำแหน่ง) 40:60 (รูปร่าง)
.code16
.intel_syntax noprefix
.text
.globl _start
_start:
    call dump
    mov dx,offset lw
    mov ah,9
    int 0x21
    xor ax,ax
    mov es,ax
    mov cx,es:[0x46c]
    add cx,36               # รอ ~2 วินาที (36 tick) ให้ตัวจับเวลา INT 8 ของ THAID ซิงก์ cursor
w1:
    mov ax,es:[0x46c]
    sub ax,cx
    js w1
    call dump
    mov ax,0x4c00
    int 0x21
dump:
    mov bx,offset regs
nxt:
    mov al,[bx]
    cmp al,0xff
    je bios
    push ax
    mov dx,offset lbl
    mov ah,9
    int 0x21
    pop ax
    push ax
    call hexb
    mov dl,'='
    mov ah,2
    int 0x21
    pop ax
    mov dx,0x3d4
    out dx,al
    inc dx
    in al,dx
    call hexb
    mov dl,0x20
    mov ah,2
    int 0x21
    inc bx
    jmp nxt
bios:
    mov dx,offset lb
    mov ah,9
    int 0x21
    xor ax,ax
    mov es,ax
    mov ax,es:[0x450]
    call hexw
    mov dl,0x20
    mov ah,2
    int 0x21
    mov ax,es:[0x460]
    call hexw
    mov dx,offset crlf
    mov ah,9
    int 0x21
    ret
hexw:
    push ax
    mov al,ah
    call hexb
    pop ax
hexb:
    push ax
    shr al,4
    call nib
    pop ax
    and al,0x0f
nib:
    add al,0x30
    cmp al,0x39
    jbe pr
    add al,7
pr:
    mov dl,al
    mov ah,2
    int 0x21
    ret
regs: .byte 9,0x0a,0x0b,0x0e,0x0f,0xff
lbl: .ascii "R$"
lb: .ascii "\r\nBIOS pos,shape: $"
crlf: .ascii "\r\n$"
lw: .ascii "\r\n(wait 2s)\r\n$"
