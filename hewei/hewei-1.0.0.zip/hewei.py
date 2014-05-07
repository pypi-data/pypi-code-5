"""aaaaaaaaaaaaaaaaaaa
aaaaaaaaaaaaaaaaaaa"""
def xunhuan(my_list):
#单行注释
	for new_list in my_list:
		if isinstance(new_list,list):
			#adasdsds
			xunhuan(new_list)
		else:
			print(new_list)