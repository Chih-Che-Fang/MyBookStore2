#!/bin/bash

# Start docker service
sudo service docker start
sudo usermod -a -G docker ec2-user

# Kill all containers
sudo docker stop $(docker ps -aq)
sudo docker rm $(docker ps -aq)
sudo docker ps -q -a | xargs docker rm

# Build docker image
sudo docker build -t bookstore .

# Run Dokcer image
sudo docker run -p 8000-8002:8000-8002 --name mybookstore32144321 bookstore
sleep 20

# Pull log from catalog & order server in the container
sudo docker cp mybookstore32144321:/usr/src/MyBookStore/output/catalog_log ./output
sudo docker cp mybookstore32144321:/usr/src/MyBookStore/output/order_log ./output
