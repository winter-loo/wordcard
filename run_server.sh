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


netstat -apn | grep 1500 | grep python | grep LISTEN
if [ $? -eq 0 ]; then
  exit 0
fi

flask run --host=0.0.0.0 --port 1500 > app.log 2>&1 &
flask routes
echo "-------------------------"
tail -12 app.log
