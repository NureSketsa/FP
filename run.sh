#!/bin/bash

# bash run.sh
# run dari FP
# minimum python 3.10

source venv/bin/activate
#uvicorn MAIN.main:app --reload
uvicorn MAIN.main:app --reload --host 0.0.0.0 --port 8010
#gunicorn MAIN.main:app -k uvicorn.workers.UvicornWorker -w 4 -t 900 -b 0.0.0.0:8010
