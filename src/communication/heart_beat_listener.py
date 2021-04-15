import requests
import threading
import time

#HeartBeater is used to send hearbeat message to fronten server and perform fault detection
class HeartBeatListener(threading.Thread):
	#Constructor of HeartBeater
	def __init__(self, lb):
		threading.Thread.__init__(self)
		
		cur_time = time.time()
		self.heart_beat_timestamp = {'catalog': [cur_time, cur_time], 'order': [cur_time, cur_time]}
		self.lb = lb

	#Record heart beat timestamp
	#input:
	#@server_type = type of the target server
	#@server_id = id of the target server
	#output: None
	def heart_beat(self, server_type, server_id):
		self.heart_beat_timestamp[server_type][server_id] = time.time()

	#Return the request server's address using round-robin algorithm
	def run(self):
		
		while True:
			cur_time = time.time()
			for server in self.heart_beat_timestamp:
				timestamps = self.heart_beat_timestamp[server]
				for id in range(len(timestamps)):
					#send health status update to loadbalance
					if (cur_time - timestamps[id]) > 5:
						#print("{} Server with id {} is died".format(server, id))
						self.lb.update_server_health(server, id, False)
					else:
						#print("{} Server with id {} is alive".format(server, id))
						self.lb.update_server_health(server, id, True)
			time.sleep(5)
		