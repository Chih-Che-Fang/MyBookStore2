REM Migrate code 
ssh -o "StrictHostKeyChecking no" -i 677kp32144321.pem ec2-user@%1 "rm -rf MyBookStore"
scp -o "StrictHostKeyChecking no" -i 677kp32144321.pem -r %cd%  ec2-user@%1:~/MyBookStore

REM Update the docker script according the type of server (frontend/catalog/order)
scp -o "StrictHostKeyChecking no" -i 677kp32144321.pem .\docker_scripts\%2  ec2-user@%1:~/MyBookStore/run.sh

REM REM Invoke ec2_setup script to build docker image, set up initalization log, and run the docker image for each type of server(frontend/order/catalog)
ssh -o "StrictHostKeyChecking no" -i 677kp32144321.pem ec2-user@%1 cd ~/MyBookStore;sh ec2_setup.sh %3