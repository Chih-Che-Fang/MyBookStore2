
# MyBazaar
# Group Members: 
# Name: Chih-Che Fang, SPIRE ID: 32144321, Email: chihchefang@umass.edu;

**Enviornment:**  Windows + Python3.7 + Docker  + AWS Cli2.0 installed + AWS cli configured with your own AWS account **(Please make sure you're able to access your AWS account by AWS CLI)**  
**Applications:**   
**[Intermediate Milestone]**  
Perform lookup and search methods correctly.
Buy operations run and update the stock of the item correctly

# How to run?  

1. Switch to the root directory of this project (Ex. cd /MyBazaar) and confirm the path contains no "blank"  

2. **[Test on Single Local Server]** Perform **run_local_test.bat** on Windows OS (With JDK installed and with JDK environment variable set), and will automatically launch multiple peers and construct the topology, finally run the peer-to-peer system  
**[Test on Multiple Remote Servers(EC2)]** Perform **run_distributed_test.bat** on Windows OS (With JDK installed, JDK environment variable set, AWS Cli set and configured, must have access to your own AWS account), and will automatically careat security group, key pair, and multiple EC2 instances, then migrate the code to remote server and complie it, finally run the peer-to-peer system for test1 to test4

3. See the testing result on console, it will tell you if the buyer bought the products or not. For every test case, it will jump out multiple console windows, they represent a buyer peer, seller peer, or a peer with no role. They will individually print logs like:  

Output info to loc:info-id-0  
ServerId:0 start!!  
Reply 0 1 0 0  
ServerID:0 receive msg:Reply 0 1 0 0 with path:0  
Output info to loc:info-id-0  
BuyerID:0 bought fish from 1  
BuyerID:0 start to buy boars  
Output info to loc:info-id-0  

Fianlly, the distributed system will output all testing log to "output" folder

4.To verify the correctness, check the log output of test1.out ~ test4.out under "output" folder  


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
