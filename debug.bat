REM Write initialization log to catalog & order server log
del /Q .\output\*
echo. 2> .\output\order_log
echo init,1,3,10,distributed systems,How to get a good grade in 677 in 20 minutes a day> .\output\catalog_log
echo init,2,3,20,distributed systems,RPCs for Dummies>> .\output\catalog_log
echo init,3,3,5,graduate school,Xen and the Art of Surviving Graduate School>> .\output\catalog_log
echo init,4,3,15,graduate school,Cooking for the Impatient Graduate Student>> .\output\catalog_log
echo. 2>> .\output\catalog_log

REM  Write initial config info for local machine
echo frontend,127.0.0.1:8000>config
echo catalog,127.0.0.1:8001>>config
echo catalog,127.0.0.1:8002>>config
echo order,127.0.0.1:8003>>config
echo order,127.0.0.1:8004>>config
echo cache,127.0.0.1:8005>>config

REM kill all docker process
@ECHO OFF
FOR /f "tokens=*" %%i IN ('docker ps -aq') DO docker stop %%i
FOR /f "tokens=*" %%i IN ('docker ps -aq') DO docker rm %%i

start cmd /k python -m src.server.front_end_server
start cmd /k python -m src.server.catalog_server 0
start cmd /k python -m src.server.catalog_server 1
start cmd /k python -m src.server.order_server 0
start cmd /k python -m src.server.order_server 1
start cmd /k python -m src.server.cache_server

timeout 3
start cmd /k python -m src.client.client