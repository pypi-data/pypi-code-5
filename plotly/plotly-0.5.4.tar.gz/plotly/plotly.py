import requests
import json


def signup(un, email):
	''' Remote signup to plot.ly and plot.ly API
	Returns:
		:param r with r['tmp_pw']: Temporary password to access your plot.ly acount
		:param r['api_key']: A key to use the API with
		
	Full docs and examples at https://plot.ly/API
	:un: <string> username
	:email: <string> email address
	'''
	payload = {'version': '0.5.4', 'un': un, 'email': email, 'platform':'Python'}
	r = requests.post('https://plot.ly/apimkacct', data=payload)
	r = json.loads(r.text)
	if 'error' in r.keys():
		if not r['error'] == '':
			print(r['error'])
	if 'warning' in r.keys():
		print(r['warning'])
	if 'message' in r.keys():
		print(r['message'])

	return r

class plotly:
	def __init__(self, username=None, key=None,verbose=True):
		''' plotly constructor. Supply username and api key.
		'''
		self.un = username
		self.key = key
		self.__filename = None
		self.__fileopt = None
		self.verbose = verbose
		self.open = False

	def iplot(self, *args, **kwargs):
		''' for use in ipython notebooks '''
		res = self.__callplot(*args, **kwargs)
		width = kwargs.get('width', 600)
		height = kwargs.get('height', 600)
		s = '<iframe height="'+str(height+50)+'" id="igraph" scrolling="no" seamless="seamless" src="'+res['url']+'/'+str(width)+'/'+str(height)+'" width="'+str(width+50)+'"></iframe>'
		try:
			from IPython.display import HTML
			return HTML(s)
		except:
			return s

	def plot(self, *args, **kwargs):
		res = self.__callplot(*args, **kwargs)
		if res['error'] == '' and self.open:
			from webbrowser import open as wbopen
			wbopen(res['url'])
		return res

	def __callplot(self, *args, **kwargs):
		''' Make a plot in plotly.
		Two interfaces:
			1 - ploty.plot(x1, y1[,x2,y2,...],**kwargs)
			where x1, y1, .... are lists, numpy arrays
			2 - plot.plot([data1, ...], **kwargs)
			where data1 is a dict that is at least
			{'x': x1, 'y': y1} but can contain more styling and sharing options.
			kwargs accepts:
				filename
				fileopt
				style
				layout
			See https://plot.ly/API for details.
		Returns:
			:param r with r['url']: A URL that displays the generated plot
			:param r['filename']: The filename of the plot in your plotly account.
		'''

		un = kwargs['un'] if 'un' in kwargs.keys() else self.un
		key = kwargs['key'] if 'key' in kwargs.keys() else self.key
		if not un or not key:
			raise Exception('Not Signed in')

		if not 'filename' in kwargs.keys():
			kwargs['filename'] = self.__filename
		if not 'fileopt' in kwargs.keys():
			kwargs['fileopt'] = self.__fileopt
	
		origin = 'plot'
		r = self.__makecall(args, un, key, origin, kwargs)
		return r

	def layout(self, *args, **kwargs):
		''' Style the layout of a Plotly plot.
			ploty.layout(layout,**kwargs)
			:param layout - a dict that customizes the style of the layout,
							the axes, and the legend.
			:param kwargs - accepts:
				filename
			See https://plot.ly/API for details.
		Returns:
			:param r with r['url']: A URL that displays the generated plot
			:param r['filename']: The filename of the plot in your plotly account.
		'''

		un = kwargs['un'] if 'un' in kwargs.keys() else self.un
		key = kwargs['un'] if 'key' in kwargs.keys() else self.key
		if not un or not key:
			raise Exception('Not Signed in')
		if not 'filename' in kwargs.keys():
			kwargs['filename'] = self.__filename
		if not 'fileopt' in kwargs.keys():
			kwargs['fileopt'] = self.__fileopt
	
		origin = 'layout'
		r = self.__makecall(args, un, key, origin, kwargs)
		return r

	def style(self, *args, **kwargs):
		''' Style the data traces of a Plotly plot.
			ploty.style([data1,[,data2,...],**kwargs)
			:param data1 - a dict that customizes the style of the i'th trace
			:param kwargs - accepts:
				filename
			See https://plot.ly/API for details.
		Returns:
			:param r with r['url']: A URL that displays the generated plot
			:param r['filename']: The filename of the plot in your plotly account.
		'''

		un = kwargs['un'] if 'un' in kwargs.keys() else self.un
		key = kwargs['un'] if 'key' in kwargs.keys() else self.key
		if not un or not key:
			raise Exception('Not Signed in')
		if not 'filename' in kwargs.keys():
			kwargs['filename'] = self.__filename
		if not 'fileopt' in kwargs.keys():
			kwargs['fileopt'] = self.__fileopt
	
		origin = 'style'
		r = self.__makecall(args, un, key, origin, kwargs)
		return r

	class __plotlyJSONEncoder(json.JSONEncoder):
		def numpyJSONEncoder(self, obj):
			try:
				import numpy
				if type(obj).__module__.split('.')[0] == numpy.__name__:
					l = obj.tolist()
					d = self.datetimeJSONEncoder(l) 
					return d if d else l
			except:
				pass
			return None
		def datetimeJSONEncoder(self, obj):
			# if datetime or iterable of datetimes, convert to a string that plotly understands
			import datetime
			try:
				if isinstance(obj,(datetime.datetime, datetime.date)):
					return obj.strftime('%Y-%m-%d %H:%M:%S')
				elif isinstance(obj[0],(datetime.datetime, datetime.date)):
					return [o.strftime('%Y-%m-%d %H:%M:%S') for o in obj]
			except:
				pass
			return None
		def pandasJSONEncoder(self, obj):
			try:
				import pandas
				if isinstance(obj, pandas.DataFrame):
					return obj.to_json()
			except:
				pass
			return None
		def default(self, obj):
			try:
				return json.dumps(obj)
			except TypeError as e:
				encoders = (self.datetimeJSONEncoder, self.numpyJSONEncoder, self.pandasJSONEncoder)
				for encoder in encoders:
					s = encoder(obj)
					if s:
						return s
				raise e
			return json.JSONEncoder.default(self,obj)

	def __makecall(self, args, un, key, origin, kwargs):
		version = '0.5.4'
		platform = 'Python'

		args = json.dumps(args, cls=self.__plotlyJSONEncoder)
		kwargs = json.dumps(kwargs, cls=self.__plotlyJSONEncoder)
		url = 'https://plot.ly/clientresp'
		payload = {'platform': platform, 'version': version, 'args': args, 'un': un, 'key': key, 'origin': origin, 'kwargs': kwargs}
		r = requests.post(url, data=payload)
		r = json.loads(r.text)
		if 'error' in r.keys():
			print(r['error'])
		if 'warning' in r.keys():
			print(r['warning'])
		if 'message' in r.keys():
			if self.verbose:
				print(r['message'])
			
		if 'filename' in r.keys():
			self.__filename = r['filename']
		return r



