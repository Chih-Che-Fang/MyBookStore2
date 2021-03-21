echo. 2>order_log
echo init,1,3,10,distributed systems,How to get a good grade in 677 in 20 minutes a day>catalog_log
echo init,2,3,20,distributed systems,RPCs for Dummies>>catalog_log
echo init,3,3,5,graduate school,Xen and the Art of Surviving Graduate School>>catalog_log
echo init,4,3,15,graduate school,Cooking for the Impatient Graduate Student>>catalog_log
echo. 2>>catalog_log

REM kill all docker process
@ECHO OFF
FOR /f "tokens=*" %%i IN ('docker ps -q') DO docker kill %%i

docker build -t bookstore .

start cmd /k docker run -it -p 8000-8002:8000-8002 bookstore 

timeout 5

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