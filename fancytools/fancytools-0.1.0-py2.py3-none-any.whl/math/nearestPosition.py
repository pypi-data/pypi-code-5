# -*- coding: utf-8 -*-


def nearestPosition(array, value):
	'''
	return the index of that value that is most similar in the array
	'''
	difference_list = array - value
	difference_list = abs(difference_list)
	return difference_list.argmin()