#!/bin/sh

SCRIPT=$(readlink -f "$0")
SCRIPT_PATH=$(dirname "$SCRIPT")

cd $SCRIPT_PATH

VERSION=$(grep ^__VER neatplan.py | awk '{print $3}' | sed s/\"//g;)
echo "neatplan v${VERSION}"

# ------------------------------------
# Functions
# ------------------------------------

deploy_venv() {
    if [ ! -e .venv/bin/activate ]; then
        echo "Deploying Python venv..."
        python3 -m venv .venv
        . .venv/bin/activate
        pip3 install -r requirements.txt
    else
        echo "Python venv already deployed"
    fi
}

deploy_config() {
    if [ ! -e /etc/neatplan/default.conf ]; then
        echo "Deploying default config"
        cp -r etc/neatplan /etc/
    else
        echo "Config already deployed"
    fi
}

deploy_init() {
    if [ -e /etc/alpine-release ]; then
        # Alpine + OpenRC
        if [ ! -e /etc/init.d/neatplan ]; then
            echo "Deploying OpenRC init script..."
            cp etc/init.d/neatplan /etc/init.d/
        else
            echo "OpenRC init already deployed"
        fi
        echo -n "Enable with: rc-update add neatplan boot"
        echo " && rc-update del networking boot"
    elif [ -d /etc/runit ]; then
        # runit
        if [ ! -e /etc/sv/neatplan/run ]; then
            echo "Deploying neatplan runit script"
            cp -r etc/sv/neatplan /etc/sv/
        else
            echo "neatplan runit script already deployed"
        fi
        echo "Enable with: ln -s /etc/sv/neatplan /var/service/"
    else
        echo "Init scripts for your distro not available"
    fi
}

# ------------------------------------
# Deploy
# ------------------------------------

deploy_venv
deploy_config
deploy_init

echo "Configuration: /etc/neatplan/default.conf"
echo "Usage: $SCRIPT_PATH/neatplan --help"
