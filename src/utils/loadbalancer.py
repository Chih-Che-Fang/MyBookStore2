#LoadBlancer is used to redirect request to alive replicas evenly 
class LoadBlancer():
	#Constructor of Monitor
	def __init__(self, config_file):
		self.server_addr = {} #replica address list for each type of server
		self.server_rr = {}  #Round-robin value 
		
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
			self.server_rr[server] = 0

	#Return the request server's address using round-robin algorithm
	def getAddress(self, server_name):
		
		#Get the index of next server that is going to receive the request (Round-robin algorithm)
		num_rep = len(self.server_addr[server_name])
		server_idx = self.server_rr[server_name] % num_rep
		
		#Update round robin value
		self.server_rr[server_name] = (server_idx + 1) % num_rep
		return self.server_addr[server_name][server_idx]