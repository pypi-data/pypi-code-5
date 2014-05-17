import csv
from django.http import HttpResponse

def render_csv(data, filename="data.csv"):
	res = HttpResponse(content_type='text/csv')
	res['Content-Disposition'] = 'attachment; filename="%s"' % filename

	writer = csv.writer(response)
	for item in data:
		writer.writerow(item)

	return response

def as_csv(fn=None, filename=None):
	def decorator(fn):
    	def _fn(request, *args, **kwargs):
        	data = fn(request, *args, **kwargs)
        	return render_csv(data, filename=filename)

		return _fn

	return decorator(fn) if fn else decorator

