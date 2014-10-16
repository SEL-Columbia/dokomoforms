#!/bin/bash

# run_tests.sh
# Kick off all the unit tests with the correct environment settings
# (should eventually change this to use nose...)

DOKO="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYTHONPATH=$PYTHONPATH:$DOKO:$DOKO/config:$DOKO/db:$DOKO/schema:$DOKO/tests:$DOKO/utils

tests=`ls $DOKO/tests/*.py`
for test in $tests
do
   /usr/bin/env python3 $test
   rc=$?
   if [[ $rc != 0 ]] ; then
       exit $rc
   fi
done
