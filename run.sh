#!/bin/sh

# wait_for()
# {
#   echo "Waiting $1 seconds for $2:$3"
#   timeout $1 sh -c 'until nc -z $0 $1; do sleep 0.1; done' $2 $3 || return 1
#   echo "$2:$3 available"
# }

echo Sleep 5...
sleep 5

# wait_for 10 ${POSTGRES_HOST} ${POSTGRES_PORT}


alembic upgrade head 
uvicorn main:app --host="0.0.0.0" --port 9000
#python ./main.py





