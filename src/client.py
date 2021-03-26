import io
import json
import requests
import threading
import time
import os

#Crate a global server address reference
frontend_addr = ''
#monitor = Monitor('Client', 'search')

#Client thread used for concurrent HTTP request test
class Client (threading.Thread):
	#Client thread constructor
	def __init__(self, c_id, num_req, run_perf_test):
		threading.Thread.__init__(self)
		self.c_id = c_id
		self.num_req = num_req
		self.run_perf_test = run_perf_test

	#Perform a series of search request to frontend server
	def run(self):
		if self.run_perf_test:
			#Run performance test
			total_time = 0
			for i in range(self.num_req):
				start_time = time.time()
				#print('Client{}: Get response '.format(self.c_id), send_req(self.c_id, "http://{}/search?topic={}".format(frontend_addr, 'graduate+school')))
				print('Client0: Get response '.format(self.c_id), send_req(self.c_id, "http://{}/lookup?item_number={}".format(frontend_addr, 3)))
				#print('Client0: Get response '.format(self.c_id), send_req(self.c_id, "http://{}/buy?item_number={}".format(frontend_addr, 2)))
				total_time += (time.time() - start_time)
			log_transaction('Client{}: Averaged Execuation time for {} request is {} ms'.format(self.c_id, self.num_req, total_time * 1000 / self.num_req))
		else:
			#Run test4:  (Race Condition) 4 clients buy book "RPCs for Dummies" that only has 3 stock concurrently, only 3 client can buy the book
			print('Client{}: Get response '.format(self.c_id), send_req(self.c_id, "http://{}/buy?item_number={}".format(frontend_addr, '2')))

			
#Log executed transaction or request
#input: log message
#output: None
def log_transaction(msg):
	print(msg)
	f = open('./output/client_log', 'a')
	f.write(msg)
	f.write('\n')
	f.close()			


#Set a HTTP request to server
#input: request message
#output: json response from server
def send_req(c_id, msg):
	print('Client{}: Send request {}'.format(c_id, msg))
	return requests.get(msg).json()

#Get a global server address reference
#input: global address config file name
#output: None
def getServerAddress(file_name):
	file = open(file_name, 'r')
	for line in file.readlines():
		tokens = line.strip().split(',')
		return tokens[1]
        
    
#start the client requests
if __name__ == '__main__':
	
	frontend_addr = getServerAddress('config')
# print(frontend_addr)
# #Run test1: Perform lookup and search methods correctly.
# print('Client0: Get response ', send_req(0, "http://{}/search?topic={}".format(frontend_addr, 'distributed+systems')))
# print('Client0: Get response ', send_req(0, "http://{}/search?topic={}".format(frontend_addr, 'graduate+school')))
# 
# for i in range(4):
# 	#Run test2: Perform lookup and search methods correctly.
# 	print('Client0: Get response ', send_req(0, "http://{}/lookup?item_number={}".format(frontend_addr, i + 1)))
# 	#Run test3: Perform Buy operations run and update the stock of the item correctly
# 	print('Client0: Get response ', send_req(0, "http://{}/buy?item_number={}".format(frontend_addr, '1')))
	
	
	##Run Performance Test
	#num_req = 500
	#total_time = 0
	#for i in range(num_req):
	#	start_time = time.time()
	#	# print('Client0: Get response ', send_req(0, "http://{}/search?topic={}".format(frontend_addr, 'graduate+school')))
	#	print('Client0: Get response ', send_req(0, "http://{}/lookup?item_number={}".format(frontend_addr, 2)))
	#	total_time += (time.time() - start_time)
	#print('Client0: Averaged Execuation time for {} request is {} ms'.format(num_req, total_time * 1000 / num_req))
	
	
	##Run test4:  (Race Condition) 4 clients buy book "RPCs for Dummies" that only has 3 stock concurrently, only 3 client can buy the book
	#clients = []
	#num_clients = 4
	#num_req = 1
	#for i in range(num_clients):
	#	c = Client(i + 1, num_req, False)
	#	c.start()
	#	clients.append(c)
	#
	#for c in clients:
	#	c.join()	


	#Run Performance Test
	clients = []
	num_clients = 9
	num_req = 500
	for i in range(num_clients):
		c = Client(i + 1, num_req, True)
		c.start()
		clients.append(c)
	
	for c in clients:
		c.join()
		

