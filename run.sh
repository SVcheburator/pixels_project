#!/bin/sh

echo Sleep 2...
sleep 2


alembic upgrade head 
uvicorn main:app --host="0.0.0.0" --port 9000
#python ./main.py





