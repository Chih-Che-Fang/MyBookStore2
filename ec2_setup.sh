#!/bin/bash
sudo service docker start
sudo usermod -a -G docker ec2-user
sudo docker stop $(docker ps -aq)
sudo docker ps -q -a | xargs docker rm
sudo docker build -t bookstore .
sudo docker run -p 8000-8002:8000-8002 bookstore