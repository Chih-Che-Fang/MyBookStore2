#!/bin/bash

# Start book store servers
exec python3 -m src.server.front_end_server &
sleep 3 &
exec python3 -m src.server.order_server 0 &
exec python3 -m src.server.order_server 1 &
exec python3 -m src.server.catalog_server 0 &
exec python3 -m src.server.catalog_server 1 &
exec python3 -m src.server.cache_server &
sleep 5
exec python3 -m src.client.client &
sleep 120000