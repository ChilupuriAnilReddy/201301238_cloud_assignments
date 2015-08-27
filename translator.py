import sys
import os

fileopen = open('32bit.asm','r')
fileopen1 = open('generated64bit.asm','w')

for line in fileopen:
	line11 = line.split()
	a="\t"
	if len(line11) == 3:
		for line1 in line11:
			z = len(line1)
			if line1 == "eax":
				a = a + " rax "
			elif line1 == "eax,":
				a = a + " rax, "

			elif line1 == "ebx":
				a = a + " rbx "
			elif line1 == "ebx,":
				a = a + " rbx, "

			elif line1 == "ecx":
				a = a + " rcx "
			elif line1 == "ecx,":
				a = a + " rcx, "

			elif line1 == "edx":
				a = a + " rdx "
			elif line1 == "edx,":
				a = a + " rdx, "

			elif line1 == "edi":
				a = a + " rdi "
			elif line1 == "edi,":
				a = a + " rdi, "

			elif line1 == "esi":
				a = a + " rsi "
			elif line1 == "esi,":
				a = a + " rsi, "

			else:
				a = a + line1 + " "

		line = a + "\n" 

			
		
	fileopen1.write(str(line))
