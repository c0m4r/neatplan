#!/bin/sh

# Neatplan wrapper

SCRIPT=$(readlink -f "$0")
SCRIPT_PATH=$(dirname "$SCRIPT")

cd $SCRIPT_PATH

if [ $(id -u) -ne 0 ]; then
    exec sudo "${SCRIPT}"
    exit 1
fi

if [ ! -d .venv ] && [ -x deploy.sh ]; then
    . deploy.sh
fi

. .venv/bin/activate
python3 -m neatplan "$@"
