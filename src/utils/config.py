#Config is used to trace address of all servers
class Config():
	#Constructor of Config
	def __init__(self, config_file):
		self.server_addr = {} #replica address list for each type of server
		self.server_health = {} #Record whether the server is alive
			
		#Build a global server/replicas address reference
		file = open(config_file, 'r')
		for line in file.readlines():
			tokens = line.strip().split(',')
			
			server = tokens[0]
			addr = tokens[1]
			
			#Create address list if never seen this type of server
			if(server not in self.server_addr):
				self.server_addr[server] = []
				self.server_health[server] = []
			
			#Append server's address to address list
			self.server_addr[server].append(addr)
			self.server_health[server].append(True)
	
	#Get address of requested server
	#input: server's name
	#output: server's address
	def getAddress(self, server_name, server_idx=0):
		return self.server_addr[server_name][server_idx]
		
	#update server's health status
	#input: 
	#@server_type = type of server
	#@server_id = id of server
	#@is_alive = health status
	#output: None
	def update_server_health(self, server_type, server_id, is_alive):
		self.server_health[server_type][server_id] = is_alive