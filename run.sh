#!/bin/bash

# bash run.sh
# run dari FP
# minimum python 3.10

source venv/bin/activate
#uvicorn MAIN.main:app --reload
#uvicorn MAIN.main:app --reload --host 0.0.0.0 --port 8000
gunicorn -k uvicorn.workers.UvicornWorker MAIN.main:app --bind 0.0.0.0:8000 --workers 4