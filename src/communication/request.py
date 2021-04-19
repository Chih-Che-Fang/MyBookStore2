import requests
import threading
from threading import Thread

#Threadred request class
class Request(threading.Thread):
	#Request constructor
	def __init__(self, req):
		threading.Thread.__init__(self)
		self.req = req
		self.res = None
	#Make HTTP request in new thread
	def run(self):
		try:
			self.res = requests.get(self.req).json()
		except:
			print('Request {} Failed because remote server crahsed'.format(self.req))
	def join(self, *args):
		Thread.join(self, *args)
		return self.res