REM Create key pair, security group
aws ec2 delete-key-pair --key-name 677kp32144321
aws ec2 create-key-pair --key-name 677kp32144321 --query "KeyMaterial" --output text > 677kp32144321.pem
aws ec2 delete-security-group --group-name MyBookStore32144321
aws ec2 create-security-group --group-name MyBookStore32144321 --description "SG for 677 lab2"

REM Set up security group permission to allow HTTP rquest among ec2 servers
aws ec2 authorize-security-group-ingress --group-name MyBookStore32144321 --protocol tcp --port 8000-8002 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-name MyBookStore32144321 --protocol tcp --port 22 --cidr 0.0.0.0/0

REM Create EC2 instances
aws ec2 run-instances --image-id ami-054d94c846d1abc06 --instance-type t2.micro --key-name 677kp32144321 --security-groups MyBookStore32144321 --tag-specifications "ResourceType=instance,Tags=[{Key=MyBookStore32144321,Value=m1}]" > instance.json
aws ec2 run-instances --image-id ami-054d94c846d1abc06 --instance-type t2.micro --key-name 677kp32144321 --security-groups MyBookStore32144321 --tag-specifications "ResourceType=instance,Tags=[{Key=MyBookStore32144321,Value=m2}]" > instance.json
aws ec2 run-instances --image-id ami-054d94c846d1abc06 --instance-type t2.micro --key-name 677kp32144321 --security-groups MyBookStore32144321 --tag-specifications "ResourceType=instance,Tags=[{Key=MyBookStore32144321,Value=m3}]" > instance.json

REM Wait for EC2 to be ready
timeout 45

REM Access EC2 public ip address and instane ids
aws ec2 describe-instances  --filter "Name=tag-key,Values=MyBookStore32144321" "Name=instance-state-name,Values=running" --query "Reservations[*].Instances[*].InstanceId" --output text> ids.txt
aws ec2 describe-instances  --filter "Name=tag-key,Values=MyBookStore32144321" "Name=instance-state-name,Values=running" --query "Reservations[*].Instances[*].PublicIpAddress" --output text> ips.txt

REM Generate inital config file
@echo off 
setlocal enabledelayedexpansion
del config
set servers[0]=frontend
set servers[1]=catalog
set servers[2]=order
set server_scripts[0]=run_frontend.sh
set server_scripts[1]=run_catalog.sh
set server_scripts[2]=run_order.sh 
set /a count = 0
set /a port = 8000

REM output server ip address to config
for /f "tokens=*" %%a in (ips.txt) do (
  (call echo %%servers[!count!]%%)>>tmp
  set /p server=<tmp
  del tmp
  
  echo !server!,%%a:!port!>> config
  if !count! == 0 (set frontend_addr=%%a:!port!)
  set /a count += 1
  set /a port += 1
)

REM Migrate latest code, build docker image, and run the docker image
set /a count = 0
for /f "tokens=*" %%a in (ips.txt) do (
	REM Migrate code 
	ssh -o "StrictHostKeyChecking no" -i 677kp32144321.pem ec2-user@%%a "rm -rf MyBookStore"
	scp -o "StrictHostKeyChecking no" -i 677kp32144321.pem -r %cd%  ec2-user@%%a:~/MyBookStore
	
	REM Update the docker script according the type of server (frontend/catalog/order)
	(call echo %%server_scripts[!count!]%%)>>tmp
	set /p server_script=<tmp
	del tmp
	
	scp -o "StrictHostKeyChecking no" -i 677kp32144321.pem .\docker_scripts\!server_script!  ec2-user@%%a:~/MyBookStore/run.sh
	
	REM Invoke ec2_setup script to build docker image, set up initalization log, and run the docker image for each type of server(frontend/order/catalog)
	start cmd /k ssh -o "StrictHostKeyChecking no" -i 677kp32144321.pem ec2-user@%%a "cd ~/MyBookStore;sh ec2_setup.sh"
	set /a count += 1
)

REM Wait for docker image to be ready
timeout 35

REM Send a seriers of Client Requests for validation
@ECHO ON
curl -L http://!frontend_addr!/lookup?item_number=1
curl -L http://!frontend_addr!/lookup?item_number=2
curl -L http://!frontend_addr!/lookup?item_number=3
curl -L http://!frontend_addr!/lookup?item_number=4
curl -L http://!frontend_addr!/search?topic=distributed+systems"
curl -L http://!frontend_addr!/search?topic=graduate+school

curl -L http://!frontend_addr!/buy?item_number=1
curl -L http://!frontend_addr!/buy?item_number=1
curl -L http://!frontend_addr!/buy?item_number=1
curl -L http://!frontend_addr!/buy?item_number=1


REM release AWS resources
aws ec2 delete-security-group --group-name MyBookStore32144321
for /f "tokens=*" %%a in (ids.txt) do (
  aws ec2 terminate-instances --instance-ids %%a
)
aws ec2 delete-key-pair --key-name 677kp32144321

REM Delete temporary files
del 677kp32144321.pem
del instance.json
del ids.txt
del ips.txt
pause