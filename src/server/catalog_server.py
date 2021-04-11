import io
import json
from flask import Flask, redirect, jsonify, request
import threading
from src.utils.logger import Logger
from src.utils.book import Book
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
logger = Logger('./output/catalog_log')

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
	stock = request.args.get('stock')
	print('Catalog Server: Receive update request where item_number={}, cost={}, stock={}'.format(book.item_number, cost, stock))
	
	#lock transaction to prevent race condition of update operation
	lock.acquire()
	#update cost if any request
	if cost != 'na':
		book.update_cost(cost)
	#update stock if any request
	if stock != 'na':
		if book.decrease_stock() == False:
			res['result'] = 'Failed'
	lock.release()
	
	#if operation executed, log trasnaction
	if(res['result'] == 'Success'):
		logger.log('update,{},{},{}'.format(book.item_number, cost, stock))
	
	return  jsonify(res)
	
#Set initialize book store satus
#input: catalog log file name
#output: None
def set_init_state(file_name):
    file = open(file_name, 'r')
    for line in file.readlines():
        tokens = line.strip().split(',')
		#if find init catalog log, add the book info to the book store 
        if tokens[0] == 'init':
            books[tokens[1]] = Book(tokens[1], int(tokens[2]), tokens[3], tokens[4], tokens[5])
        
    
#start the bookstore catalog server
if __name__ == '__main__':
	id = int(sys.argv[1])
	set_init_state('./output/catalog_log')
	app.run(host='0.0.0.0', port=8001 + id, threaded=True)