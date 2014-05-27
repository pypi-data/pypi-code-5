"""This is a module which provides a function called print_list().This
function is can print the list."""
def print_list (alist , indent = False,level=0):
	"""这个函数有三个参数，alist是一个任意的python列表，
	indent用于确认是否打开缩进功能，level表示缩进多少个制表符"""
	for each_item in alist :
		if isinstance( each_item,list):
			print_list(each_item,level+1)
		else :
			for tab_stop in range(level):
				print "\t",
			print (each_item)
