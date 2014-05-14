import six
if six.PY3:
	from wmon.wmonpy3 import *
else:
	from wmonpy2 import *

def mainwmon():				
		main()

if __name__ == "__main__":
 	mainwmon()
			
