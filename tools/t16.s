# T16: ทดสอบมาโคร ั้ ของ INT 16h : เฟส 1 อ่านด้วย AH=00h, เฟส 2 อ่านด้วย AH=10h (ESC = จบเฟส)
.code16
.intel_syntax noprefix
.text
.globl _start
_start:
    mov dx,offset m1
    mov ah,9
    int 0x21
    mov byte ptr [fn],0x00
    call phase
    mov dx,offset m2
    mov ah,9
    int 0x21
    mov byte ptr [fn],0x10
    call phase
    mov ax,0x4c00
    int 0x21
phase:
rd:
    mov ah,[fn]
    int 0x16
    push ax
    call hexw
    mov dl,0x20
    mov ah,2
    int 0x21
    pop ax
    cmp al,0x1b
    jne rd
    ret
hexw:                       # พิมพ์ AX เป็นฐาน 16
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
fn: .byte 0
m1: .ascii "Phase 1: INT 16h AH=00h, press Shift+7 (ESC to end)\r\n$"
m2: .ascii "\r\nPhase 2: INT 16h AH=10h, press Shift+7 (ESC to end)\r\n$"
