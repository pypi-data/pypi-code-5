import sys


def render_json(data, indent=0, mimetype='applicaction/json'):
	import json
	from django.http import HttpResponse

	return HttpResponse(json.dumps(data, indent=4), mimetype=mimetype)


sys.modules[__name__]  = render_json
