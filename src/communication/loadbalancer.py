import requests
from flask import jsonify

#LoadBlancer is used to redirect request to alive replicas evenly 
class LoadBlancer():
	#Constructor of LoadBlancer
	def __init__(self, config):
		#self.config = config
		self.server_addr = config.server_addr #replica address list for each type of server
		self.server_rr = {}  #Round-robin value 
		self.server_health = config.server_health #Record whether the server is alive
		
		for server_type in self.server_addr:
			self.server_rr[server_type] = 0

	#Perform HTTP request to alive servers
	#input: HTTP request
	#output: HTTP request result
	def request(self, req):
		res = None
		max_retry = 2
		while res == None and max_retry > 0:
			max_retry -= 1
			try:
				res = requests.get(req).json()
			except:
				#nofitfy current chosen server is crashed
				self.notify_server_crashed('catalog')
				print('server crashed')
				break;
		return jsonify({'result': 'Failed'}) if res == None else res
	
	#update server's health status
	#input: 
	#@server_type = type of server
	#@server_id = id of server
	#@is_alive = health status
	#output: None
	def update_server_health(self, server_type, server_id, is_alive):
		self.server_health[server_type][server_id] = is_alive
	
	
	#nofitfy current chosen server is crashed
	#input: 
	#@server_type = type of server
	#output: None
	def notify_server_crashed(self, server_type):
		server_idx = self.server_rr[server_type]
		self.server_health[server_type][server_idx] = False

	#get next alive server id
	#input: type of server want to access
	#output: server idex
	def get_next_server(self, server_type):
		
		num_rep = len(self.server_addr[server_type])
		server_idx = (self.server_rr[server_type] + 1) % num_rep

		while self.server_health[server_type][server_idx] == False:
			server_idx = (server_idx + 1) % num_rep
		
		self.server_rr[server_type] = server_idx
		return server_idx

	#Return the request server's address using round-robin algorithm
	#input: type of server want to access
	#output: server address
	def getAddress(self, server_type, server_idx = -1):
		#Get the index of next server that is going to receive the request (Round-robin algorithm)
		if server_idx == -1:
			server_idx = self.get_next_server(server_type)
		return self.server_addr[server_type][server_idx]