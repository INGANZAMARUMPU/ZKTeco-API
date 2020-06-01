import cherrypy
from requests_methods import *

class Server:

	def __init__(self, *args, **kwargs):
		self.obj = ZKTeco()

	@cherrypy.expose
	def logs(self, id_user):
		# cherrypy.response.headers['Content-Type'] = 'application/json'
		return self.obj.logs(id_user)

	@cherrypy.expose
	def users(self, first=None, last=None):
		# cherrypy.response.headers['Content-Type'] = 'application/json'
		return self.obj.users(first, last)

	@cherrypy.expose
	def user(self):
		# cherrypy.response.headers['Content-Type'] = 'application/json'
		return ""