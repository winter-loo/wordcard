#!/bin/bash

cwd=$(dirname $0)

pushd $cwd

netstat -apn | grep 1500
if [ $? -eq 0 ]; then
  exit 0
fi

flask --app wordcard_server run --host=0.0.0.0 --port 1500 &