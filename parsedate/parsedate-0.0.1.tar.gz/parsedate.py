import sys

def parse(result):
	from datetime import datetime
	import days

	if result == 'today' :
		return days.today()
	elif result == 'yesterday':
		return days.yesterday()
	else:
		return datetime.strptime(result, "%Y-%m-%d")
	
	return result

sys.modules[__name__] = parse
