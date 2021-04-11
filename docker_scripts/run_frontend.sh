#!/bin/bash

exec python3 -m src.server.front_end_server &
exec python3 -m src.server.cache_server
