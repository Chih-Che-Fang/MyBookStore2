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
**Logger:** A class used to output log to files  

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
**test3 (Intermediate Milestone):** Run Buy operations and update the stock of the item correctly
**test4 (Intermediate Milestone):** (Race Condition) 4 clients buy book "RPCs for Dummies" that only has 3 stock concurrently, only 3 client can buy the book 
**Test5 (Final Milestone):** Run test1~test4 again, but deploy servers on different AWS EC2 instances.  

## Automatic Test Scripts
**run_local_test.bat:** This script will automatically start frontend, catalog, and order server on local mahcine in a container. Then run a client in a container and perform test 1 ~ test 4 in order on a local machine. Finally, store output under the output folder for validation.  

**run_distributed_test.bat:**  This script will automatically create 3 Amazon EC2 instances, migrating code and config file to remote servers, building docker image, deploying corresponding server, on remote servers. Next, deploy a client on local machine and perform test 1 ~ test 4 in order on remote EC2 instances. Finally, store output under the output folder for validation and release all cloud resources. For more detail please see the chapter, "How it Works/Automatic Distributed Server Deployment".  

## Test Output (Log)  
We store all testing output under the output folder and use them to validate the correctness of each test case. There are three types of logs:  
catalog_log: store all execuated transaction on catalog server  
order_log: store all execuated transaction on order server  
client_log: store all execuated HTTP request and response log for all concurrent clients  

## Verification of All Test Cases  
### Test1 output: Perform search methods correctly  
**Client Log:**  
Client0: Send request http://127.0.0.1:8000/search?topic=distributed+systems  
Client0: Get response {'result': [{'item_number': '1', 'title': 'How to get a good grade in 677 in 20 minutes a day'}, {'item_number': '2', 'title': 'RPCs for Dummies'}]}  
Client0: Send request http://127.0.0.1:8000/search?topic=graduate+school  
Client0: Get response {'result': [{'item_number': '3', 'title': 'Xen and the Art of Surviving Graduate School'}, {'item_number': '4', 'title': 'Cooking for the Impatient Graduate Student'}]}  

**Catalog Server Log:**    
query_by_topic,distributed systems  
query_by_topic,graduate school  

**Result:** Pass, client correctly find all books related to topic "distributed system" and "graduate school". The catalog server correctly stored the two search operation.    

### Test2 output: Perform lookup methods correctly
**Client Log:**  
Client0: Send request http://127.0.0.1:8000/lookup?item_number=1  
Client0: Get response {'result': {'cost': '10', 'item_number': '1', 'stock': 1000, 'title': 'How to get a good grade in 677 in 20 minutes a day', 'type': 'distributed systems'}}  
Client0: Send request http://127.0.0.1:8000/lookup?item_number=2  
Client0: Get response {'result': {'cost': '20', 'item_number': '2', 'stock': 1000, 'title': 'RPCs for Dummies', 'type': 'distributed systems'}}  
Client0: Send request http://127.0.0.1:8000/lookup?item_number=3  
Client0: Get response {'result': {'cost': '5', 'item_number': '3', 'stock': 1000, 'title': 'Xen and the Art of Surviving Graduate School', 'type': 'graduate school'}}  
Client0: Send request http://127.0.0.1:8000/lookup?item_number=4  
Client0: Get response {'result': {'cost': '15', 'item_number': '4', 'stock': 1000, 'title': 'Cooking for the Impatient Graduate Student', 'type': 'graduate school'}}  

**Catalog Server Log:** 
query_by_item,1  
query_by_item,2  
query_by_item,3  
query_by_item,4  

**Result:** Pass, client correctly get detailed information of book item_number 1 ~ 4. The catalog server correctly stored the 4 lookup operation.  

### Test3 output: Run Buy operations and update the stock of the item correctly
**Client Log:**  
Client0: Send request http://127.0.0.1:8000/buy?item_number=1  
Client0: Get response {'result': 'Success'}  
Client0: Send request http://127.0.0.1:8000/buy?item_number=1  
Client0: Get response {'result': 'Success'}  
Client0: Send request http://127.0.0.1:8000/buy?item_number=1  
Client0: Get response {'result': 'Success'}  
Client0: Send request http://127.0.0.1:8000/buy?item_number=1  
Client0: Get response {'result': 'Failed'} 

**Catalog Server Log:**  
query_by_item,1  
update,1,na,-1  
query_by_item,1  
update,1,na,-1  
query_by_item,1  
update,1,na,-1  

**Order Server Log:**  
bought book 1  
bought book 1  
bought book 1  
 

**Result:** Pass, book item_number 1 only has 3 stock. First of 3 client's buy request should success and the last one should fail. The order server correctly stored only the three succeded buy operation. The catalog server correctly log the 3 executed query and 3 update request.


### Test4 output: (Race Condition) 4 clients buy book "RPCs for Dummies" that only has 3 stock concurrently, only 3 client can buy the book 
**Client Log:**  
Client1: Send request http://127.0.0.1:8000/buy?item_number=2  
Client2: Send request http://127.0.0.1:8000/buy?item_number=2  
Client3: Send request http://127.0.0.1:8000/buy?item_number=2  
Client4: Send request http://127.0.0.1:8000/buy?item_number=2  
Client1: Get response {'result': 'Success'}  
Client2: Get response {'result': 'Success'}  
Client3: Get response {'result': 'Success'}  
Client4: Get response {'result': 'Failed'}  

**Catalog Server Log:**  
query_by_item,2
update,2,na,-1
query_by_item,2
query_by_item,2
query_by_item,2
update,2,na,-1
update,2,na,-1

**Order Server Log:**  
bought book 2  
bought book 2    
bought book 2    
 

**Result:** Pass, book item_number 2 only has 3 stock. First of 3 concurrent client's buy request should return success and the last one should return fail. The order server correctly stored only the 3 succeded buy operation. The catalog server correctly log the 4 executed query and 3 update request.  

### Test5 output: Run test1~test4 again, but deploy servers on different AWS EC2 instances.  
**Result:** Pass, All test1 ~ test 4 log is the same as run in local machine

# Evaluation and Measurements
## 1.	Compute the average response time per client search request by measuring the end-to-end response time seen by a client

Avg Response Time (1 Client) | Avg Response Time (3 Client) |  Avg Response Time (5 Client) |  Avg Response Time (9 Client)
------------ | ------------- | ------------- | -------------
79.524ms | 79.636ms | 86.7036ms  | 94.7036ms

PS: all response time sampled from 1000 requests  

Results show averaged response times increases as concurrent client increases. Even though all servers adopted multi-thread to handle with client requests, server still need time to process request and launch a new thread. Too much request during a short time still makes the frontend and catalog server become a bottleneck and therefore the averaged time increases.

## 2.	Break down the end-to-end response time into component-specific response times by computing the per-tier response time for query and buy requests
**Breakdown of Search Operation:**  (Flow: Client -> frontend -> catalog)  
Avg response time of **Frontend Server** to **Search** request (Seen by Client)  
Avg Response Time (1 Client) | Avg Response Time (3 Client) |  Avg Response Time (5 Client) |  Avg Response Time (9 Client)  
------------ | ------------- | ------------- | -------------
79.524ms | 79.636ms | 86.7036ms  | 94.7036ms  


Avg response time of **Catalog Server** to **Query by Topic** request (Seen by Frontend Server)  
Avg Response Time (1 Client) | Avg Response Time (3 Client) |  Avg Response Time (5 Client) |  Avg Response Time (9 Client)
------------ | ------------- | ------------- | -------------
4.6953ms | 4.6999ms | 4.8698ms  | 4.8789ms  

<br />
<br />
<br />

**Breakdown of Buy Operation:** (Flow: Client -> fronend -> order -> catalog)  
Avg response time of **Frontend Server** to **Buy request** (Seend By Client)  
Avg Response Time (1 Client) | Avg Response Time (3 Client) |  Avg Response Time (5 Client) |  Avg Response Time (9 Client)  
------------ | ------------- | ------------- | -------------
94.972ms | 94.424ms | 94.999ms  | 110.733ms  


Avg response time of **Order Server** to **Buy request** (Seen By Frontend Server)  
Avg Response Time (1 Client) | Avg Response Time (3 Client) |  Avg Response Time (5 Client) |  Avg Response Time (9 Client)  
------------ | ------------- | ------------- | -------------
15.8532ms | 15.636ms | 15.9036ms  | 16.0036ms  


Avg response time of **Catalog Server** to **Query by Item Number** request (Seen By Order Server)  
Avg Response Time (1 Client) | Avg Response Time (3 Client) |  Avg Response Time (5 Client) |  Avg Response Time (9 Client)  
------------ | ------------- | ------------- | -------------
5.6154ms | 5.636ms | 5.64ms  | 6.309ms  


Avg response time of **Catalog Server** to **Update** request** (Seen By Order Server)  
Avg Response Time (1 Client) | Avg Response Time (3 Client) |  Avg Response Time (5 Client) |  Avg Response Time (9 Client)  
------------ | ------------- | ------------- | ------------
4.623ms | 4.782ms | 4.9531ms  | 5.321ms  

<br />
<br />
<br />

**Breakdown of Lookup operation:**  (Flow: Client -> fronend -> catalog)  
Avg response time of **Frontend Server** to **Lookup** request (Seen by Client)  
Avg Response Time (1 Client) | Avg Response Time (3 Client) |  Avg Response Time (5 Client) |  Avg Response Time (9 Client)
------------ | ------------- | ------------- | -------------
76.293ms | 78.131ms | 86.386ms  | 92.9996ms  


Avg response time of **Catalog Server** to **Query by Item Number** request (Seen by Frontend Server)  
Avg Response Time (1 Client) | Avg Response Time (3 Client) |  Avg Response Time (5 Client) |  Avg Response Time (9 Client)
------------ | ------------- | ------------- | -------------
4.456ms | 4.3929ms | 4.4558ms  | 4.5089ms  

PS: all response time sampled from 1000 requests

<br />
<br />
<br />

Results show averaged response times are almost the same (only a slight increase) as multiple clients are making requests to a peer. It matches what we expected since our system design will launch a new thread whenever receive a client request. The response time shouldn't be affected by the number of concurrent request since the server respond to clients as soon as it receives the request. However, we still see a little increase in average response time, I think it might be affected by the time used to launch a new thread. As more requests receive concurrently, the server spends some time launching a new thread, which causes a slight difference.  


# Design Tradeoffs
**Flask  V.S Django/Struts**  
We must choose one of web server framework to implement the servers, the pros of Django/Struts framework are:  
1. It is a versatile framework and can be used for any website (social network, news site, content management, and more) with content in any format like HTML, XML, JSON, and more. It works in tandem with any client-side framework.  
2. It is a secure framework and automatically manages standard security features like user account management, transaction management, cross-site request forgery, clickjacking, and more.  
3. It is scalable and maintainable. Django follows design patterns and principles to reuse and maintain the code.  

The cons of Django/Struts are:  
1. Configuration is complicated than Flask  
2. Lack of built-in development server and harder to debug  

We finally choose to use Flask as our server implementation as it is easier to configure and have several built-in server template. It support multi-thread without any effort. As this project is small, we don't suffer from scability and security problem.   

**Synchronous HTTP Request V.S Asyncrounous HTTP Request**  
The pros of using Synchronous HTTP Request is:  
1. Client side don't need to worry about the implementation of callback (from server) function  
2. Client-side has lower complexity of system design. 

The cons of Synchronous HTTP Request is:  
1. Inefficiency of resource usage (Client can do nothing when waiting for response)  
2. Higher response time  

We finally chose Synchronous HTTP Request since it makes the whole design in client-side simplier and consie. Alos, it makes debugging work easier. We use multiple threads to make HTTP request concurrently, overcoming the disavatage of inefficient resource use.  

**Thread Pool V.S Dynamically Creating New Thread**  
To handle client HTTP requests, we can choose either to launch a new thread every time or use the existing thread pool to allocate thread to message processing task. The pros of Thread Pool is:  
1.Shorter response time of client request since we don't need to create new thread dynamically  

The cons are:  
1. Higher complexity of system since we need to handle the creation and recycle of threads  
2. Higher memory usage since we must maintain a certain amount of thread  
3. Hard to debug  

We finally choose Dynamically Creating New Thread since the HTTP thread doesn't have too many data attributes and creating is fast. Given that performance doesn't have too much difference and we want to simplify our design, we can dynamically creating a new thread to handle HTTP client requests.

**Dynamic Creation of EC2 Instances V.S Hot Stand-By EC2 Instances**  
When launching multiple servers for server deployment, we must choose between whether to dynamically creating new instances or deploy peers on hot standby servers. The pros of dynamic creation of EC2 Instances are:  
1. Lower cost of AWS EC2 instance (EC2s are billed by running time of instances)  

The cons of a hot stand-by EC2 instance is:  
1. Longer deployment time since we need to wait for instances to be created  
2. Need to re-migrate and compile code every time we update our code  

We finally chose Dynamic Creation of EC2 Instances since the cost is significant if we maintain a lot of running EC2 instances. We write a script to quickly creating a security group and instances when deploying.  


**Open All TCP Port between Different Remote Server V.S Open only certain range of TCP Port between Different Remote Server**  
To allow HTTP access permission between different servers so that servers can communicate with each other. We attached the Amazon security group to each Amazon EC2 instance to implement this permission control. The pros of opening all TCP Port between Different Remote Serve is:  
1. Don't need to worry about port range change (Ex. Add/Deletion new port dynamically) as we may want to add a new port to a peer  
2. Easy to configure  

The cons are:  
1.  Impaired security since if one of the servers is malicious, it can exploit and attack the opened port  

We finally chose to open only a certain range of TCP ports between Different Remote Server. We use a script to automatically create a security group to save the effort of changing the port in the future.


# How to Run It

See [README.md #How to run?](https://github.com/Chih-Che-Fang/MyBookStore/blob/main/README.md "How to run")

# Possible Improvements and Extensions

1. We didn't implement the fault tolerance. However, since catalog & order server stored all execuated log and initialization informtion, we can, in the future, implement a mechanisim reasily to recover books' status after a machine recovered from a fail  
2. Currently we only have 1 machine for each type of server, but as client increases, the server has slower response time. Therefore, in the fututre, we can add more replicated server for each type of server and add a load balancer to handle concurrently client reuqests. In this way, we can reduce averaged response time and scale this bookstore to a large number of customers.
3. We are using the thread per request model currently. Therefore, we could optimize averaged response latency time by using thread pool since each request doesn't need to wait for the launch time of a thread  
