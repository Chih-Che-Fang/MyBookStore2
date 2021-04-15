
# MyBookStore
# Group Members: 
# Name: Chih-Che Fang, SPIRE ID: 32144321, Email: chihchefang@umass.edu;

**Enviornment:**  Windows + Docker  + AWS Cli2.0 installed + AWS cli configured with your own AWS account **(Please make sure you're able to access your AWS account by AWS CLI)**  
**Test Cases:**   
**[Intermediate Milestone]**  
test1: (Cache) Perform search methods with cache correctly.  
test2: (Cache) Perform lookup methods with cache correctly. 
test3: (Loadbalance) frontend server direct requests to servers evenly  
test3: (Replication and Consistency) Run Buy operations and update the stock of the item correctly  
test4: (Replication and Consistency + Race Condition) 4 clients buy book "RPCs for Dummies" that only has 3 stock concurrently, only 3 client can buy the book  
test5: (Replication and Consistency) All catalog replicas have the same state after serveral stock updates  
**[Final Milestone]**  
test6: (Loadblance + Fault tolerance) Frontend server correctly receive heart beat from order/catalog serverand tolerate 1 replica fail  
test7: (Fault tolerance) Frontend server reissue failed HTTP request correctly  
test8: (Fault tolerance) Catalog server can correctly recover from a fail and resync with replicas  
test9: (Replication + Fault tolerance) replica can identify peer failing and elect new primary server, tolerating 1 replica fail  
test10: Run above test cases, but deploy servers on 5 remote EC2 machines, with each of the components and replicas on different machines  

# How to run?  

1. Switch to the root directory of this project (Ex. cd /MyBookStore) and confirm the path contains no "blank"  

2. **[Test on Single Local Server]** Perform **run_local_test.bat** on Windows OS (With Docker installed), and will automatically build docker image, run docker image and deploy client and all servers in a container. Client then will perform test1 - test10 to frontend server automatically.  
**[Test on Multiple Remote Servers(EC2)]** Perform **run_distributed_test.bat** on Windows OS (With Docker installed, AWS Cli set and configured, must have access to your own AWS account), and will automatically careat security group, key pair, and 5 EC2 instances, then migrate the code/config to remote server, build docker image, and run one of the 3 type bookstore server (frontend/catalog/order) on remote machines. Finally, the script will deploy the client in local machine's container and  will perform test1 - test10 on remote servers.  
3. See the testing result on console that runs the client container, it will tell you what client requet each server received, and the server's response, you should be able to see the logs like:  
Client1: Send request http://127.0.0.1:8000/buy?item_number=2  
Client2: Send request http://127.0.0.1:8000/buy?item_number=2  
Client3: Send request http://127.0.0.1:8000/buy?item_number=2  
Client4: Send request http://127.0.0.1:8000/buy?item_number=2  
Client1: Get response  {'result': 'Success'}  
Client2: Get response  {'result': 'Success'}  
Client3: Get response  {'result': 'Success'}  
Client4: Get response  {'result': 'Failed'}  


Fianlly, the distributed servers will output all server logs to "output" folder  

4.To verify the server operation's correctness and executed HTTP request, check the log file **cache_log**, **"catalog0_log/catalog1_log"** , and **"order0_log/order1_log"** under "output" folder. To verify client's HTTP requests & response log, check the log file **client_log**   


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
-	init_bookstore: initialization bookstore infromation
-	run_performance_test.bat: Used only for performance test
-	dockerfile: docker file for all servers (frontend/catalog/order)
-	requirements.txt: Docker image dependencies
-	ec2_setup.sh: sub-scripts for distributed testing, used to set up remote machines (Ex.build docker, run docker, ..)
-	debug.bat: for debug use
