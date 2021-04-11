from flask import Flask, redirect, jsonify, request
import time
import requests
from src.utils.performance_monitor import Monitor
from src.utils.loadbalancer import LoadBlancer
import json

#Create the book store front end server instance
app = Flask(__name__)
#Crate a global server address reference
lb = LoadBlancer('config')

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
	cache = requests.get('http://{}/search?topic={}'.format(lb.getAddress('cache'), topic)).json()
	
	if len(cache) == 0:
		#cache doesn't exist, redirect search request to catalog server
		print('Frontend Server: Redirect search request to catalog server')
		start_time = time.time()
		res = requests.get('http://{}/query_by_topic?topic={}'.format(lb.getAddress('catalog'), topic)).json()
		res_cache = requests.get('http://{}/put_search_cache?topic={}&res={}'.format(lb.getAddress('cache'), topic, json.dumps(res)))
		q_by_topic_monitor.add_sample(time.time() - start_time)
		return res
	else:
		#Cache hit! Return cache directly
		print('Frontend Server: Get result from cache')
		return cache
	

#Process search client request 
#input: book item number
#output: detail book inforamtion of the item number
@app.route('/lookup', methods=['GET'])
def lookup():
	print('Frontend Server: Process lookup request')
	item_number = request.args.get('item_number')
	
	#Query the cache server for lookup operation
	cache = requests.get('http://{}/lookup?item_number={}'.format(lb.getAddress('cache'), item_number)).json()
	
	if len(cache) == 0:
		#cache doesn't exist, redirect search request to catalog server
		print('Frontend Server: Redirect lookup request to catalog server')
		start_time = time.time()
		
		res = requests.get('http://{}/query_by_item?item_number={}'.format(lb.getAddress('catalog'), item_number)).json()
		res_cache = requests.get('http://{}/put_lookup_cache?res={}'.format(lb.getAddress('cache'), json.dumps(res))).json()
		q_by_item_monitor.add_sample(time.time() - start_time)
		return res
	else:
		#Cache hit! Return cache directly
		print('Frontend Server: Get result from cache')
		return cache

#Process search client request 
#input: book item number
#output: transaction result of buy request
@app.route('/buy', methods=['GET'])
def buy():
	print('Frontend Server: Redirect buy request to catalog server')
	item_number = request.args.get('item_number')

	#redirect search request to order server
	start_time = time.time()
	res = requests.get('http://{}/buy?item_number={}'.format(lb.getAddress('order'), item_number)).json()
	buy_monitor.add_sample(time.time() - start_time)
	
	return res
    
#start the bookstore frontend server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, threaded=True)