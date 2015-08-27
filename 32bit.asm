section .data
   num1: equ 3
   num2: equ 4
   SYS_READ equ 3
   SYS_WRITE equ 4
   STDIN equ 0
   STD_OUT equ 1
   SYS_EXIT equ 1
   EXIT_CODE   equ 0
   NEW_LINE db 0xa

section	.text
   global _start    
	
_start:
   mov eax, num1
   mov ebx, num2   
   add eax, ebx
   add eax, '0'   	  
   mov [res], eax
   mov eax, SYS_WRITE        
   mov ebx, STD_OUT
   mov ecx, res         
   mov edx, 1        
   int 0x80  
   mov eax, SYS_WRITE        
   mov ebx, STD_OUT
   mov ecx, NEW_LINE         
   mov edx, 1        
   int 0x80 
   mov   eax, SYS_EXIT
   mov   edi, EXIT_CODE	
   int 0x80	
	

      
   segment .bss
   res resb 1