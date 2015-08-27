import sys
import os

fileopen = open('32bit.asm','r')
fileopen1 = open('generated62bit.asm','w')

for line in fileopen:
	line11 = line.split()
	a="\t"
	if len(line11) == 3:

		for line1 in line11:

			if line1 == "eax,":
				a = a + " rax ,"
			elif line1 == "ebx,":
				a = a + " rbx ,"
			elif line1 == "ecx,":
				a = a + " rcx ,"
			elif line1 == "edx,":
				a = a + " rdx ,"
			elif line1 == "ebx":
				a = a + " rbx"

			elif line1 == "eax":
				a = a + " rax "
			elif line1 == "edi,":
				a = a + " rdi ,"


			else:
				a = a + line1  + " "
		line = a + "\n"
	elif len(line11) == 2:
		if(line11[0]=='int'):
			line = "\t"+'syscall' + "\n"
	fileopen1.write(str(line))
