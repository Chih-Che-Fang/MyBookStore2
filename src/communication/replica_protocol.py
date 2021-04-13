import requests

#Replica protocal (Primary-Backup)
class ReplicaProtocol():
	#ReplicaProtocol constructor
	def __init__(self, server_type, config):
		self.config = config
		self.replica_addr = config.server_addr[server_type]
		self.cache_addr = config.getAddress('cache')

	#check whether the server is a primary
	def is_primary(self, id):
		return id == (len(self.replica_addr) - 1)
	
	#notify all replicated server to update
	def notify_replicas_update(self, id, req):
		requests.get(req.format(self.cache_addr)) #notify cache server to update
		for i in range(len(self.replica_addr)):
			if i != id:
				requests.get(req.format(self.replica_addr[i]))
		
	#notify primary server to update
	def notify_primary_update(self, req):
		requests.get(req.format(self.replica_addr[-1]))
		