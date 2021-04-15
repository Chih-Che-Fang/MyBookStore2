import io
import json
from flask import Flask, redirect, jsonify, request
import threading
from os import path
from src.utils.logger import Logger
from src.utils.book import Book
from src.utils.config import Config
from src.communication.replica_protocol import ReplicaProtocol
from src.communication.heart_beater import HeartBeater
import sys

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
		#If server is the primary, Perform update operation
		res = perform_update(book, cost, stock)
		if res['result'] == 'Failed':
			return jsonify(res)
		#notify all replica to update
		rp.notify_replicas_update(id, "http://{}/internal_update?item_number={}&stock={}&cost={}".format('{}', book.item_number, stock, 'na'))
	else:
		#Server is not a Primary, notify primary server to update
		can_notify = rp.notify_primary_update("http://{}/internal_update?item_number={}&stock={}&cost={}".format('{}', book.item_number, stock, 'na'))
		if not can_notify:
			#If primary server crashed, Perform update operation
			res = perform_update(book, cost, stock)
			if res['result'] == 'Failed':
				return jsonify(res)
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
	rp.update_replica_health(server_id, True)
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
	lock.release()
	
	#if operation executed, log trasnaction
	if(res['result'] == 'Success'):
		logger.log('update,{},{},{}'.format(book.item_number, cost, stock))
	
	return res


#Set initialize book store satus
#input: catalog log file name
#output: None
def init_state(file_name):
	#Cata log server has crashed before
	if path.exists(logger.log_file):
		return false
	
	file = open(file_name, 'r')
	for line in file.readlines():
		tokens = line.strip().split(',')
		#if find init catalog log, add the book info to the book store 
		books[tokens[1]] = Book(tokens[1], int(tokens[2]), tokens[3], tokens[4], tokens[5])
		logger.log(line)
	return True
        
    
#start the bookstore catalog server
if __name__ == '__main__':
	#get server id
	print(sys.argv)
	id = int(sys.argv[1])
	rp.id = id
	logger.log_file = './output/catalog{}_log'.format(id)
	
	#initialize/recover book store satus
	if init_state('./init_bookstore') == False:
		books = rp.recover() #recover from a failed state
	
	#start heart beater
	hb.server_id = id
	hb.start()
	
	#start server
	logger.log('catalog server started,{}'.format(id))
	app.run(host='0.0.0.0', port=8001 + id, threaded=True)