import os
from main import Server

conf = os.path.join(os.path.dirname(__file__), "settings.conf")

if __name__ == '__main__':
	import cherrypy
	cherrypy.quickstart(Server(), config=conf)