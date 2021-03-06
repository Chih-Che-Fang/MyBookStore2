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

REM start all type of servers
start cmd /k python -m src.server.front_end_server
start cmd /k python -m src.server.catalog_server 0
start cmd /k python -m src.server.catalog_server 1
start cmd /k python -m src.server.order_server 0
start cmd /k python -m src.server.order_server 1
start cmd /k python -m src.server.cache_server

REM REM test fault tolerance
REM REM Test primary server crashed and then recovered
REM curl localhost:8001/shutdown
REM curl localhost:8000/buy?item_number=2
REM curl localhost:8000/buy?item_number=2
REM curl localhost:8000/buy?item_number=2
REM start cmd /k python -m src.server.catalog_server 0
REM timeout 4
REM curl localhost:8002/query_by_item?item_number=2
REM curl localhost:8001/query_by_item?item_number=2
REM 
REM REM Test replicated server crashed and then recovered
REM curl localhost:8002/shutdown
REM curl localhost:8000/buy?item_number=2
REM curl localhost:8000/buy?item_number=2
REM curl localhost:8000/buy?item_number=2
REM start cmd /k python -m src.server.catalog_server 1
REM timeout 4
REM curl localhost:8002/query_by_item?item_number=2
REM curl localhost:8001/query_by_item?item_number=2



timeout 3
start cmd /k python -m src.client.client
pause