#!/bin/bash

RELATIVEPATH="$1"

if [ ! -e ${RELATIVEPATH}/lib/python3.11/site-packages/crossplane/parser.py ]; then
    echo "wrong relative path"
    exit 1
fi

touch ${RELATIVEPATH}/lib/python3.11/site-packages/crossplane/py.typed
sed -i 's/parse(filename,/parse(filename: str,/g;' ${RELATIVEPATH}/lib/python3.11/site-packages/crossplane/parser.py
