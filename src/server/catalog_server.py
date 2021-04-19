import io
import json, os, signal
from flask import Flask, redirect, jsonify, request
import threading
from os import path
from src.utils.logger import Logger
from src.utils.book import Book
from src.utils.config import Config
from src.communication.replica_protocol import ReplicaProtocol
from src.communication.heart_beater import HeartBeater
from src.communication.heart_beat_listener import HeartBeatListener
import sys
import logging

#Disable unnecessary log
log = logging.getLogger('werkzeug')
log.disabled = True

#Create the book store catalog end server instance
app = Flask(__name__)

#Define server id
id = -1

#Initialition of book store instance
books = {}
#lock to prevent race condition of update request
lock = threading.Lock()

#logger used to store log
logger = Logger('./output/order_log')

#global server address reference
config = Config('config')

#Get replication protocol (Primary Back-up Replcaition)
rp = ReplicaProtocol(id, 'catalog', config)

#Crate a hear beat listener to monitor health of replicas
hb_listener = HeartBeatListener(config, id)

#Create heartbeater to send heart beat message to frontend server
hb = HeartBeater('catalog', -1, config)

#Perform inference request 
#input: search topic
#output: list of book matched the topic
@app.route('/query_by_topic', methods=['GET'])
def query_by_topic():
	#Get input parameter from HTTP request
	topic = request.args.get('topic')
	book_lst = []
	print('Catalog Server: Receive query_by_topic request where topic=', topic)
	
	#Search all matched book for the topic
	for item_number in books:
		b = books[item_number]
		if b.type == topic:
			book_lst.append(b.get_title())
	
	#log transaction
	logger.log('query_by_topic,{}'.format(topic))
	return jsonify({'result': book_lst})

#Perform inference request 
#input: lookup book item number
#output: classification of all images
@app.route('/query_by_item', methods=['GET'])
def query_by_item():
	item_number = request.args.get('item_number')
	print('Catalog Server: Receive query_by_item request where item_number=', item_number)
	
	#log transaction
	logger.log('query_by_item,{}'.format(item_number))
	return jsonify({'result': books[item_number].get_info()})

#Process update request
#input: book item number, book cost, update number for the book item
#output: Result of update request
@app.route('/update', methods=['GET'])
def update():
	#Get input parameter from HTTP request
	res = {'result': 'Success'}
	book = books[request.args.get('item_number')]
	cost = request.args.get('cost')
	stock = int(request.args.get('stock'))
	global id
	print('Catalog Server: Receive update request where item_number={}, cost={}, stock={}'.format(book.item_number, cost, stock))
	
	if rp.is_primary():
		#invalidate cache
		rp.invalidate_cache("http://{}/invalidate_cache?item_number={}".format(config.getAddress('cache'), book.item_number))
		#If server is the primary, Perform update operation
		res = perform_update(book, cost, stock)
		if res['result'] == 'Failed':
			return jsonify(res)
		#notify all replica to update
		rp.notify_replicas_update(id, "http://{}/internal_update?item_number={}&stock={}&cost={}".format('{}', book.item_number, stock, 'na'))
	else:
		#Server is not a Primary, notify primary server to update
		res = rp.notify_primary_update("http://{}/internal_update?item_number={}&stock={}&cost={}".format('{}', book.item_number, stock, 'na'))
	return jsonify(res)

#Process update request sent by replicas
#input: book item number, book cost, update number for the book item
#output: Result of update request
@app.route('/internal_update', methods=['GET'])
def internal_update():
	#Get input parameter from HTTP request
	book = books[request.args.get('item_number')]
	cost = request.args.get('cost')
	stock = int(request.args.get('stock'))
	global id
	print('Catalog Server: Receive internal update request where item_number={}, cost={}, stock={}'.format(book.item_number, cost, stock))
	
	#Perform update operation
	if rp.is_primary():
		#invalidate cache
		rp.invalidate_cache("http://{}/invalidate_cache?item_number={}".format(rp.cache_addr, book.item_number))
	res = perform_update(book, cost, stock)
	if res['result'] == 'Failed':
		return jsonify(res)
	#if server is primary, notify all other replicas to update
	if rp.is_primary():
		rp.notify_replicas_update(id, "http://{}/internal_update?item_number={}&stock={}&cost={}".format('{}', book.item_number, stock, 'na'))
		
	return jsonify(res)
	

#Process re-sync request
#input: book item number, book cost, update number for the book item
#output: Result of update request
@app.route('/resync', methods=['GET'])
def resync():
	#Get input parameter from HTTP request
	server_id = int(request.args.get('server_id'))
	config.update_server_health('catalog', server_id, True)
	logger.log('resync,{}'.format(server_id))
	return jsonify(Book.get_book_list(books))


#Perform update operation
#input: book instance, cost of the book, result of the HTTP reuqest
#output: Result of update operation
def perform_update(book, cost, stock):
	res = {'result': 'Success'}
	
	#lock transaction to prevent race condition of update operation
	lock.acquire()
	#update cost if any request
	if cost != 'na':
		book.update_cost(cost)
	#update stock if any request
	if stock != 'na':
		if book.update_stock(stock) == False:
			res['result'] = 'Failed'
			print('out of stock, buy operation failed!')
	lock.release()
	
	#if operation executed, log trasnaction
	if(res['result'] == 'Success'):
		logger.log('update,{},{},{}'.format(book.item_number, cost, stock))
	
	return res


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


#Shut down the server forcely
#input: None
#output: Shout down result
@app.route('/shutdown', methods=['GET'])
def shutdown():
	hb.stop()
	logger.log('shutdown')
	return jsonify({'result': 'Succeed'})


#Recover the server forcely
#input: None
#output: recover result
@app.route('/recover', methods=['GET'])
def recover():
	global id
	global books
	global hb

	hb = HeartBeater('catalog', id, config)
	hb.start()
	books = rp.recover() #recover from a failed state
	
	print('catalog {} recovered from crash'.format(id))
	logger.log('recover')
	return jsonify({'result': 'Succeed'})


#Set initialize book store satus
#input: catalog log file name
#output: None
def init_state(file_name):
	file = open(file_name, 'r')
	for line in file.readlines():
		tokens = line.strip().split(',')
		#if find init catalog log, add the book info to the book store 
		books[tokens[1]] = Book(tokens[1], int(tokens[2]), tokens[3], tokens[4], tokens[5])
		logger.log(line)
        
    
#start the bookstore catalog server
if __name__ == '__main__':
	#get server id
	print(sys.argv)
	id = int(sys.argv[1])
	rp.id = id
	logger.log_file = './output/catalog{}_log'.format(id)
	
	#initialize book store satus
	init_state('./init_bookstore')
	
	#start heart beater
	hb_listener.id = id
	hb.server_id = id
	hb.start()
	
	#start server
	logger.log('catalog server started,{}'.format(id))
	app.run(host='0.0.0.0', port=8001 + id, threaded=True)