# My Book Store Design Doc

Authors: Chih-Che Fang

# System Design

## UML Class Diagram
![UML diagram](./UML.png "UML")

## Class Discription  
**frontend_server:** frontend server that process and dispatch client's request  
**catalog_server:** catalog server that host book information and is able to serve update, query_by_item, query_by_topic request from frontend and order server  
**order_server:** order server that process frontend server's buy request  
**SystemMonitor:** A class used to store and calculate the latency/average response time of HTTP requests.  
**Client:** A class used to perform multiple HTTP request to frontend server  
**Book:** A class used to store all book's detailed information like cost, title, topic, ...etc

## Operation Discription:  
The **front end server** supports three operations:  
**search(topic)**: Allows the user to specify a topic and returns all entries belonging to that category (a title and an item number are displayed for each match).  
**lookup(item_number)**: Allows an item number to be specified and returns details such as number of items in stock and cost  
**buy(item_number)**: Allows client to buy a book with the item number  

The **catalog server** supports three operations:  
**query_by_topic(topic)**: Allows the user to specify a topic and returns all entries belonging to that category (a title and an item number are displayed for each match).  
**query_by_item(item_number)**: Allows an item number to be specified and returns details such as number of items in stock and cost  
**update(item_number, cost, stock_update)**: Allows client to update cost or update the stock of book  

The **order server** supports three operations:  
**buy(item_number)**: Allows the user to buy a book with certain item number

## Sequence Diagram
**Client/Server Interaction Workflow**  
![WorkFlow diagram](./WorkFlow.PNG "WorkFlow")



# How it Works
 ## Bootstraping & Communication
I used Flask to implement each server. I start frontend server, catalog server, order server in sequence and finally launch client to send HTTP request to frontend server.
Each Client reprensent a thread so that multiple client can request a single frontend server concurrently. Flask server support multi-threaded so that the server will launch a new thread for processing each new client request. Single Client request is implment as a synchronous request and will wait for frontend server's response.  When frontend server receive client's request, it just lauch a new HTTP request to the corresponding server.

Servers can know each other's IP address and port by reading config file. Catalog server will read from catalog_log to init the status of books. Book class is used to store all book's detailed information. Catalog and order server will output executed operation to catalog_log and order_log under "output" folder. Initialization log has the following format:  

Format = **[Operation item_number stock cost Count topic title]**  

**Operation:** Indicate the execuated operation  
**item_number:** Indeicate the book's item number  
**stock:** Initial stock of the book  
**cost:** The cost of the book  
**topic:** The topic of the book  
**title:** Indicate the book title  

Here is one example of book initialization information that a catalog used to init book status:  
[init,1,3,10,distributed systems,How to get a good grade in 677 in 20 minutes a day]  


## Operation Request Format
**Lookup:**  
request: [SERVER_IP:8000/lookup/item_number], Ex. http://127.0.0.1/lookup?item_number=1  
response: {'item_number': item_number, 'stock':self.stock, 'cost': cost, 'type': type, 'title': title}, Ex. {'item_number': 1, 'stock':1000, 'cost': 50, 'type': distributed systems, 'title': How to get a good grade in 677 in 20 minutes a day.}  

**Search:**  
request: [SERVER_IP:8000/search/topic], Ex. http://127.0.0.1/search?topic=distributed systems  
response: {'result': book list}, Ex. {'result': [{'item_number': 1, 'title':How to get a good grade in 677 in 20 minutes a day},{'item_number': 2, 'title':RPCs for Dummies}]}  

**Buy:**  
request: [SERVER_IP:8000/buy/item_number], Ex. http://127.0.0.1/buy?item_number=1  
response: {'result': result}, Ex. {'result': Success}  

## Global IP/Port Address Configuration
To allow servers to communicate with each other, we need to give them other peer's addresses and port, we use a file - config to record the information.
Format = **[Type, IPAddress:Port]**  

**Type:** Type of the server
**IPAddress:Port:** The peer's ipv4 address and listening port  

Here is one example of configt file:  
frontend,127.0.0.1:8080  
catalog,127.0.0.1:8081  
order,127.0.0.1:8082  
 

## Concurency / Race Condition Protection
All books' information is stored in catalog server's memeory and shared by multiple threads concurrently. When a flask server receives a new client request, it will launch a new thread to process the message.  Therfore, when updating and read the book's information, we used a lock to make sure the whole operation is atomic in all server. For example, buy request from order server will check the book's stock, and if there is enough stock, the server will then decrease the stock by 1. Otherwise, the buy operation should reutrn "fail" rsult. Consider the following error case:  

client 1 queried the stock of book item_number 1 is 1  
client 2 queried the stock of book item_number 1 is 1  
client 1 update book stock to 0  
client 2 update book stock to 0  

To prevent the race condition mentioned above, we used a lock for buy operation:  

getLock()  
client 1 queried the stock of book item_number 1 is 1  
client 1 update book stock to 0  
releaseLock()  
getLock()  
client 2 queried the stock of book item_number 1 is 0  
client 2 buy failed  
releaseLock()  

## Server Output Log
We store the execuated operation with file name of catalog_log, order_log in catalog server & order server respectively:  
Format = **[Operation args]**  

**Operation:** Execuated operation name  
**args:** Argumnets of the execuated operation  

Here is one example of execuated operation stored by catalog server:  
[query_by_item,2]  
[update,2,na,-1]  

## Automatic Distributed Server Deployment
### 1.Pre-created AMI image  
We already create a Amazon Linux2 AMI image with Docker installed and made it public to access, later we can create new EC2 instances from the image, it provides us a machine that is able to build and run docker image

### 2.Dynamic creation of key pair
We will create a key pair in AWS account for latter access of EC2 instances  

### 3.Dynamic security group
We dynamically create security group and open HTTP port 8000-8002, 22 for servers

### 4.Dynamic server creation
We have pr-created Amazon AMI image that has Docker installed. We dynamically create a security group that allows HTTP REST API access permission. We create an EC2 instance from the pre-created AMI image and attached it with the created security group. We tag each EC2 instance with a tag MyBazaar32144321" so that we can later access them and release them.

### 5.Dynamic code mgration and docker image build-up
We migrate the latest code to the remote server using SCP and invoke script ec2_setup.sh to build the docker image, run the docker image, and start the corresponding server on that EC2 machine

### 6.Perform test 1 ~ test 4
We automatically build a docker image for client and run the client in a container. Then the client can launch multiple threads and perform multiple HTTP request to frontend server. That is, the client will run test1 ~ test4 in order and send requests to frontend server.

### 7.Gather test output(log) for validation
We use SCP to pull test output under the output folder from all remote servers. We store the output from each server to the local machine's output folder. The output is named with catalog_log and order_log, which respresent catalog server's log and order server's log respectively.

### 8.Release AWS resource
We terminate all EC2 instances, delete the security group, and key pairs created previously at the end of the test

# Validation & Test
## Test Cases
**test1 (Intermediate Milestone):** Perform search methods correctly.
**test2 (Intermediate Milestone):** Perform lookup methods correctly.
**test3 (Intermediate Milestone):** Buy operations run and update the stock of the item correctly
**test4 (Intermediate Milestone):** (Race Condition) 4 clients buy book "RPCs for Dummies" that only has 3 stock concurrently, only 3 client can buy the book 
**Test5 (Final Milestone):** Run test1~test4 again, but deploy peers on different AWS EC2 instances.  

## Automatic Test Scripts
**run_local_test.bat:** This script will automatically start frontend, catalog, and order server on local mahcine in a container. Then run a client in a container and perform test 1 ~ test 4 in order on a local machine. Finally, store output under the output folder for validation.  

**run_distributed_test.bat:**  This script will automatically create 3 Amazon EC2 instances, migrating code and config file to remote servers, building docker image, deploying corresponding server, on remote servers. Next, deploy a client on local machine and perform test 1 ~ test 4 in order on remote EC2 instances. Finally, store output under the output folder for validation and release all cloud resources. For more detail please see the chapter, "How it Works/Automatic Distributed Server Deployment".  

## Test Output (Log)  
We store all testing output under the output folder and use them to validate the correctness of each test case. There are three types of logs:  
catalog_log: store all execuated transaction on catalog server  
order_log: store all execuated transaction on order server  
client_log: store all execuated HTTP request and response log for all concurrent clients  

## Verification of All Test Cases  
### Test1 output:  
**Client Log:**  
Client0: Send request http://127.0.0.1:8000/search?topic=distributed+systems  
Client0: Get response {'result': [{'item_number': '1', 'title': 'How to get a good grade in 677 in 20 minutes a day'}, {'item_number': '2', 'title': 'RPCs for Dummies'}]}  
Client0: Send request http://127.0.0.1:8000/search?topic=graduate+school  
Client0: Get response {'result': [{'item_number': '3', 'title': 'Xen and the Art of Surviving Graduate School'}, {'item_number': '4', 'title': 'Cooking for the Impatient Graduate Student'}]}  

**Catalog Server Log:**    
query_by_topic,distributed systems  
query_by_topic,graduate school  
**Result:** Pass, client correctly find all books related to topic "distributed system" and "graduate school". The catalog server correctly stored the two search operation.    

### Test2 output:   
BuyerID:0 start to buy fish  
SellerID:1 start to sell boars  
**Result:** Pass, buyer 1 buy nothing, seller 1 sells nothing  


### Test3 output:  
BuyerID:0 start to buy boars  
BuyerID:1 start to buy salt  
**Result:** Pass, buyer 1 buy nothing, seller 1 sells nothing  


### Test4 output:   
SellerID:1 start to sell boars  
PeerID:5 with no role start to work  
BuyerID:2 start to buy boars  
BuyerID:0 start to buy boars  
BuyerID:3 start to buy boars  
PeerID:4 with no role start to work  
SellerID:1 replied buyerID:0  
SellerID:1 replied buyerID:2  
SellerID:1 replied buyerID:3  
SellerID:1 start to sell boars  
SellerID:1 start to sell fish  
BuyerID:2 bought boars from 1  
BuyerID:2 start to buy fish  
SellerID:1 replied buyerID:2  
SellerID:1 start to sell salt  
BuyerID:2 bought fish from 1  
BuyerID:2 start to buy fish  
**Result:** Pass, buyer 0,2,3 want to buy boars from seller 1, and seller 1 also replied all of them (race condition), only buyer 2 baught boars from seller 1 successfully  

**Test5 output: (Run on distributed servers, log is collect from different servers)**  
BuyerID:2 start to buy boars  
BuyerID:0 start to buy boars  
SellerID:1 start to sell boars  
PeerID:5 with no role start to work  
PeerID:4 with no role start to work  
BuyerID:3 start to buy boars  
SellerID:1 replied buyerID:0  
SellerID:1 replied buyerID:3  
SellerID:1 replied buyerID:2  
SellerID:1 start to sell boars  
BuyerID:3 bought boars from 1  
SellerID:1 start to sell fish  
BuyerID:3 start to buy boars   
SellerID:1 start to sell salt  
SellerID:1 replied buyerID:2  
SellerID:1 start to sell salt  
BuyerID:2 bought salt from 1  
BuyerID:2 start to buy fish  
**Result:** Pass, buyer 0,2,3 want to buy boars from seller 1, and seller 1 also replied all of them (race condition), only buyer 3 baught boars from seller 1 successfully  

# Evaluation and Measurements
## 1.	Compute the average response time per client search request by measuring the end-to-end response time seen by a client

Avg Response Time (1 Client) | Avg Response Time (3 Client) |  Avg Response Time (5 Client) |  Avg Response Time (9 Client)
------------ | ------------- | ------------- | -------------
79.524ms | 79.636ms | 86.7036ms  | 94.7036ms

PS: all response time sampled from 1000 requests
PS: We defines response time as the time the client receives responses from remote servers, the time doesn't imply the message is being processed since we use asynchronous RPC call design, the server will launch a new thread whenever it receives a request from a client, sending a message to background processing, and respond to client immediately.  

Results show averaged response times are almost the same (only a slight increase) as multiple clients are making requests to a peer. It matches what we expected since our system design will launch a new thread whenever receive a client request. The response time shouldn't be affected by the number of concurrent request since the server respond to clients as soon as it receives the request. However, we still see a little increase in average response time, I think it might be affected by the time used to launch a new thread. As more requests receive concurrently, the server spends some time launching a new thread, which causes a slight difference.  


## 2.	Break down the end-to-end response time into component-specific response times by computing the per-tier response time for query and buy requests
**Search Operation:**  (Flow: Client -> frontend -> catalog)  
Avg response time of **Frontend Server** to **Search** request (Seen by Client)  
Avg Response Time (1 Client) | Avg Response Time (3 Client) |  Avg Response Time (5 Client) |  Avg Response Time (9 Client)  
------------ | ------------- | ------------- | -------------
79.524ms | 79.636ms | 86.7036ms  | 94.7036ms  


Avg response time of **Catalog Server** to **Query by Topic** request (Seen by Frontend Server)  
Avg Response Time (1 Client) | Avg Response Time (3 Client) |  Avg Response Time (5 Client) |  Avg Response Time (9 Client)
------------ | ------------- | ------------- | -------------
4.6953ms | 4.6999ms | 4.8698ms  | 4.8789ms  


**Buy Operation:** (Flow: Client -> fronend -> order -> catalog)  
Avg response time of **Frontend Server** to **Buy request** (Seend By Client)  
Avg Response Time (1 Client) | Avg Response Time (3 Client) |  Avg Response Time (5 Client) |  Avg Response Time (9 Client)  
------------ | ------------- | ------------- | -------------
94.972ms | 94.424ms | 94.999ms  | 110.733ms  


Avg response time of **Order Server** to **Buy request** (Seend By Frontend Server)  
Avg Response Time (1 Client) | Avg Response Time (3 Client) |  Avg Response Time (5 Client) |  Avg Response Time (9 Client)  
------------ | ------------- | ------------- | -------------
15.8532ms | 15.636ms | 15.9036ms  | 16.0036ms  


Avg response time of **Catalog Server** to **Query by Item Number** request (Seend By Order Server)  
Avg Response Time (1 Client) | Avg Response Time (3 Client) |  Avg Response Time (5 Client) |  Avg Response Time (9 Client)  
------------ | ------------- | ------------- | -------------
5.6154ms | 5.636ms | 5.64ms  | 6.309ms  


Avg response time of **Catalog Server** to **Update** request** (Seend By Order Server)  
Avg Response Time (1 Client) | Avg Response Time (3 Client) |  Avg Response Time (5 Client) |  Avg Response Time (9 Client)  
------------ | ------------- | ------------- | ------------
4.623ms | 4.782ms | 4.9531ms  | 5.321ms  


**Lookup operation:**  (Flow: Client -> fronend -> catalog)  
Avg response time of **Frontend Server** to **Lookup** request (Seen by Client)  
Avg Response Time (1 Client) | Avg Response Time (3 Client) |  Avg Response Time (5 Client) |  Avg Response Time (9 Client)
------------ | ------------- | ------------- | -------------
76.293ms | 78.131ms | 86.386ms  | 92.9996ms  


Avg response time of **Catalog Server** to **Query by Item Number** request (Seen by Frontend Server)  
Avg Response Time (1 Client) | Avg Response Time (3 Client) |  Avg Response Time (5 Client) |  Avg Response Time (9 Client)
------------ | ------------- | ------------- | -------------
4.456ms | 4.3929ms | 4.4558ms  | 4.5089ms  


PS: all response time sampled from 1000 requests
PS: We defines response time as the time the client receives responses from remote servers, the time doesn't imply the message is being processed since we use asynchronous RPC call design, the server will launch a new thread whenever it receives a request from a client, sending a message to background processing, and respond to client immediately.  

Results show averaged response times are almost the same (only a slight increase) as multiple clients are making requests to a peer. It matches what we expected since our system design will launch a new thread whenever receive a client request. The response time shouldn't be affected by the number of concurrent request since the server respond to clients as soon as it receives the request. However, we still see a little increase in average response time, I think it might be affected by the time used to launch a new thread. As more requests receive concurrently, the server spends some time launching a new thread, which causes a slight difference.  


# Design Tradeoffs
**RPC/RMI Call V.S Socket**  
We must choose one of the ways for communication among peers. The pros of RPC/RMI is:    
1. Allow user to define communicate interface, more human-readable and concise  
2. Don't need to worry about low-level networking communication implementation  
3. Remove the complexity of low-level networking communication implementation  

The cons of RPC/RMI:  
1. Reduced flexibility on low-level networking implementation and communication interface  

We finally choose to use RPC as our peer communication since we want to hide the complexity of lowe-lever networking communication, making the system more simple, concise, and easy to debug. Also, this assignment doesn't require us to implement a difficult connection fault tolerance or mechanism, we don't need a socket for flexibility.  

**Synchronous RPC Call V.S Asyncrounous RPC Call**  
The pros of using Synchronous RPC is:
1. Don't need to worry about concurrency issues caused by multi-thread  
2. Lower complexity of system design. 
The cons of Synchronous RPC is:  
1. Impaired performance (throughput) if multiple requests happen concurrently.  
2. Higher latency 

We finally chose Asyncrounous RPC Call since we want better performance(throughput) and shorter response time of message processing. We used a lock and shared data to overcome the concurrent issue caused by multi-thread.  

**Thread Pool V.S Dynamically Creating New Thread**  
To handle client RPC requests, we can choose either to launch a new thread every time or use the existing thread pool to allocate thread to message processing task. The pros of Thread Pool is:  
1.Shorter response time of client request since we don't need to create new thread dynamically  
The cons are:  
1. Higher complexity of system since we need to handle the creation and recycle of threads  
2. Higher memory usage since we must maintain a certain amount of thread  
3. Hard to debug  

We finally choose Dynamically Creating New Thread since the message handler thread doesn't have too many data attributes and creating is fast. Given that performance doesn't have too much difference and we want to simplify our design, we can dynamically creating a new thread to handle RPC client requests.

**Dynamic Creation of EC2 Instances V.S Hot Stand-By EC2 Instances**  
When launching multiple servers for peer deployment, we must choose between whether to dynamically creating new instances or deploy peers on hot standby servers. The pros of dynamic creation of EC2 Instances are:  
1. Lower cost of AWS EC2 instance (EC2 bills by running time of instances)  
The cons of a hot stand-by EC2 instance is:  
1. Longer deployment time since we need to wait for instances to be created  
2. Need to re-migrate and compile code every time we update our code  

We finally chose Dynamic Creation of EC2 Instances since the cost is significant if we maintain a lot of running EC2 instances. We write a script to quickly creating a security group and instances when deploying.  


**Open All TCP Port between Different Remote Server V.S Open only certain range of TCP Port between Different Remote Server**  
To allow RPC access permission between different servers so that peers can communicate with each other. We attached the Amazon security group to each Amazon EC2 instance to implement this permission control. The pros of opening all TCP Port between Different Remote Serve is:  
1. Don't need to worry about port range change (Ex. Add/Deletion) as we may want to add a new port to a peer  
2. Easy to configure  
The cons are:  
1.  Impaired security since if one of the servers is malicious, it can exploit and attack the opened port  

We finally chose to open only a certain range of TCP ports between Different Remote Server. We use a script to automatically create a security group to save the effort of changing the port in the future.


# How to Run It

See [README.md #How to run?](https://github.com/Chih-Che-Fang/MyBookStore/blob/main/README.md "How to run")

# Possible Improvements and Extensions

1. We didn't implement the fault tolerance. However, since catalog & order server stored all execuated log and initialization informtion, we can, in the future, implement a mechanisim reasily to recover books' status after a machine recovered from a fail
2. We are using the thread per request model currently. Therefore, we could be optimized by using thread pool to improve response latency.
