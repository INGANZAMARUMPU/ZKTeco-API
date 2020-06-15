import cherrypy
from requests_methods import *

class Server:

	def __init__(self, *args, **kwargs):
		self.obj = ZKTeco()

	@cherrypy.expose
	@cherrypy.tools.json_out()
	def logs(self, id_user, sdate=None, edate=None):
		# cherrypy.response.headers['Content-Type'] = 'application/json'
		if sdate and edate:
			return self.obj.logs(id_user, sdate, edate)
		return self.obj.logs(id_user)

	@cherrypy.expose
	@cherrypy.tools.json_out()
	def users(self, first=None, last=None):
		# cherrypy.response.headers['Content-Type'] = 'application/json'
		return self.obj.users(first, last)

	@cherrypy.expose
	@cherrypy.tools.json_out()
	def user(self):
		# cherrypy.response.headers['Content-Type'] = 'application/json'
		return ""