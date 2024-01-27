#!/usr/bin/env python3
"""
neatplan - nginx-like network configuration
Copyright (C) 2024 c0m4r

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import argparse
import ipaddress
import json
import os
import sys

from shutil import which
from subprocess import run
from typing import Any as Whatever

# https://github.com/nginxinc/crossplane
import crossplane
import psutil


__VERSION = "0.2.0"


def read_args() -> argparse.Namespace:
    """
    Parse arguments
    """
    parser = argparse.ArgumentParser(
        prog="neatplan",
        description="nginx-style network configuration",
        epilog="https://github.com/c0m4r/neatplan",
    )

    parser.add_argument(
        "-c",
        "--config",
        help="Config file absolute path",
        default="/etc/neatplan/default.conf",
    )
    parser.add_argument(
        "-v",
        "--version",
        help="Show version and exit",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--dry-run",
        help="Don't execute, only show what you've got",
        action="store_true",
        default=False,
    )

    return parser.parse_args()


def check_init_system() -> None:
    """
    pest control
    """
    init_name = psutil.Process(1).name()
    if init_name == "systemd":
        print("systemd detected, this program will self-destruct now")
        print("just kidding, but seriously: ZnVjayBzeXN0ZW1k")


def check_errors(config: Whatever) -> None:
    """
    check config errors
    """
    errors = config["errors"]

    if errors:
        print(json.dumps(errors, indent=2))
        sys.exit(1)


def is_ip(ip: str) -> bool:
    """
    IP validation
    """
    try:
        if ipaddress.ip_address(ip):
            return True
    except ValueError:
        return False
    return False


def is_ipv4(ip: str) -> bool:
    """
    IPv4 validation
    """
    try:
        if ipaddress.IPv4Interface(ip):
            return True
    except ValueError:
        return False
    return False


def is_ipv6(ip: str) -> bool:
    """
    IPv6 validation
    """
    try:
        if ipaddress.IPv6Interface(ip):
            return True
    except ValueError:
        return False
    return False


def which_ip() -> str:
    """
    Find ip command path
    """
    ip_cmd = which("ip")
    if not ip_cmd:
        print("ip command not found")
        sys.exit(1)
    else:
        return ip_cmd


def iface_up(iface: str, dry_run: bool) -> None:
    """
    Bring the interface up
    """
    command = [which_ip(), "link", "set", iface, "up"]

    if not dry_run:
        run(command, check=True)
        with open("/run/neatplan", "a+", encoding="utf-8") as neatplan_run:
            neatplan_run.write(f"{iface}\n")
    else:
        print("dry-run:", command)


def set_ip(ip: str, iface: str) -> None:
    """
    Set IP
    """
    command = []

    if is_ipv6(ip):
        command = [which_ip(), "-6", "address", "add", ip, "dev", iface]

    if is_ipv4(ip):
        command = [which_ip(), "address", "add", ip, "dev", iface]

    run(command, check=False)


def set_route(route: str, iface: str) -> None:
    """
    Set route
    """

    command = []
    command6 = []
    default_command = []
    default6_command = []
    via_command = []
    via6_command = []

    if "default" in route:
        default_command = [
            which_ip(),
            "route",
            "add",
            "default",
            "via",
            route[0],
            "dev",
            iface,
        ]
        default6_command = [
            which_ip(),
            "-6",
            "route",
            "add",
            "default",
            "via",
            route[0],
            "dev",
            iface,
        ]
    elif "via" in route:
        via_command = [
            which_ip(),
            "route",
            "add",
            route[0],
            "via",
            route[2],
            "dev",
            iface,
        ]
        via6_command = [
            which_ip(),
            "-6",
            "route",
            "add",
            "default",
            "via",
            route,
            "dev",
            iface,
        ]
    else:
        command = [which_ip(), "route", "add", route[0], "dev", iface]
        command6 = [which_ip(), "-6", "route", "add", route[0], "dev", iface]

    if is_ipv6(route[0]):
        if default6_command:
            run(default6_command, check=False)
        elif via6_command:
            run(via6_command, check=False)
        else:
            run(command6, check=False)

    if is_ipv4(route[0]):
        if default_command:
            run(default_command, check=False)
        if via_command:
            run(via_command, check=False)
        else:
            run(command, check=False)


def parse_addresses(addresses: Whatever, iface: str, dry_run: bool) -> None:
    """
    Parse addresses
    """
    for addr in addresses:
        if not dry_run:
            set_ip(addr["args"][0], iface)
        else:
            print("dry-run:", addr["args"][0], iface)


def parse_routes(routes: Whatever, iface: str, dry_run: bool) -> None:
    """
    Parse routes
    """
    for route in routes:
        if not dry_run:
            set_route(route["args"], iface)
        else:
            print("dry-run:", route["args"], iface)


def parse_nameservers(nameservers: Whatever, dry_run: bool) -> None:
    """
    Parse nameservers
    """
    resolv_conf_file = "/etc/resolv.conf"

    if not dry_run and os.path.isfile(resolv_conf_file):
        os.remove(resolv_conf_file)

    for ns in nameservers:
        # type = ns["directive"]
        nameserver = ns["args"][0]
        if not dry_run:
            set_ns(nameserver, resolv_conf_file)
        else:
            print("dry-run:", "nameserver", nameserver)


def parse_firewall(firewalls: Whatever, dry_run: bool) -> None:
    """
    Parse firewall
    """
    for firewall in firewalls:
        command = ""
        rules = ""
        if firewall["directive"] == "iptables":
            command = "iptables-restore"
            rules = firewall["args"][0]
        if firewall["directive"] == "ip6tables":
            command = "ip6tables-restore"
            rules = firewall["args"][0]
        if not which(command):
            print(command, "not found")
            continue
        if not os.path.isfile(rules):
            print(rules, "is not a file")
            continue

        if not dry_run:
            run([command, rules], check=False)
        else:
            print("dry-run:", command, rules)


def dhcp(version: int, iface: str, dry_run: bool) -> None:
    """
    DHCP
    """
    command = []
    dhclient = "/usr/sbin/dhclient"

    if not os.path.isfile(dhclient):
        print(f"DHCP unavailable: {dhclient} not found")
    elif version == 6:
        command = [dhclient, "-6", "-1", iface]
    else:
        command = [dhclient, "-1", iface]

    if not dry_run:
        run(command, check=False)
    else:
        print("dry-run:", command)


def parse_ethernet(ethernet: Whatever, dry_run: bool) -> None:
    """
    Parse ethernet
    """
    for eth in ethernet:
        iface = eth["directive"]
        iface_up(iface, dry_run)
        for ethconf in eth["block"]:
            if ethconf["directive"] == "addresses":
                parse_addresses(ethconf["block"], iface, dry_run)
            if ethconf["directive"] == "routes":
                parse_routes(ethconf["block"], iface, dry_run)
            if (
                ethconf["directive"] == "dhcp4"
                and ethconf["block"][0]["args"][0] == "true"
            ):
                dhcp(4, iface, dry_run)
            if (
                ethconf["directive"] == "dhcp6"
                and ethconf["block"][0]["args"][0] == "true"
            ):
                dhcp(6, iface, dry_run)


def parse_custom(custom: Whatever, dry_run: bool) -> None:
    """
    Parse custom commands
    """
    for cmd in custom:
        command = cmd["args"][0]
        if not dry_run:
            os.system(command)  # nosec
        else:
            print("dry-run:", command)


def parse_network_configuration(cfg: Whatever, dry_run: bool) -> None:
    """
    Parse network configuration
    """
    for net in cfg:
        # if net["directive"] == "backend":
        #     backend = net["args"][0]
        #     print(f"Backend: {backend}")
        if net["directive"] == "before":
            parse_custom(net["block"], dry_run)
        if net["directive"] == "firewall":
            parse_firewall(net["block"], dry_run)
        if net["directive"] == "ethernet":
            parse_ethernet(net["block"], dry_run)
        if net["directive"] == "dns":
            parse_nameservers(net["block"], dry_run)
        if net["directive"] == "after":
            parse_custom(net["block"], dry_run)


def set_ns(nameserver: str, resolv_conf_file: str) -> None:
    """
    Set nameserver
    """
    with open(resolv_conf_file, "a+", encoding="utf-8") as resolv_conf:
        if is_ip(nameserver):
            print("nameserver", nameserver)
            resolv_conf.write(f"nameserver {nameserver}\n")


def main() -> None:
    """
    neatplan main
    """

    print("neatplan by c0m4r", f"v{__VERSION}")

    # Read arguments
    args = read_args()

    if args.version:
        sys.exit(0)
    if args.dry_run:
        print("Running dry-run mode")

    # Read config
    config_json = crossplane.parse(args.config)

    # Check for errors
    check_errors(config_json)

    # Check init system
    check_init_system()

    # Set lookpback device up
    iface_up("lo", args.dry_run)

    # Parse config
    for cfg in config_json["config"][0]["parsed"]:
        if cfg["directive"] == "network":
            parse_network_configuration(cfg["block"], args.dry_run)


if __name__ == "__main__":
    main()
