"""aaaaaaaaaaaaaaaaaaa
aaaaaaaaaaaaaaaaaaa"""
def xunhuan(my_list):
#单行注释
def xunhuan2(this_list,num):
	for f in this_list:
		if isinstance(f,list):
			xunhuan2(f,num+1)
		else:
			for table_num in range(num):
				print("\t",end='')
				print(f)