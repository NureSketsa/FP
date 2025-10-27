#!/bin/bash

# bash run.sh
# run dari FP
# minimum python 3.10

# pip install -r requirements.txt
# pip install -r requirements.txt --upgrade --ignore-installed --no-deps
uvicorn MAIN.main:app --reload