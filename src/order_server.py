import io
import json
from flask import Flask, redirect, jsonify, request
import requests
import time
from performance_monitor import Monitor

#Create the book store order server instance
app = Flask(__name__)
#Crate a global server address reference
server_addr = {}
#Create Performance monitors to trace average response time
q_by_item_monitor = Monitor('Order Server', 'query_by_item')
update_monitor = Monitor('Order Server', 'update')

#Process buy request
#input: book item number, book cost, update number for the book item
#output: Result of update request
@app.route('/buy', methods=['GET'])
def buy():
	
	#send query request to catalog server to get the number of book
	item_number = request.args.get('item_number')
	print('Order Server: Receive buy request where item_number=', item_number)
	
	start_time = time.time()
	res = requests.get("http://{}/query_by_item?item_number={}".format(server_addr['catalog'], item_number)).json()
	q_by_item_monitor.add_sample(time.time() - start_time)
	

	#if the book is sold out, skip transaction and return failed result
	if int(res['result']['stock']) == 0:
		return jsonify({'result': 'Failed'})
	
	#Send update request to catalog server to buy the book
	start_time = time.time()
	res = requests.get("http://{}/update?item_number={}&stock={}&cost={}".format(
																	server_addr['catalog'], item_number,-1,'na')).json()
	update_monitor.add_sample(time.time() - start_time)
	
	#if buy operation executed, log trasnaction
	if res['result'] == 'Success':
		log_transaction('bought book {}'.format(item_number))
	
	return res

#Log executed transaction or request
#input: log message
#output: None
def log_transaction(msg):
	print(msg)
	f = open('./output/order_log', 'a')
	f.write(msg)
	f.write('\n')
	f.close()
	
#Set a global server address reference
#input: global address config file name
#output: None
def setServerAddress(file_name):
    file = open(file_name, 'r')
    for line in file.readlines():
        tokens = line.strip().split(',')
        server_addr[tokens[0]] = tokens[1]
        
    
#start the bookstore order server
if __name__ == '__main__':
    setServerAddress('config')
    app.run(host='0.0.0.0', port=8002, threaded=True)