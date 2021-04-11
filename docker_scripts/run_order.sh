#!/bin/bash
> order_log

exec python3 -m src.server.order_server
