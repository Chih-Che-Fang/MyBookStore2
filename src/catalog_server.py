import io
import json
from flask import Flask, redirect, jsonify, request
import threading

#Create the book store front end server instance
app = Flask(__name__)
#Initialition of inference model
books = {}
lock = threading.Lock()



class Book(object):
    def __init__(self, item_number, stock, cost, type, title):
        self.item_number = item_number
        self.stock = stock
        self.cost = cost
        self.type = type
        self.title = title
    def decrement(self):
        if self.stock == 0:
            return False
        self.stock -= 1
        return True
    def increment(self):
        self.stock += 1
    def update_cost(self, cost):
        self.cost = cost
    def get_info(self):
        return {'item_number':self.item_number, 'stock':self.stock, 'cost':self.cost
                , 'type':self.type, 'title':self.title}
    def get_title(self):
        return {'item_number':self.item_number, 'title':self.title}

#Perform inference request 
#input: images
#output: classification of all images
@app.route('/query_by_topic', methods=['GET'])
def query_by_topic():
    #Only process POST/GET request
    topic = request.args.get('topic').replace('%20', ' ')
    book_lst = []
    print('query_by_topic where topic=', topic)
    
    for item_number in books:
        b = books[item_number]
        if b.type == topic:
            book_lst.append(b.get_title())
    
    log_transaction('query_by_topic,{}'.format(topic))
    return jsonify({'result': book_lst})

#Perform inference request 
#input: images
#output: classification of all images
@app.route('/query_by_item', methods=['GET'])
def query_by_item():
    #Only process POST/GET request
    item_number = request.args.get('item_number')
    log_transaction('query_by_item,{}'.format(item_number))
    return jsonify({'result': books[item_number].get_info()})

#Perform inference request 
#input: images
#output: classification of all images
@app.route('/update', methods=['GET'])
def update():
    #Only process POST/GET request
    res = {'result': 'Success'}
    book = books[request.args.get('item_number')]
    cost = request.args.get('cost')
    stock = request.args.get('stock')

    lock.acquire()
    if cost != 'na':
        book.update_cost(cost)
    if stock != 'na':
        if book.decrement() == False:
            res['result'] = 'Failed'
    lock.release()
    
    if(res['result'] == 'Success'):
        log_transaction('update,{},{},{}'.format(book.item_number, cost, stock))
    
    return  jsonify(res)


def log_transaction(msg):
    f = open('./output/catalog_log', 'a')
    f.write(msg)
    f.write('\n')
    f.close()

def get_init_state(file_name):
    file = open(file_name, 'r')
    for line in file.readlines():
        tokens = line.strip().split(',')

        if tokens[0] == 'init':
            print(tokens[1])
            books[tokens[1]] = Book(tokens[1], int(tokens[2]), tokens[3], tokens[4], tokens[5])
        
    
#start the inferece server
if __name__ == '__main__':
    get_init_state('./output/catalog_log')
    app.run(host='0.0.0.0', port=8001, threaded=True)