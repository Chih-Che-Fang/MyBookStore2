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
		#self.config = config
		self.frontend_addr = config.getAddress('frontend')
		self.catalog_server_addr = config.server_addr['catalog']
		self.stop_listener = False

	#Stop the listener
	#input: None
	#output: None
	def stop(self):
		self.stop_listener = True
	
	#Return the request server's address using round-robin algorithm
	#input: None
	#output: None
	def run(self):
		while True:
			try:
				#send heart beat to frontend server
				res = requests.get("http://{}/heart_beat?server_type={}&server_id={}".format(self.frontend_addr, self.server_type, self.server_id))
				#send heart beat to all order replicas
				#for addr in replicas:
				for server_id in range(len(self.catalog_server_addr)):
					if server_id != self.server_id:
						res = requests.get("http://{}/heart_beat?server_type={}&server_id={}".format(self.catalog_server_addr[server_id], self.server_type, self.server_id))	
			except:
				print('remote server is not ready yet')
			#Stop listener
			if self.stop_listener:
				print('heart beater stopped')
				break
			
			time.sleep(1)
		