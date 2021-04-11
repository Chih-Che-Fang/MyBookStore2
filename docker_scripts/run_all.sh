#!/bin/bash
> order_log
# log initilazation state
echo "init,1,3,10,distributed systems,How to get a good grade in 677 in 20 minutes a day"> ./output/catalog_log
echo "init,2,3,20,distributed systems,RPCs for Dummies">> ./output/catalog_log
echo "init,3,3,5,graduate school,Xen and the Art of Surviving Graduate School">> ./output/catalog_log
echo "init,4,3,15,graduate school,Cooking for the Impatient Graduate Student"$'\n'>> ./output/catalog_log

# Start book store servers
exec python3 -m src.server.front_end_server &
exec python3 -m src.server.order_server &
exec python3 -m src.server.catalog_server &
exec python3 -m src.server.cache_server &
sleep 5
exec python3 -m src.client.client &
sleep 120000