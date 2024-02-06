#!/bin/bash

# neatplan by c0m4r
# https://github.com/c0m4r/neatplan
# Licnse: GPLv3

neatplan_runfile="/run/neatplan"
ipcmd="/sbin/ip"
ifaces=$(cat ${neatplan_runfile})

for iface in $ifaces ; do
    echo $iface
    tentatives=$($ipcmd -6 a s $iface | grep tentative)
    iters=1
    until [ ! "$tentatives" ] ; do
        sleep 0.1
        tentatives=$($ipcmd -6 a s $iface | grep tentative)
        iters=$(( iters + 1 ))
        # Give up after 3 seconds to avoid infinite loop
        if [ $iters -gt 30 ]; then
            tentatives=""
        fi
    done
done
