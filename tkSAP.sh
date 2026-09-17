#!/bin/sh
cd "`dirname $0`"
. venv/bin/activate
rm pySAP_trace.log 2>/dev/null
python -m tkSAP
