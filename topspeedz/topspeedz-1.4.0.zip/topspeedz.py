import sys

"""printing element of list"""
def print_lol(aList,indent=False,num=0,fh=sys.stdout):
	"""function explanation"""

	for each_item in aList:
		if isinstance(each_item,list):
			print_lol(each_item,indent,num+1,fh)
		else:
			for i in range(num):
				if indent:
					print("\t",end="",file=fh)
			print(each_item,file=fh)