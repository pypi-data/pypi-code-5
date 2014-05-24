"""This is a standard tuple in python:"""
array = (("apple", "banana"), ("grape", "orange"), ("watermelon",), ("grapefruit",));

"""the loop of travel the whole tuple"""
for i in range(len(array)):
	print "array[% i]: "% i, "",
	for j in range(len(array[i])):
		print array[i][j], "",
	print
