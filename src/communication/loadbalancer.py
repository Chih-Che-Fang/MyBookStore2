#LoadBlancer is used to redirect request to alive replicas evenly 
class LoadBlancer():
	#Constructor of Monitor
	def __init__(self, config):
		self.config = config
		self.server_addr = config.server_addr #replica address list for each type of server
		self.server_rr = {}  #Round-robin value 
		self.server_health = {} #Record whether the server is alive
		
		#Init round-robin value
		for server in self.server_addr:
			self.server_rr[server] = -1
			self.server_health[server] = [True] * len(self.server_addr[server])

	#update server's health status
	def update_server_health(self, server_type, server_id, is_alive):
		self.server_health[server_type][server_id] = is_alive
	
	#get next alive server id
	def get_next_server(self, server_type):
		
		num_rep = len(self.server_addr[server_type])
		server_idx = (self.server_rr[server_type] + 1) % num_rep

		while self.server_health[server_type][server_idx] == False:
			self.server_rr[server_type] = (server_idx + 1) % num_rep
		
		return server_idx

	#Return the request server's address using round-robin algorithm
	def getAddress(self, server_type):
		#Get the index of next server that is going to receive the request (Round-robin algorithm)
		server_idx = self.get_next_server(server_type)
		return self.server_addr[server_type][server_idx]