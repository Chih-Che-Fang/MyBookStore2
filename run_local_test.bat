REM Write initialization log to catalog & order server log
echo. 2> .\output\order_log
echo init,1,3,10,distributed systems,How to get a good grade in 677 in 20 minutes a day> .\output\catalog_log
echo init,2,3,20,distributed systems,RPCs for Dummies>> .\output\catalog_log
echo init,3,3,5,graduate school,Xen and the Art of Surviving Graduate School>> .\output\catalog_log
echo init,4,3,15,graduate school,Cooking for the Impatient Graduate Student>> .\output\catalog_log
echo. 2>> .\output\catalog_log

REM  Write config info for local machine
echo frontend,127.0.0.1:8000>config
echo catalog,127.0.0.1:8001>>config
echo order,127.0.0.1:8002>>config



REM kill all docker process
@ECHO OFF
FOR /f "tokens=*" %%i IN ('docker ps -q') DO docker kill %%i

REM Build docker image
docker build -t bookstore .

REM Run the docker image and map port to local host
start cmd /k docker run -it -p 8000-8002:8000-8002 bookstore 

REM Wait for the docker image initialization
timeout 10

REM Perform a series of client rquest for validation
@ECHO ON
curl -L "http://127.0.0.1:8000/lookup?item_number=1"
curl -L "http://127.0.0.1:8000/lookup?item_number=2"
curl -L "http://127.0.0.1:8000/lookup?item_number=3"
curl -L "http://127.0.0.1:8000/lookup?item_number=4"
curl -L "http://127.0.0.1:8000/search?topic=distributed+systems"
curl -L "http://127.0.0.1:8000/search?topic=graduate+school"

curl -L "http://127.0.0.1:8000/buy?item_number=1"
curl -L "http://127.0.0.1:8000/buy?item_number=1"
curl -L "http://127.0.0.1:8000/buy?item_number=1"
curl -L "http://127.0.0.1:8000/buy?item_number=1"


pause