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
import sys

from subprocess import run
from typing import Any as Whatever

# https://github.com/nginxinc/crossplane
import crossplane


def read_args() -> argparse.Namespace:
    """
    Parse arguments
    """
    parser = argparse.ArgumentParser(
        description="neatplan - nginx-like network configuration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-c",
        "--config",
        help="Config file absolute path",
        default="/etc/neatplan/default.conf",
    )

    return parser.parse_args()


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
    if ipaddress.ip_address(ip):
        return True
    return False


def is_ipv4(ip: str) -> bool:
    """
    IPv4 validation
    """
    if ipaddress.IPv4Interface(ip):
        return True
    return False


def is_ipv6(ip: str) -> bool:
    """
    IPv6 validation
    """
    if ipaddress.IPv6Interface(ip):
        return True
    return False


def set_ip(ip: str, iface: str) -> None:
    """
    Set IP
    """
    if is_ipv6(ip):
        run(["ip", "-6", "address", "add", ip, "dev", iface], check=True)


def set_route(route: str, default: bool, iface: str) -> None:
    """
    Set route
    """
    if is_ipv6(route):
        run(["ip", "-6", "route", "add", route, "dev", iface], check=True)
        if default:
            run(
                [
                    "ip",
                    "-6",
                    "route",
                    "add",
                    "default",
                    "via",
                    route,
                    "dev",
                    iface,
                ],
                check=False,
            )


def parse_addresses(addresses: Whatever, iface: str) -> None:
    """
    Parse addresses
    """
    for addr in addresses:
        set_ip(addr["args"][0], iface)


def parse_routes(routes: Whatever, iface: str) -> None:
    """
    Parse routes
    """
    for route in routes:
        if route["args"][1] == "default":
            set_route(route["args"][0], True, iface)
        else:
            set_route(route["args"][0], False, iface)


def parse_nameservers(nameservers: Whatever) -> None:
    """
    Parse nameservers
    """
    for ns in nameservers:
        # type = ns["directive"]
        nameserver = ns["args"][0]
        set_ns(nameserver)


def parse_network_configuration(cfg: Whatever) -> None:
    """
    Parse network configuration
    """
    for net in cfg:
        if net["directive"] == "backend":
            backend = net["args"][0]
            print(f"Backend: {backend}")
        if net["directive"] == "ethernet":
            ethernet = net["block"]
            for eth in ethernet:
                iface = eth["directive"]
                print(iface)
                for ethconf in eth["block"]:
                    if ethconf["directive"] == "addresses":
                        parse_addresses(ethconf["block"], iface)
                    if ethconf["directive"] == "routes":
                        parse_routes(ethconf["block"], iface)
        if net["directive"] == "dns":
            parse_nameservers(net["block"])


def set_ns(nameserver: str) -> None:
    """
    Set nameserver
    """
    with open("/etc/resolv.conf", "w+", encoding="utf-8") as resolv_conf:
        if is_ip(nameserver):
            print("nameserver", nameserver)
            resolv_conf.write(f"nameserver {nameserver}\n")


def main() -> None:
    """
    neatplan main
    """

    # Read arguments
    args = read_args()

    # Read config
    config_json = crossplane.parse(args.config)

    # Check for errors
    check_errors(config_json)

    # Parse config
    for cfg in config_json["config"][0]["parsed"]:
        if cfg["directive"] == "network":
            parse_network_configuration(cfg["block"])


if __name__ == "__main__":
    main()
