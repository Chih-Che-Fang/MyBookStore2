REM Write initialization log to catalog & order server log
del /Q .\output\*

REM  Write initial config info for local machine
echo frontend,127.0.0.1:8000>config
echo catalog,127.0.0.1:8001>>config
echo catalog,127.0.0.1:8002>>config
echo order,127.0.0.1:8003>>config
echo order,127.0.0.1:8004>>config
echo cache,127.0.0.1:8005>>config


REM Get docker entry point script
xcopy /y .\docker_scripts\run_all.sh .\run.sh

REM kill all docker process
@ECHO OFF
FOR /f "tokens=*" %%i IN ('docker ps -aq') DO docker stop %%i
FOR /f "tokens=*" %%i IN ('docker ps -aq') DO docker rm %%i

REM Build docker image
docker build -t bookstore .

REM Run the docker image and map port to local host
start cmd /k docker run -p 8000-8005:8000-8005 --name mybookstore32144321 bookstore

timeout 20

REM pull log from catalog & order server in the container
docker cp mybookstore32144321:/usr/src/MyBookStore/output/catalog0_log .\output
docker cp mybookstore32144321:/usr/src/MyBookStore/output/catalog1_log .\output
docker cp mybookstore32144321:/usr/src/MyBookStore/output/order0_log .\output
docker cp mybookstore32144321:/usr/src/MyBookStore/output/order1_log .\output
docker cp mybookstore32144321:/usr/src/MyBookStore/output/client_log .\output
docker cp mybookstore32144321:/usr/src/MyBookStore/output/cache_log .\output

pause