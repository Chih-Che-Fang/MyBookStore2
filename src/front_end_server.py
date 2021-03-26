from flask import Flask, redirect, jsonify, request
import time
import requests
from performance_monitor import Monitor

#Create the book store front end server instance
app = Flask(__name__)
#Crate a global server address reference
server_addr = {}

#Performance monitors to trace average response time
q_by_topic_monitor = Monitor('Frontend Server', 'query by item topic')
q_by_item_monitor = Monitor('Frontend Server', 'query by item number')
buy_monitor = Monitor('Frontend Server', 'buy')

#Process search client request 
#input: book topic
#output: list of book of the searched topic
@app.route('/search', methods=['GET'])
def search():
	print('Frontend Server: Redirect search request to catalog server')
	topic = request.args.get('topic')
	
	#redirect search request to catalog server
	start_time = time.time()
	res = requests.get('http://{}/query_by_topic?topic={}'.format(server_addr['catalog'], topic)).json()
	q_by_topic_monitor.add_sample(time.time() - start_time)
	
	return res
	

#Process search client request 
#input: book item number
#output: detail book inforamtion of the item number
@app.route('/lookup', methods=['GET'])
def lookup():
	print('Frontend Server: Redirect lookup request to catalog server')
	item_number = request.args.get('item_number')
	
	#redirect search request to catalog server
	start_time = time.time()
	res = requests.get('http://{}/query_by_item?item_number={}'.format(server_addr['catalog'], item_number)).json()
	q_by_item_monitor.add_sample(time.time() - start_time)
	
	return res

#Process search client request 
#input: book item number
#output: transaction result of buy request
@app.route('/buy', methods=['GET'])
def buy():
	print('Frontend Server: Redirect buy request to catalog server')
	item_number = request.args.get('item_number')

	#redirect search request to order server
	start_time = time.time()
	res = requests.get('http://{}/buy?item_number={}'.format(server_addr['order'], item_number)).json()
	buy_monitor.add_sample(time.time() - start_time)
	
	return res

#Set a global server address reference
#input: global address config file name
#output: None
def setServerAddress(file_name):
    file = open(file_name, 'r')
    for line in file.readlines():
        tokens = line.strip().split(',')
        server_addr[tokens[0]] = tokens[1]
    
#start the bookstore frontend server
if __name__ == '__main__':
    setServerAddress('config')
    app.run(host='0.0.0.0', port=8000, threaded=True)