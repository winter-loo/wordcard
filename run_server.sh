#!/bin/bash

cwd=$(dirname $0)

pushd $cwd

export GOOGLE_APPLICATION_CREDENTIALS=`pwd`/my-translation-sa-key.json

if [ -d .venv ]; then
  source .venv/bin/activate
else
  python3.9 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
fi

if [ ! -f data.db ]; then
  python create_database.py
fi

PORT=1500

pid=$(ps aux | grep flask | grep $PORT | awk '{print $2}')
if [ -n $pid ]; then
  kill $pid
fi

flask run --host=0.0.0.0 --port $PORT > app.log 2>&1 &
flask routes
echo "-------------------------"
tail -12 app.log
