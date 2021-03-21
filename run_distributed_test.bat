REM Create key pair, security group
aws ec2 delete-key-pair --key-name 677kp32144321
aws ec2 create-key-pair --key-name 677kp32144321 --query "KeyMaterial" --output text > 677kp32144321.pem
aws ec2 create-security-group --group-name MyBookStore32144321 --description "SG for 677 lab2"

REM Create EC2 instances
aws ec2 authorize-security-group-ingress --group-name MyBookStore32144321 --protocol tcp --port 8000-8002 --cidr 0.0.0.0/0
aws ec2 run-instances --image-id ami-023ba056901e16c76 --instance-type t2.micro --key-name 677kp32144321 --tag-specifications "ResourceType=instance,Tags=[{Key=MyBookStore32144321,Value=m1}]" > instance.json
aws ec2 run-instances --image-id ami-023ba056901e16c76 --instance-type t2.micro --key-name 677kp32144321 --tag-specifications "ResourceType=instance,Tags=[{Key=MyBookStore32144321,Value=m2}]" > instance.json
aws ec2 run-instances --image-id ami-023ba056901e16c76 --instance-type t2.micro --key-name 677kp32144321 --tag-specifications "ResourceType=instance,Tags=[{Key=MyBookStore32144321,Value=m3}]" > instance.json

timeout 45

REM Access EC2 public ip address and instane ids
aws ec2 describe-instances  --filter "Name=tag-key,Values=MyBookStore32144321" "Name=instance-state-name,Values=running" --query "Reservations[*].Instances[*].InstanceId" --output text> ids.txt
aws ec2 describe-instances  --filter "Name=tag-key,Values=MyBookStore32144321" "Name=instance-state-name,Values=running" --query "Reservations[*].Instances[*].PublicIpAddress" --output text> ips.txt




REM release AWS resources
aws ec2 delete-security-group --group-name MyBookStore32144321
for /f "tokens=*" %%a in (ids.txt) do (
  aws ec2 terminate-instances --instance-ids %%a
)
aws ec2 delete-key-pair --key-name 677kp32144321
del 677kp32144321.pem
del instance.json
del ids.txt
del ips.txt