#!/bin/ksh

cd `dirname $0`

if [ ! -f ./venv/bin/python ]; then
    python3 -m venv venv
fi

./venv/bin/python ./pySAP.py
