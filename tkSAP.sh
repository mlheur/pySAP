#!/bin/sh
cd "`dirname $0`"
. venv/bin/activate
rm pySAP_trace.log
python -m tkSAP
