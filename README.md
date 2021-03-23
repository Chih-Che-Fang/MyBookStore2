
# MyBookStore
# Group Members: 
# Name: Chih-Che Fang, SPIRE ID: 32144321, Email: chihchefang@umass.edu;

**Enviornment:**  Windows + Docker  + AWS Cli2.0 installed + AWS cli configured with your own AWS account **(Please make sure you're able to access your AWS account by AWS CLI)**  
**Applications:**   
**[Intermediate Milestone]**  
test1: Perform lookup and search methods correctly.  
test2: Buy operations run and update the stock of the item correctly  
test3: (Race Condition) 4 clients buy book "RPCs for Dummies" that only has 3 stock concurrently, only 3 client can buy the book  
**[Final Milestone]**  
test4: Run above test cases, but deploy system on three machines, with each of the three components on a different machine  

# How to run?  

1. Switch to the root directory of this project (Ex. cd /MyBookStore) and confirm the path contains no "blank"  

2. **[Test on Single Local Server]** Perform **run_local_test.bat** on Windows OS (With Docker installed), and will automatically launch multiple peers and construct the topology, finally run the peer-to-peer system  
**[Test on Multiple Remote Servers(EC2)]** Perform **run_distributed_test.bat** on Windows OS (With Docker installed, AWS Cli set and configured, must have access to your own AWS account), and will automatically careat security group, key pair, and multiple EC2 instances, then migrate the code to remote server, build docker image, finally run one of the 3 type bookstore server (frontend/catalog/order)  

3. See the testing result on console, it will tell you what client requet each server received, and the server's response, you should be able to see the logs like:



Fianlly, the distributed servers will output all testing log to "output" folder

4.To verify the correctness, check the log file **"catalog_log"** & **"order_log"** under "output" folder  


# Directory/Files Description
-	Src: Project source code
-	Run_local_test.bat: local testing script on single machines
-	Run_distributed_test.bat: testing script on multuple remote machines
-	docker_scripts: docker entry point script for each type of server (frontend/catalog/order)
-	output: output log of all test cases for catalog/order server
-	run.sh: docker image entrypoint script
-	docs: Design documents
-	Read.md: Readme file
-	test: Initial peer state for all tetest cases 
-	config: Gloabal server IP/Port address reference
-	run_performance_test.bat: Used only for performance test
-	dockerfile: docker file for all servers (frontend/catalog/order)
-	requirements.txt: Docker image dependencies
-	ec2_setup.sh: sub-scripts for distributed testing, used to set up remote machines (Ex.build docker, run docker, ..)
