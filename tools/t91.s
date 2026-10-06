.code16
.intel_syntax noprefix
.text
.globl _start
_start:
    mov ah,0x0f
    int 0x16
    mov es,bx
    cmp word ptr es:[0x1fd0],0x694d      # "Mi" ของ "MicroWizKBD" ที่ 1FD0h
    jne notinst
    mov [tseg],bx
    mov ax,es:[0x13e]
    mov [vseg],ax
    mov bp,offset tests
nexttest:
    mov al,[bp]
    mov ah,[bp+1]
    mov [mode],al
    mov [chbuf],ah
    # ล้างพื้นที่ทดสอบ
    mov es,[vseg]
    mov di,0x150
    mov cx,0x90
    xor ax,ax
    cld
    rep stosw
    # เรียก INT 10h AH=91h
    mov si,offset chbuf
    mov di,0x200
    mov cx,1
    mov bl,7
    mov al,[mode]
    mov ah,0x91
    int 0x10
    mov ax,cs
    mov ds,ax
    mov es,[vseg]
    mov dx,offset s_al
    call puts
    mov al,[mode]
    call hex
    mov dx,offset s_ch
    call puts
    mov al,[chbuf]
    call hex
    mov dx,offset s_mid
    call puts
    mov al,es:[0x200]
    call hex
    mov dx,offset s_low
    call puts
    mov al,es:[0x2a0]
    call hex
    mov dx,offset crlf
    call puts
    add bp,2
    cmp bp,offset tests_end
    jb nexttest
    ret
notinst:
    mov dx,offset s_no
    call puts
    ret
puts:
    mov ah,9
    int 0x21
    ret
hex:
    push ax
    shr al,4
    call nib
    pop ax
    and al,0x0f
nib:
    add al,'0'
    cmp al,'9'
    jbe 1f
    add al,7
1:  mov dl,al
    mov ah,2
    int 0x21
    ret
tseg: .word 0
vseg: .word 0
mode: .byte 0
chbuf: .byte 0
tests: .byte 0xff,0x67, 0x00,0x67, 0xff,0x80, 0x00,0x80
tests_end:
s_al: .ascii "AL=$"
s_ch: .ascii " ch=$"
s_mid: .ascii "  mid=$"
s_low: .ascii " low=$"
crlf: .ascii "\r\n$"
s_no: .ascii "THAID not resident (run THAID first)\r\n$"
