import io
import json
from flask import Flask, redirect, jsonify, request
import requests
import time
from src.utils.performance_monitor import Monitor
from src.utils.logger import Logger
from src.communication.loadbalancer import LoadBlancer
from src.utils.config import Config
from src.communication.heart_beater import HeartBeater
from src.communication.heart_beat_listener import HeartBeatListener
import sys


#Create the book store order server instance
app = Flask(__name__)

#Define server id
id = -1


#Create Performance monitors to trace average response time
q_by_item_monitor = Monitor('Order Server', 'query_by_item')
update_monitor = Monitor('Order Server', 'update')

#logger used to store log
logger = Logger('./output/order_log')

#global server address reference
config = Config('config')

#Process buy request
#input: book item number, book cost, update number for the book item
#output: Result of update request
@app.route('/buy', methods=['GET'])
def buy():
	
	#send query request to catalog server to get the number of book
	global id
	item_number = request.args.get('item_number')

	print('Order Server: Receive buy request where item_number=', item_number)
	
	start_time = time.time()
	res = requests.get("http://{}/query_by_item?item_number={}".format(config.getAddress('catalog', id), item_number)).json()
	q_by_item_monitor.add_sample(time.time() - start_time)
	

	#if the book is sold out, skip transaction and return failed result
	print(res)
	if res['result'] == 'Failed' or int(res['result']['stock']) == 0:
		return jsonify({'result': 'Failed'})
	
	#Send update request to catalog server to buy the book
	start_time = time.time()
	res = requests.get("http://{}/update?item_number={}&stock={}&cost={}".format(config.getAddress('catalog', id), item_number, -1, 'na')).json()
	update_monitor.add_sample(time.time() - start_time)
	
	#if buy operation executed, log trasnaction
	if res['result'] == 'Success':
		logger.log('bought book {}'.format(item_number))
	
	return jsonify(res)
        
##Process heart beat message
##input: server id
##output: ACK of heart beat
#@app.route('/heart_beat', methods=['GET'])
#def heart_beat():
#	server_type = request.args.get('server_type')
#	server_id = request.args.get('server_id')
#	hb_listener.heart_beat(server_type, int(server_id))
#	#print('Frontend Server: Receive heart beat message from {} server where id = {}'.format(server_type, server_id))
#	return jsonify({'result': 'Success'})

    
#start the bookstore order server
if __name__ == '__main__':
	#get server id
	id = int(sys.argv[1])
	logger.log_file = './output/order{}_log'.format(id)
	
	#start heart beater
	#hb.server_id = id
	#hb.start()
	
	#start server
	logger.log('order server started,{}'.format(id))
	app.run(host='0.0.0.0', port=8003 + id, threaded=True)