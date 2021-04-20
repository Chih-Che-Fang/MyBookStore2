
# MyBookStore
# Group Members: 
# Name: Chih-Che Fang, SPIRE ID: 32144321, Email: chihchefang@umass.edu;

**Enviornment:**  Windows + Docker  + AWS Cli2.0 installed + AWS cli configured with your own AWS account **(Please make sure you're able to access your AWS account by AWS CLI)**  
**Test Cases:**   
**[Intermediate Milestone]**  
- **test1:** (Verify Search transaction + Cache) Perform search requests for each topic twice, verify we get the same and correct result  
- **test2:** (Verify Lookup transaction + Cache) Perform lookup methods for each book twice, verify we get the same and correct result  
- **test3:** (Verify Buy transaction + Replication/Cache Consistency + Loadbalance) Process Buy request and update the book stock correctly with Frontend server direct requests to servers evenly. Also check the cache consistency after several buy transaction  
- **test4:** (Verify Replication/Cache Consistency + Race Condition Protection) 4 concurrent clients buy book "RPCs for Dummies" that only has 3 stock concurrently, only 3 client can buy the book  

**[Final Milestone]**  
- **test5:** (Verify Fault tolerance) After primary catalog server crashed, Frontend server can still correctly process update and query requests. Check alive replica will take over the primary job correctly.  
- **test6:** (Verify Fault tolerance) Primary catalog server can correctly recover from a fail and resync with replicas  
- **test7:** (Verify Fault tolerance) Same with test5, but the crashed server is a replicated catalog server  
- **test8:** (Verify Fault tolerance) Same with test 6, but the recovered server is a replicated catalog server   
- **test9:** (Verify Distributed System) Run all of above test cases, but deploy servers on 5 remote EC2 machines, with each of the components and replicas on different machines
  

# How to run?  

1. Switch to the root directory of this project (Ex. cd /MyBookStore) and confirm the path contains no "blank"  

2. **[Test on Single Local Server]** Perform **run_local_test.bat** on Windows OS (With Docker installed), and will automatically build docker image, run docker image and deploy client and all type of servers in a container. Client then will perform all test cases defined above to frontend server automatically.  
**[Test on Multiple Remote Servers(EC2)]** Perform **run_distributed_test.bat** on Windows OS (With Docker installed, AWS Cli set and configured, must have access to your own AWS account), and will automatically careat security group, key pair, and 5 EC2 instances, then migrate the code/config to remote server, build docker image, and run one of the 4 type bookstore server (frontend/cache/catalog/order) on remote machines. Finally, the script will deploy the client in local machine's container and  will perform all test cases on remote servers.  
3. See the testing result on console that runs the client container, it shows you client requets performed and the server's response, you'll see the logs like:  
Client1: Send request http://127.0.0.1:8000/buy?item_number=2  
Client2: Send request http://127.0.0.1:8000/buy?item_number=2  
Client3: Send request http://127.0.0.1:8000/buy?item_number=2  
Client4: Send request http://127.0.0.1:8000/buy?item_number=2  
Client1: Get response  {'result': 'Success'}  
Client2: Get response  {'result': 'Success'}  
Client3: Get response  {'result': 'Success'}  
Client4: Get response  {'result': 'Failed'}  


Fianlly, the distributed servers will output all server logs to "output" folder  

4.To verify the server operation's correctness and executed HTTP request, check the log file **cache_log**, **"catalog0_log/catalog1_log"** , and **"order0_log/order1_log"** under **"output"** folder. To verify client's HTTP requests & response log for each test cases, check the log file **client_log**   


# Directory/Files Description
-	Src: Project source code
-	function_batch: store batch functions
-	Run_local_test.bat: local testing script on single machines
-	Run_distributed_test.bat: testing script on multuple remote machines
-	docker_scripts: docker entry point script for each type of server (frontend/catalog/order)
-	output: output log of all test cases for catalog/order server
-	run.sh: docker image entrypoint script
-	docs: Design documents
-	Read.md: Readme file
-	config: Gloabal server IP/Port address reference
-	init_bookstore: used for initialization of bookstore  
-	run_performance_test.bat: Used only for performance test  
-	dockerfile: docker file for all servers (frontend/catalog/order)
-	requirements.txt: Docker image dependencies
-	ec2_setup.sh: sub-scripts for distributed testing, used to set up remote machines (Ex.build docker, run docker, ..)
-	debug.bat: for debug use
