import sys
if sys.version[0] == '3':
	from wmon.wmonpy3 import *
elif sys.version[0:3] == '2.7':
	from wmonpy2 import *
elif sys.version[0] == '2':
	print ("ERROR: Wmon is only compatible with Python 2.7 , Python 3 or higher.")

def mainwmon():				
		main()

if __name__ == "__main__":
 	mainwmon()
			
