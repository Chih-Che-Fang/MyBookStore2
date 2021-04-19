import requests
import threading
import time

#HeartBeater is used to send hearbeat message to fronten server and perform fault detection
class HeartBeatListener(threading.Thread):
	#Constructor of HeartBeater
	def __init__(self, config, id = -1):
		threading.Thread.__init__(self)
		
		cur_time = time.time()
		self.heart_beat_timestamp = {'catalog': [cur_time, cur_time], 'order': [cur_time, cur_time]}
		self.config = config
		self.started = False
		self.id = id

	#Record heart beat timestamp
	#input:
	#@server_type = type of the target server
	#@server_id = id of the target server
	#output: None
	def heart_beat(self, server_type, server_id):
		#if heart beat listener hasn't been started, start it
		if self.started == False:
			self.start()
		self.heart_beat_timestamp[server_type][server_id] = time.time()
		self.config.update_server_health('catalog', int(server_id), True)
		self.config.update_server_health('order', int(server_id), True)

	#Return the request server's address using round-robin algorithm
	def run(self):
		self.started = True
		server = 'catalog'
		while True:
			cur_time = time.time()
			timestamps = self.heart_beat_timestamp[server]
			for id in range(len(timestamps)):
				if self.id != id:
					#send health status update to loadbalance
					if (cur_time - timestamps[id]) > 1:
						#print("{} Server with id {} is died".format(server, id))
						self.config.update_server_health(server, id, False)
						self.config.update_server_health('order', id, False)
					else:
						#print("{} Server with id {} is alive".format(server, id))
						self.config.update_server_health(server, id, True)
						self.config.update_server_health('order', id, True)
			time.sleep(1)
		