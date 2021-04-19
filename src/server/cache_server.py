from flask import Flask, redirect, jsonify, request, json
import time
import requests
from src.utils.book import Book
from src.utils.logger import Logger

#Create the book store front end server instance
app = Flask(__name__)

#Cache for search operation
search_cache = {}

#Cache for lookup operation
lookup_cache = {}

#logger used to store log
logger = Logger('./output/cache_log')

#Process search request from frontend server
#input: book topic
#output: list of book of the searched topic
@app.route('/search', methods=['GET'])
def search():
	print('Cache Server: Pass back search cache content to catalog server')
	topic = request.args.get('topic')
	logger.log('search,{}'.format(topic))
	return jsonify({'result': search_cache[topic]} if topic in search_cache else {})
	

#Process search request from frontend server
#input: book item number
#output: detail book inforamtion of the item number
@app.route('/lookup', methods=['GET'])
def lookup():
	print('Cache Server: Pass back lookup cache content to catalog server')
	item_number = request.args.get('item_number')
	logger.log('lookup,{}'.format(item_number))
	return jsonify({'result': lookup_cache[item_number].get_info()} if item_number in lookup_cache else {})

#Put search result into cache
#input: topic
#output: result of put operation
@app.route('/put_search_cache', methods=['GET'])
def put_search_cache():
	
	topic = request.args.get('topic')
	res = json.loads(request.args.get('res'))['result']

	print('Cache Server: Put search({}) result into search cache'.format(topic))
	search_cache[topic] = res
	
	logger.log('put_search_cache,{}'.format(topic))
	return jsonify({'result':'success'})

#Put lookup result into cache
#input: book item number
#output: result of put operation
@app.route('/put_lookup_cache', methods=['GET'])
def put_lookup_cache():
	res = json.loads(request.args.get('res'))['result']
	book = Book(res['item_number'], res['stock'], res['cost'], res['type'], res['title'])
	
	lookup_cache[book.item_number] = book
	print('Cache Server: Put result of lookup({}) into lookup cache'.format(book.item_number))
	logger.log('put_lookup_cache,{}'.format(book.item_number))
	return jsonify({'result':'success'})
	

#Process cache invalidation request from catalog server
#input: book item number
#output: invalidation result
@app.route('/invalidate_cache', methods=['GET'])
def invalidate_cache():
	item_number = request.args.get('item_number')
	lookup_cache.pop(item_number, None)
	logger.log('invalidate_cache,{}'.format(item_number))
	return jsonify({'result':'success'})
    
#start the bookstore frontend server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8005, threaded=True)