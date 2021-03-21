from flask import Flask, redirect, jsonify, request


#Create the book store front end server instance
app = Flask(__name__)
#Initialition of inference model
server_addr = {}

#Perform inference request 
#input: images
#output: classification of all images
@app.route('/search', methods=['GET'])
def search():
    #Only process POST/GET request
    topic = request.args.get('topic')
    return redirect('http://{}/query_by_topic?topic={}'.format(server_addr['catalog'], topic))

#Perform inference request 
#input: images
#output: classification of all images
@app.route('/lookup', methods=['GET'])
def lookup():
    #Only process POST/GET request
    item_number = request.args.get('item_number')
    return redirect('http://{}/query_by_item?item_number={}'.format(server_addr['catalog'], item_number))

#Perform inference request 
#input: images
#output: classification of all images
@app.route('/buy', methods=['GET'])
def buy():
    #Only process POST/GET request
    item_number = request.args.get('item_number')
    return redirect('http://{}/buy?item_number={}'.format(server_addr['order'], item_number))

def getServerAddress(file_name):
    file = open(file_name, 'r')
    for line in file.readlines():
        tokens = line.strip().split(',')
        server_addr[tokens[0]] = tokens[1]
    
#start the inferece server
if __name__ == '__main__':
    getServerAddress('config')
    app.run(host='0.0.0.0', port=8000, threaded=True)