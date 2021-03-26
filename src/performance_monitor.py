#Monitor is used to trace averaged response time of a request
class Monitor():
	#Constructor of Monitor
	def __init__(self, server, op):
		self.num_req = 0
		self.total_time = 0
		self.server = server
		self.op = op
	#Add a response time sample and print averaged response time
	def add_sample(self, res_time):
		#Accumulate response time 
		self.total_time += res_time
		self.num_req += 1

		#Calculate averaged response time
		avg_res_time = self.total_time * 1000 / self.num_req
		print('{}: Avg Response Time of {} Request={} ms'.format(self.server, self.op, avg_res_time))