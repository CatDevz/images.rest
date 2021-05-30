#!/bin/sh

# Loading all variables from .env
export $(grep -v '^#' .env | xargs)

# Set HOST to localhost if it isn't set
if [ -z $HOST ]; then
  export HOST="localhost"
fi

# Set PORT to 8000 if it isn't set
if [ -z $PORT ]; then
  export PORT="8000"
fi

exec uvicorn app.api:app --reload --reload-dir app --host $HOST --port $PORT
