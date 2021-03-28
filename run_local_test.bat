REM Write initialization log to catalog & order server log
echo. 2> .\output\order_log
echo init,1,1000,10,distributed systems,How to get a good grade in 677 in 20 minutes a day> .\output\catalog_log
echo init,2,1000,20,distributed systems,RPCs for Dummies>> .\output\catalog_log
echo init,3,1000,5,graduate school,Xen and the Art of Surviving Graduate School>> .\output\catalog_log
echo init,4,1000,15,graduate school,Cooking for the Impatient Graduate Student>> .\output\catalog_log
echo. 2>> .\output\catalog_log

REM  Write config info for local machine
echo frontend,127.0.0.1:8000>config
echo catalog,127.0.0.1:8001>>config
echo order,127.0.0.1:8002>>config

REM Get docker entry point script
xcopy /y .\docker_scripts\run_all.sh .\run.sh

REM kill all docker process
@ECHO OFF
FOR /f "tokens=*" %%i IN ('docker ps -aq') DO docker stop %%i
FOR /f "tokens=*" %%i IN ('docker ps -aq') DO docker rm %%i

REM Build docker image
docker build -t bookstore .

REM Run the docker image and map port to local host
start cmd /k docker run -p 8000-8002:8000-8002 --name mybookstore32144321 bookstore 

timeout 20

REM pull log from catalog & order server in the container
docker cp mybookstore32144321:/usr/src/MyBookStore/output/catalog_log .\output
docker cp mybookstore32144321:/usr/src/MyBookStore/output/order_log .\output
docker cp mybookstore32144321:/usr/src/MyBookStore/output/client_log .\output

pause