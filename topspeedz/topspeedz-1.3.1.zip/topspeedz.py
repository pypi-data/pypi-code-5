
"""printing element of list"""
def print_lol(aList,indent=False,num=0):
	"""function explanation"""

	for each_item in aList:
		if isinstance(each_item,list):
			print_lol(each_item,indent,num+1)
		else:
			for i in range(num):
				if indent:
					print("\t",end="")
			print(each_item)