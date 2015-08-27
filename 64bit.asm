section .data
   num1: equ 3
   num2: equ 4
   SYS_READ  equ 3
   SYS_WRITE equ 1
   STDIN     equ 0
   STD_OUT     equ 1
   SYS_EXIT equ 60
   EXIT_CODE   equ 0
   NEW_LINE db 0xa



section .text
    global _start


_start:
    mov     rax, num1
    mov     rbx, num2
    add     rax, rbx
    add     rax, '0'
    
    mov  [res], rax


   mov   rax, SYS_WRITE
   mov   rdi, STD_OUT
   mov   rsi, res
   mov   rdx, 1
   syscall

   mov   rax, SYS_WRITE
   mov   rdi, STD_OUT
   mov   rsi, NEW_LINE
   mov   rdx, 1
   syscall

   mov   rax, SYS_EXIT
   mov   rdi, EXIT_CODE
   syscall



segment .bss
   res resb 1