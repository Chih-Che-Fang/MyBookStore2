#!/bin/bash
> order_log
# log initilazation state
echo "init,1,1000,10,distributed systems,How to get a good grade in 677 in 20 minutes a day"> ./output/catalog_log
echo "init,2,1000,20,distributed systems,RPCs for Dummies">> ./output/catalog_log
echo "init,3,1000,5,graduate school,Xen and the Art of Surviving Graduate School">> ./output/catalog_log
echo "init,4,1000,15,graduate school,Cooking for the Impatient Graduate Student"$'\n'>> ./output/catalog_log

# Start book store servers
exec python3 ./src/front_end_server.py &
exec python3 ./src/order_server.py &
exec python3 ./src/catalog_server.py &
sleep 5
exec python3 ./src/client.py &
sleep 120000