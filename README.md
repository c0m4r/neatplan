# neatplan

[![Python](https://img.shields.io/badge/made%20with-python-blue?logo=python&logoColor=ffffff)](https://www.python.org/)
[![Python](https://img.shields.io/badge/pypi-neatplan-blue?logo=pypi&logoColor=ffffff)](https://pypi.org/project/neatplan/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![CodeFactor](https://www.codefactor.io/repository/github/c0m4r/neatplan/badge)](https://www.codefactor.io/repository/github/c0m4r/neatplan)

nginx-style network configuration

## Dependencies

* Python >= 3.6
* [crossplane](https://github.com/nginxinc/crossplane)
* iproute2
* dhclient (optional)

## Features

- Boot-time configuration
- IPv4/IPv6 support
- Loopback interface up by default (`ip link set lo up`)
- Set link up for a given interface (`ip link set <iface> up`)
- Set IP address for a given interface (`ip addr add <ip/mask> dev <iface>`)
- Set IP route for a given interface (`ip ro add <ip> dev <iface>`)
- Set default IP route for a given interface (`ip ro add default via <ip> dev <iface>`)
- Set via IP route for a given interface (`ip ro add <ip> via <ip> dev <iface>`)
- Set nameservers (/etc/resolv.conf)
- DHCP configuration (dhclient)
- Firewall configuration (`iptables-restore`, `ip6tables-restore`)
- Custom commands to run before and after
- Configured interfaces are being stored in /run/neatplan

## Installation

### PyPI

```
pip install neatplan
```

### Alpine Linux

```bash
cd /opt
git clone https://github.com/c0m4r/neatplan.git
cd neatplan
cp etc/init.d/neatplan /etc/init.d/
cp -r etc/neatplan /etc/
rc-update del networking boot
rc-update add neatplan boot
```

## Configuration

Sample config: `/etc/neatplan/default.conf`

```nginx
network {
    backend iproute2;
    before {
        command "touch /tmp/neatplan";
    }
    firewall {
        iptables /etc/iptables/iptables.rules;
        ip6tables /etc/iptables/ip6tables.rules;
    }
    ethernet {
        eth0 {
            dhcp4 {
                enable true;
            }
            dhcp6 {
                enable false;
            }
            addresses {
                address fe80:ffff:eeee:dddd::1/64;
                address fe80:ffff:eeee:dddd::2/64;
                address 192.168.0.10;
                address 192.168.100.50/24;
            }
            routes {
                route fe80::1 default;
                route 192.168.0.1;
                route 1.1.1.1 via 192.168.0.1;
            }
        }
    }
    dns {
        nameserver 2606:4700:4700::1111;
        nameserver 2606:4700:4700::1001;
    }
    after {
        command "echo I\'m so custom, wow";
        command "ip link add link eth0 name eth0.1337 type vlan id 1337";
    }
}
```

## Documentation

### Contexts

| name | context | description | 
| --- | --- | --- |
| network | | root of network configuration |
| before | network | list of commands to run before network configuration |
| firewall | network | firewall configuration |
| ethernet | network | ethernet configuration |
| \<iface\> | network &rarr; ethernet | network interface configuration |
| dhcp4 | network &rarr; ethernet &rarr; \<iface\> | DHCP v4 settings |
| dhcp6 | network &rarr; ethernet &rarr; \<iface\> | DHCP v6 settings |
| addresses | network &rarr; ethernet &rarr; \<iface\> | IP addresses configuration |
| routes | network &rarr; ethernet &rarr; \<iface\> | IP routes configuration |
| dns | network | list of nameservers |
| before | network | list of commands to run after network configuration |

### Directives

| name | context | syntax | description |
| --- | --- | --- | --- |
| backend | network | `backend <name>;` | IP configuration backend |
| command | before, after | `command "<command> <args>";` | Custom shell command |
| iptables | firewall | `iptables <filepath>;` | Path to iptables rules |
| ip6tables | firewall | `ip6tables <filepath>;` | Path to ip6tables rules |
| enable | dhcp4, dhcp6 | `option true \| false;` | Enable or disable option |
| address | \<iface\> | `address <ip/mask>;` | IPv4 or IPv6 address |
| route | \<iface\> | `route <ip> [default \| via <ip>];` | IP route |
| nameserver | dns | `nameserver <ip>;` | Nameserver address |

## License

```
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
```

## Funding

If you found this script helpful, please consider [making a donation](https://en.wosp.org.pl/fundacja/jak-wspierac-wosp/wesprzyj-online) to a charity on my behalf. Thank you.
