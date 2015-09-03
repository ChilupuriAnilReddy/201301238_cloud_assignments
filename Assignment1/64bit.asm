section .data
   msg db "", 0xA,0xD 
   len equ $ - msg
  num1: equ 3 
  num2: equ 4 
  SYS_READ equ 3 
  SYS_WRITE equ 4 
  STDIN equ 0 
  STD_OUT equ 1 
  SYS_EXIT equ 1 
  EXIT_CODE equ 0 
  NEW_LINE db 0xa 

section .text
   global _start    
  
_start:
  mov  rax, num1 
  mov  rbx, num2 
  add  rax,  rbx 
  add  rax, '0' 

  mov [res],  rax 
  mov  rcx, res 
  mov  rdx, 1 
  mov  rbx, STD_OUT 
  mov  rax, SYS_WRITE 
   int 0x80  
  mov  rcx, NEW_LINE 
  mov  rdx, 1 
  mov  rbx, STD_OUT 
  mov  rax, SYS_WRITE 
           
   int 0x80 
  mov  rax, SYS_EXIT 
   int 0x80 
  

      
   segment .bss
  res resb 1 
