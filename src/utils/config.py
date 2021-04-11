#Monitor is used to trace averaged response time of a request
class Config():
	#Constructor of Monitor
	def __init__(self, config_file):
		self.server_addr = {}
		
		#Set a global server address reference
		file = open(config_file, 'r')
		for line in file.readlines():
			tokens = line.strip().split(',')
			self.server_addr[tokens[0]] = tokens[1]


	def getAddress(self, server_name):
		return self.server_addr[server_name]