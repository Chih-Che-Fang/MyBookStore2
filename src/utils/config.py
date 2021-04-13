#Config is used to trace address of all servers
class Config():
	#Constructor of Config
	def __init__(self, config_file):
		self.server_addr = {} #replica address list for each type of server
		
		#Build a global server/replicas address reference
		file = open(config_file, 'r')
		for line in file.readlines():
			tokens = line.strip().split(',')
			
			server = tokens[0]
			addr = tokens[1]
			
			#Create address list if never seen this type of server
			if(server not in self.server_addr):
				self.server_addr[server] = []
			
			#Append server's address to address list
			self.server_addr[server].append(addr)
	
	#Get address of requested server
	def getAddress(self, server_name):
		return self.server_addr[server_name][0]