import requests
from src.communication.request import Request

#Replica protocal (Primary-Backup) class
class ReplicaProtocol():
	#ReplicaProtocol constructor
	def __init__(self, id, server_type, config):
		#self.config = config
		self.id = id #server id
		self.replica_addr = config.server_addr[server_type] #address of all replica
		self.cache_addr = config.getAddress('cache') #address of cache server
		self.server_health = config.server_health[server_type] #Record whether the server is alive

	#get current primary server
	#input: None
	#output: primary server index
	def get_primary_server(self):
		server_idx = 0
		while self.server_health[server_idx] == False:
			server_idx += 1
		return server_idx
	
	#update server's health status
	#input: 
	#@server_id = id of server
	#@is_alive = health status
	#output: None
	def update_replica_health(self, server_id, is_alive):
		self.server_health[server_id] = is_alive
	
	#check whether the server is a primary
	#input: server id
	#output: whether the id is a primary
	def is_primary(self):
		return self.id == self.get_primary_server()
	
	#notify all replicated server to update
	#input:
	#@id = server id
	#@req = HTTP requests
	#output: None
	def notify_replicas_update(self, id, req):
		
		req_threads = []
		
		#notify cache server to update
		req_thread = Request(req.format(self.cache_addr))
		req_thread.start()
		req_threads.append(req_thread)
		
		#notify replicas to update
		for server_id in range(len(self.replica_addr)):
			if server_id != self.id and self.server_health[server_id]:
				req_thread = Request(req.format(self.replica_addr[server_id]))
				req_thread.start()
				req_threads.append(req_thread)

		#wait for each requests' response
		for req_thread in req_threads:
			req_thread.join()
		
	#notify primary server to update
	#input:
	#@req = HTTP requests
	#output: None
	def notify_primary_update(self, req):
		can_notify = True
		primary_idx = self.get_primary_server()
		if primary_idx != self.id and self.server_health[primary_idx]:
			try:
				requests.get(req.format(self.replica_addr[primary_idx]))
			except:
				can_notify = False
				self.server_health[server_id] = False
				print('primary with addr {} is crahsed'.format(self.replica_addr[server_id]))
			
		return can_notify

	#recover server from a crashed state
	#input: None
	#output: book list and detail information
	def recover(self):
		#resync with replicas
		req = "http://{}/resync?server_id={}".format('{}', self.id)
		books = None

		for server_id in range(len(self.replica_addr)):
			if server_id != self.id and self.server_health[server_id]:
				try:
					res = requests.get(req.format(self.replica_addr[server_id])).json()
					books = Book.recover_book_list(res)
				except:
					self.server_health[server_id] = False
		
		return books
		