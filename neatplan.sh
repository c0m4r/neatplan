#!/bin/sh

# Neatplan wrapper

SCRIPT=$(readlink -f "$0")
SCRIPT_PATH=$(dirname "$SCRIPT")

cd $SCRIPT_PATH

if [ ! -d .venv ] && [ -x deploy.sh ]; then
    . deploy.sh
fi

. .venv/bin/activate
python3 -m neatplan "$@"