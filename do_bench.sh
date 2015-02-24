#!/bin/bash

#config this how you want 
# assumes:
# 100 surveys
# create endpoint is desired
# you have survey.json present in benchmark

sh clean_slate.sh > /dev/null 

if [ -z "`awk /TEST_USER/ local_settings.py`" ]; 
then 
    echo 'TEST_USER = "poop"' >> local_settings.py; 
else
    sed -i 's/TEST_USER.*/TEST_USER="poop"/' local_settings.py
fi

python -m cProfile -o /tmp/prof benchmark/benchmark_tornado.py --path=/api/surveys/create --post_file=benchmark/survey.json -n=100
