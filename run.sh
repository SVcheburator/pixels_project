#!/bin/sh

echo Sleep 5...
sleep 5

alembic upgrade head 
uvicorn main:app --host="0.0.0.0" --port 9000
#python ./main.py





