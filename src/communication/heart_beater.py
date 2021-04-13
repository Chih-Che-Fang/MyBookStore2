import requests
import threading
import time

#HeartBeater is used to send hearbeat message to fronten server and perform fault detection
class HeartBeater(threading.Thread):
	#Constructor of HeartBeater
	def __init__(self, server_type, server_id, config):
		threading.Thread.__init__(self)
		self.server_type = server_type
		self.server_id = server_id
		self.config = config
		self.frontend_addr = config.getAddress('frontend')

	#Return the request server's address using round-robin algorithm
	def run(self):
		
		while True:
			res = requests.get("http://{}/heart_beat?server_type={}&server_id={}".format(self.frontend_addr, self.server_type, self.server_id))
			time.sleep(2)
		