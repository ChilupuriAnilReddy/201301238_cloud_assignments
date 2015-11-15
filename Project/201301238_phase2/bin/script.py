import os
import sys
if __name__ == '__main__':
	if len(sys.argv) < 4:
			print "Entered Wrong Format"
			exit(1)
	#os.system("sudo apt-get install python-virtualenv")
	#os.system("sudo pip install Flask")
	os.system("cp " + sys.argv[1] +" " + "../src")
	os.system("cp " + sys.argv[2] +" " + "../src")
	os.system("cp " + sys.argv[3] +" " + "../src")
	os.chdir("../src")
 	os.system("python hello.py " + sys.argv[1] + " " +sys.argv[2] + " " +sys.argv[3])
