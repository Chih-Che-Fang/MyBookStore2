REM Write initialization log to catalog & order server log
del /Q .\output\*

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