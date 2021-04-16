import os
from datetime import timedelta

class Config(object):
	#USE_SESSION_FOR_NEXT = True
	#REMEMBER_COOKIE_DURATION = timedelta(20)
	catalog_server = {
		'ip': "http://127.0.0.1",
		'port': "8010"
	}
