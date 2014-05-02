added_list=[1,2,3,4,5,[61,62,63,64,65],7,[81,82,83,[841,842,843,844],85]]

def showlist(l,indent=False,tap_num=0):
	for i in l:
		if isinstance(i,list):
			showlist(i,indent,tap_num+1)
		else:
			if indent:
				for num in range(tap_num):
					print("\t",end='')
			print(i)
