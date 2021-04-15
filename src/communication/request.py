import requests
import threading

#Threadred request class
class Request(threading.Thread):
	#Request constructor
	def __init__(self, req):
		threading.Thread.__init__(self)
		self.req = req
	#Make HTTP request in new thread
	def run(self):
		try:
			requests.get(self.req)
		except:
			print('Request {} Failed because remote server crahsed'.format(self.req))