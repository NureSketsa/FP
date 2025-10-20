#!/bin/bash

# bash run.sh
# run in FP-fastapi dir
# minimum python 3.10
pip install -r requirements.txt

uvicorn main:app --reload

cd FP
uvicorn MAIN.main:app --reload