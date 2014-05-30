import sys

def mask_string(string, start, stop, mask='****'):
	length = len(string)
	start = start if start > 0 else start % length
	stop = stop if stop > 0 else stop % length
	return string[:start] + mask + string[stop+1:]

sys.modules[__name__] = mask_string
