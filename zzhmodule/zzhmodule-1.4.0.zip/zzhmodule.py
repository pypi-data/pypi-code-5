"""This is a module which provides a function called print_list().This
function is can print the list."""
import sys
def print_list (alist , indent = False,level=0,fh=sys.stdout):
	"""这个函数有三个参数，alist是一个任意的python列表，
	indent用于确认是否打开缩进功能，level表示缩进多少个制表符"""
	for each_item in alist :
		if isinstance( each_item,list):
			print_list(each_item,indent,level+1,fh)
		else :
			if indent :
				for tab_stop in range(level):
					print >> fh,"\t",
			print >> fh,each_item
