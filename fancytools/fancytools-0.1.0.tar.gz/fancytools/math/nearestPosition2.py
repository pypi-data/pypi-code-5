# -*- coding: utf-8 -*-


def nearestPosition2(array, value, lastPos):
	'''
	return the index of that value that is most similar in the array
	starting from the last known position, checking the right direction
	'''
	#get initialdirection
	d1 = abs(value - array[lastPos])
	if lastPos == 0:
		p = 1 #increase
	elif lastPos == array.size-1:#len(array)-1: #TODO besser:resolution nehmen
		p = -1 #decrease
	else: #check direction
		d0 = abs(value - array[lastPos-1])
		d2 = abs(value - array[lastPos+1])
		if d0 >= d1 <= d2:
			return lastPos # new pos is last position
		elif d0 < d1:
				p = -1 #decrease
				lastPos -= 1
				d1 = d0
		else:
			p = 1 #increase
			lastPos += 1
			d1 = d2
	while True:
		lastPos += p
		if lastPos < 0:
			return 0
		try:
			d2 = abs(value - array[lastPos])
			if d2 > d1:
				return lastPos - p
		except IndexError:# hit the border
			return lastPos - p
		d1 = d2