import io
import json
from flask import Flask, redirect, jsonify, request
import requests

#Create the book store front end server instance
app = Flask(__name__)
server_addr = {}

#Perform inference request 
#input: images
#output: classification of all images
@app.route('/buy', methods=['GET'])
def buy():
    item_number = request.args.get('item_number')
    res = requests.get("http://{}/query_by_item?item_number={}".format(server_addr['catalog'], item_number))

    if int(res.json()['result']['stock']) == 0:
        return jsonify({'result': 'Failed'})
    
    res = requests.get("http://{}/update?item_number={}&stock={}&cost={}".format(
                                                                    server_addr['catalog'], item_number,-1,'na'))
    
    log_transaction('bought book {}'.format(item_number))
    
    return res.json()

def log_transaction(msg):
    f = open('order_log', 'a')
    f.write(msg)
    f.write('\n')
    f.close()

def getServerAddress(file_name):
    file = open(file_name, 'r')
    for line in file.readlines():
        tokens = line.strip().split(',')
        server_addr[tokens[0]] = tokens[1]
        
    
#start the inferece server
if __name__ == '__main__':
    getServerAddress('config')
    app.run(host='0.0.0.0', port=8002, threaded=True)