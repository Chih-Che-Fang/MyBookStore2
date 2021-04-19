from flask import Flask, redirect, jsonify, request
import sys
import time
import requests

from src.utils.performance_monitor import Monitor
from src.utils.config import Config
from src.communication.loadbalancer import LoadBlancer
from src.communication.heart_beat_listener import HeartBeatListener
import json
import logging

#Disable unnecessary log
log = logging.getLogger('werkzeug')
log.disabled = True

#Create the book store front end server instance
app = Flask(__name__)

#global server address reference
config = Config('config')

#Crate a load balancer
lb = LoadBlancer(config)

#Crate a hear beat listener to monitor health of replicas
hb_listener = HeartBeatListener(config)

#Performance monitors to trace average response time
q_by_topic_monitor = Monitor('Frontend Server', 'query by item topic')
q_by_item_monitor = Monitor('Frontend Server', 'query by item number')
buy_monitor = Monitor('Frontend Server', 'buy')

#Process search client request 
#input: book topic
#output: list of book of the searched topic
@app.route('/search', methods=['GET'])
def search():
	print('Frontend Server: Process search request')
	topic = request.args.get('topic')
	
	#Query the cache server for search operation
	cache = lb.request('http://{}/search?topic={}'.format({}, topic), 'cache')
	#cache = {}
	
	start_time = time.time()
	if len(cache) == 0:
		#cache doesn't exist, redirect search request to catalog server
		print('Frontend Server: Redirect search request to catalog server')
		
		res = lb.request( 'http://{}/query_by_topic?topic={}'.format({}, topic), 'catalog')

		#put search result into cache
		lb.request('http://{}/put_search_cache?topic={}&res={}'.format({}, topic, json.dumps(res)), 'cache')

		q_by_topic_monitor.add_sample(time.time() - start_time)
		return jsonify(res)
	else:
		#Cache hit! Return cache directly
		print('Frontend Server: Get result from cache')
		q_by_topic_monitor.add_sample(time.time() - start_time)

		return jsonify(cache)
	

#Process search client request 
#input: book item number
#output: detail book inforamtion of the item number
@app.route('/lookup', methods=['GET'])
def lookup():
	print('Frontend Server: Process lookup request')
	item_number = request.args.get('item_number')
	
	#Query the cache server for lookup operation
	cache = lb.request('http://{}/lookup?item_number={}'.format({}, item_number), 'cache')
	#cache = {}
	
	start_time = time.time()
	if len(cache) == 0:
		#cache doesn't exist, redirect search request to catalog server
		print('Frontend Server: Redirect lookup request to catalog server')
		
		res = lb.request('http://{}/query_by_item?item_number={}'.format({}, item_number), 'catalog')
		

		#put search result into cache
		lb.request('http://{}/put_lookup_cache?res={}'.format({}, json.dumps(res)), 'cache')
		
		q_by_item_monitor.add_sample(time.time() - start_time)
		return jsonify(res)
	else:
		#Cache hit! Return cache directly
		print('Frontend Server: Get result from cache')
		q_by_item_monitor.add_sample(time.time() - start_time)
		return jsonify(cache)

#Process search client request 
#input: book item number
#output: transaction result of buy request
@app.route('/buy', methods=['GET'])
def buy():
	print('Frontend Server: Redirect buy request to catalog server')
	item_number = request.args.get('item_number')

	#redirect search request to order server
	start_time = time.time()
	res = lb.request('http://{}/buy?item_number={}'.format({}, item_number), 'order')
	buy_monitor.add_sample(time.time() - start_time)
	
	return jsonify(res)


#Process heart beat message
#input: server id
#output: ACK of heart beat
@app.route('/heart_beat', methods=['GET'])
def heart_beat():
	server_type = request.args.get('server_type')
	server_id = request.args.get('server_id')

	#process hear beat
	hb_listener.heart_beat(server_type, int(server_id))
	#print('Frontend Server: Receive heart beat message from {} server where id = {}'.format(server_type, server_id))
	return jsonify({'result': 'Success'})

#start the bookstore frontend server
if __name__ == '__main__':
	#start server
	app.run(host='0.0.0.0', port=8000, threaded=True)