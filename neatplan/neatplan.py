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
from subprocess import run  # nosec
from typing import Any as Whatever


class Neatplan:
    """
    Neatplan class
    """

    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args

    def check_errors(self, config_json: Whatever) -> None:
        """
        check config errors
        """
        errors = config_json["errors"]

        if errors:
            print(json.dumps(errors, indent=2))
            sys.exit(1)

    def is_ip(self, ip: str) -> bool:
        """
        IP validation
        """
        try:
            if ipaddress.ip_address(ip):
                return True
        except ValueError:
            return False
        return False

    def is_ipv4(self, ip: str) -> bool:
        """
        IPv4 validation
        """
        try:
            if ipaddress.IPv4Interface(ip):
                return True
        except ValueError:
            return False
        return False

    def is_ipv6(self, ip: str) -> bool:
        """
        IPv6 validation
        """
        try:
            if ipaddress.IPv6Interface(ip):
                return True
        except ValueError:
            return False
        return False

    def which_ip(self) -> str:
        """
        Find ip command path
        """
        ip_cmd = which("ip")
        if not ip_cmd:
            print("ip command not found")
            sys.exit(1)
        else:
            return ip_cmd

    def iface_up(self, iface: str) -> None:
        """
        Bring the interface up
        """
        command = [self.which_ip(), "link", "set", iface, "up"]

        if not self.args.dry_run:
            run(command, check=True)  # nosec
            with open("/run/neatplan", "a+", encoding="utf-8") as neatplan_run:
                neatplan_run.write(f"{iface}\n")
        else:
            print("dry-run:", command)

    def set_ip(self, ip: str, iface: str) -> None:
        """
        Set IP
        """
        command = []

        if self.is_ipv6(ip):
            command = [self.which_ip(), "-6", "address", "add", ip, "dev", iface]

        if self.is_ipv4(ip):
            command = [self.which_ip(), "address", "add", ip, "dev", iface]

        run(command, check=False)  # nosec

    def set_route(self, route: str, iface: str) -> None:
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
                self.which_ip(),
                "route",
                "add",
                "default",
                "via",
                route[0],
                "dev",
                iface,
            ]
            default6_command = [
                self.which_ip(),
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
                self.which_ip(),
                "route",
                "add",
                route[0],
                "via",
                route[2],
                "dev",
                iface,
            ]
            via6_command = [
                self.which_ip(),
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
            command = [self.which_ip(), "route", "add", route[0], "dev", iface]
            command6 = [self.which_ip(), "-6", "route", "add", route[0], "dev", iface]

        if self.is_ipv6(route[0]):
            if default6_command:
                run(default6_command, check=False)  # nosec
            elif via6_command:
                run(via6_command, check=False)  # nosec
            else:
                run(command6, check=False)  # nosec

        if self.is_ipv4(route[0]):
            if default_command:
                run(default_command, check=False)  # nosec
            if via_command:
                run(via_command, check=False)  # nosec
            else:
                run(command, check=False)  # nosec

    def parse_addresses(self, addresses: Whatever, iface: str) -> None:
        """
        Parse addresses
        """
        for addr in addresses:
            if not self.args.dry_run:
                self.set_ip(addr["args"][0], iface)
            else:
                print("dry-run:", addr["args"][0], iface)

    def parse_routes(self, routes: Whatever, iface: str) -> None:
        """
        Parse routes
        """
        for route in routes:
            if not self.args.dry_run:
                self.set_route(route["args"], iface)
            else:
                print("dry-run:", route["args"], iface)

    def parse_nameservers(self, nameservers: Whatever) -> None:
        """
        Parse nameservers
        """
        resolv_conf_file = "/etc/resolv.conf"

        if not self.args.dry_run and os.path.isfile(resolv_conf_file):
            os.remove(resolv_conf_file)

        for ns in nameservers:
            # type = ns["directive"]
            nameserver = ns["args"][0]
            if not self.args.dry_run:
                self.set_ns(nameserver, resolv_conf_file)
            else:
                print("dry-run:", "nameserver", nameserver)

    def parse_firewall(self, firewalls: Whatever) -> None:
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

            if not self.args.dry_run:
                run([command, rules], check=False)  # nosec
            else:
                print("dry-run:", command, rules)

    def dhcp(self, version: int, iface: str) -> None:
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

        if not self.args.dry_run:
            run(command, check=False)  # nosec
        else:
            print("dry-run:", command)

    def parse_ethernet(self, ethernet: Whatever) -> None:
        """
        Parse ethernet
        """
        for eth in ethernet:
            iface = eth["directive"]
            self.iface_up(iface)
            for ethconf in eth["block"]:
                if ethconf["directive"] == "addresses":
                    self.parse_addresses(ethconf["block"], iface)
                if ethconf["directive"] == "routes":
                    self.parse_routes(ethconf["block"], iface)
                if (
                    ethconf["directive"] == "dhcp4"
                    and ethconf["block"][0]["args"][0] == "true"
                ):
                    self.dhcp(4, iface)
                if (
                    ethconf["directive"] == "dhcp6"
                    and ethconf["block"][0]["args"][0] == "true"
                ):
                    self.dhcp(6, iface)

    def parse_custom(self, custom: Whatever) -> None:
        """
        Parse custom commands
        """
        for cmd in custom:
            command = cmd["args"][0]
            if not self.args.dry_run:
                os.system(command)  # nosec
            else:
                print("dry-run:", command)

    def parse_network_configuration(self, cfg: Whatever) -> None:
        """
        Parse network configuration
        """
        for net in cfg:
            # if net["directive"] == "backend":
            #     backend = net["args"][0]
            #     print(f"Backend: {backend}")
            if net["directive"] == "before":
                self.parse_custom(net["block"])
            if net["directive"] == "firewall":
                self.parse_firewall(net["block"])
            if net["directive"] == "ethernet":
                self.parse_ethernet(net["block"])
            if net["directive"] == "dns":
                self.parse_nameservers(net["block"])
            if net["directive"] == "after":
                self.parse_custom(net["block"])

    def set_ns(self, nameserver: str, resolv_conf_file: str) -> None:
        """
        Set nameserver
        """
        with open(resolv_conf_file, "a+", encoding="utf-8") as resolv_conf:
            if self.is_ip(nameserver):
                print("nameserver", nameserver)
                resolv_conf.write(f"nameserver {nameserver}\n")
