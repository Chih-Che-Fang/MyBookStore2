#!/bin/bash
>order_log

echo "init,1,3,10,distributed systems,How to get a good grade in 677 in 20 minutes a day">catalog_log
echo "init,2,3,20,distributed systems,RPCs for Dummies">>catalog_log
echo "init,3,3,5,graduate school,Xen and the Art of Surviving Graduate School">>catalog_log
echo "init,4,3,15,graduate school,Cooking for the Impatient Graduate Student"$'\n'>>catalog_log

exec python3 front_end_server.py &
exec python3 order_server.py &
exec python3 catalog_server.py