#!/bin/sh

SCRIPT=$(readlink -f "$0")
SCRIPT_PATH=$(dirname "$SCRIPT")

cd $SCRIPT_PATH

if [ $(id -u) -ne 0 ]; then
    exec sudo "${SCRIPT}"
    exit 1
fi

VERSION=$(grep ^__VER neatplan/__init__.py | awk '{print $3}' | sed s/\"//g;)
echo "neatplan v${VERSION}"

# ------------------------------------
# Functions
# ------------------------------------

custom_crossplane_hack() {
    crossplane_path=$(dirname .venv/lib/python*/site-packages)
    if [[ -d $crossplane_path ]]; then
        touch ${crossplane_path}/site-packages/crossplane/py.typed
        sed -i 's/parse(filename,/parse(filename: str,/g;' ${crossplane_path}/site-packages/crossplane/parser.py
    fi
}

deploy_venv() {
    if [ ! -e .venv/bin/activate ]; then
        echo "Deploying Python venv..."
        python3 -m venv .venv
        . .venv/bin/activate
        pip3 install -r requirements.txt
        custom_crossplane_hack
    else
        echo "Python venv already deployed"
    fi
}

deploy_bin() {
    neatplan_target_bin="/usr/local/bin/neatplan"
    if [ ! -x $neatplan_target_bin ]; then
        echo "Creating symlink: ${neatplan_target_bin}"
        ln -s ${SCRIPT_PATH}/neatplan.sh $neatplan_target_bin
        chmod u+x $neatplan_target_bin
    else
        echo "${neatplan_target_bin} already exists"
    fi
}

deploy_config() {
    if [ ! -e /etc/neatplan/default.conf ]; then
        echo "Deploying default config"
        cp -r etc/neatplan /etc/
        default_eth_iface=$(ls /sys/class/net/ | grep ^e | head -n 1)
        if [ "$default_eth_iface" ]; then
            sed -i "s/eth0/$default_eth_iface/g;" /etc/neatplan/default.conf
        fi
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
deploy_bin
deploy_config
deploy_init

echo "Configuration: /etc/neatplan/default.conf"
echo "Usage: $SCRIPT_PATH/neatplan.sh --help"
