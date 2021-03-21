REM del config
REM 
REM REM Create key pair, security group
REM aws ec2 delete-key-pair --key-name 677kp32144321
REM aws ec2 create-key-pair --key-name 677kp32144321 --query "KeyMaterial" --output text > 677kp32144321.pem
REM aws ec2 create-security-group --group-name MyBookStore32144321 --description "SG for 677 lab2"
REM 
REM REM Create EC2 instances
REM aws ec2 authorize-security-group-ingress --group-name MyBookStore32144321 --protocol tcp --port 8000-8002 --cidr 0.0.0.0/0
REM aws ec2 run-instances --image-id ami-054d94c846d1abc06 --instance-type t2.micro --key-name 677kp32144321 --tag-specifications "ResourceType=instance,Tags=[{Key=MyBookStore32144321,Value=m1}]" > instance.json
REM aws ec2 run-instances --image-id ami-054d94c846d1abc06 --instance-type t2.micro --key-name 677kp32144321 --tag-specifications "ResourceType=instance,Tags=[{Key=MyBookStore32144321,Value=m2}]" > instance.json
REM aws ec2 run-instances --image-id ami-054d94c846d1abc06 --instance-type t2.micro --key-name 677kp32144321 --tag-specifications "ResourceType=instance,Tags=[{Key=MyBookStore32144321,Value=m3}]" > instance.json
REM 
REM timeout 45
REM 
REM REM Access EC2 public ip address and instane ids
REM aws ec2 describe-instances  --filter "Name=tag-key,Values=MyBookStore32144321" "Name=instance-state-name,Values=running" --query "Reservations[*].Instances[*].InstanceId" --output text> ids.txt
REM aws ec2 describe-instances  --filter "Name=tag-key,Values=MyBookStore32144321" "Name=instance-state-name,Values=running" --query "Reservations[*].Instances[*].PublicIpAddress" --output text> ips.txt

REM Generate inital config file
@echo off 
del config
setlocal enabledelayedexpansion 
set servers[0]=frontend
set servers[1]=catalog
set servers[2]=order
set server_scripts[0]=run_frontend.sh
set server_scripts[1]=run_catalog.sh
set server_scripts[2]=run_order.sh 
set /a count = 0
set /a port = 8080
 

for /f "tokens=*" %%a in (ips.txt) do (

  (call echo %%servers[!count!]%%)>>tmp
  set /p server=<tmp
  del tmp
  
  echo !server!,%%a:!port!>> config
  if !count! == 0 (set frontend_addr=%%a:!port!)
  set /a count += 1
  set /a port += 1
)

pause

REM REM Migrate latest code and build docker image
REM set /a count = 0
REM for /f "tokens=*" %%a in (ips.txt) do (
REM 	ssh -o "StrictHostKeyChecking no" -i 677kp32144321.pem ec2-user@%%a "rm -rf MyBookStore"
REM 	scp -o "StrictHostKeyChecking no" -i 677kp32144321.pem -r %cd%  ec2-user@%%a:~/MyBookStore
REM 	scp -o "StrictHostKeyChecking no" -i 677kp32144321.pem .\docker_scripts\!server_scripts[!count!]!  ec2-user@%%a:~/MyBookStore/run.sh
REM 	start cmd /k ssh -o "StrictHostKeyChecking no" -i 677kp32144321.pem ec2-user@%%a "cd ~/MyBookStore;sh ec2_setup.sh"
REM 	set /a count += 1
REM )
REM 
REM timeout 45
REM REM Send Client Requests
REM @ECHO ON
REM curl -L "http://!frontend_addr!/lookup?item_number=1"
REM curl -L "http://!frontend_addr!/lookup?item_number=2"
REM curl -L "http://!frontend_addr!/lookup?item_number=3"
REM curl -L "http://!frontend_addr!/lookup?item_number=4"
REM curl -L "http://!frontend_addr!/search?topic=distributed+systems"
REM curl -L "http://!frontend_addr!/search?topic=graduate+school"
REM 
REM curl -L "http://!frontend_addr!/buy?item_number=1"
REM curl -L "http://!frontend_addr!/buy?item_number=1"
REM curl -L "http://!frontend_addr!/buy?item_number=1"
REM curl -L "http://!frontend_addr!/buy?item_number=1"
REM 
REM 
REM REM release AWS resources
REM aws ec2 delete-security-group --group-name MyBookStore32144321
REM for /f "tokens=*" %%a in (ids.txt) do (
REM   aws ec2 terminate-instances --instance-ids %%a
REM )
REM aws ec2 delete-key-pair --key-name 677kp32144321
REM del 677kp32144321.pem
REM del instance.json
REM del ids.txt
REM del ips.txt