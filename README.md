# neatplan

[![Python](https://img.shields.io/badge/made%20with-python-blue?logo=python&logoColor=ffffff)](https://www.python.org/)
[![Python](https://img.shields.io/badge/pypi-neatplan-blue?logo=pypi&logoColor=ffffff)](https://pypi.org/project/neatplan/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![CodeFactor](https://www.codefactor.io/repository/github/c0m4r/neatplan/badge)](https://www.codefactor.io/repository/github/c0m4r/neatplan)

nginx-style network configuration

...pretty neat, huh?

Why, for the love of integrated circuits why you ask? Because I can.

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
- Custom commands to run before and after for advanced and custom configuration
- Configured interfaces are being stored in `/run/neatplan`

## Installation

Neatplan is intended for people who know what they are doing, 
or at least for those aware that this may result 
in the loss of access to the server over the network. 
If you're afraid of breaking things, pick something else. 
Although, returning to the previous network configuration method is trivial 
because neatplan does not introduce any invasive changes to the system. 
But before you start destroying your network configuration, 
however enjoyable it is, make sure you have access to some kind 
of remote (or local) console that will allow you to debug without direct SSH access.

All the scripts must be run with root privileges, 
as it is necessary to interact with network configuration.

### PyPI

```bash
pip install neatplan
```

### Github

```bash
git clone https://github.com/c0m4r/neatplan.git /opt/neatplan
cd /opt/neatplan
./deploy.sh
```

The script will:

* create the Python venv
* create a symlink to the wrapper in `/usr/local/bin/neatplan`
* copy the respective init script if it's available
* create a config file in `/etc/neatplan/default.conf`

#### Alpine Linux

To replace networking with neatplan at boot time:

```bash
rc-update del networking boot
rc-update add neatplan boot
```

#### Void Linux

To start neatplan as a runit service:

```bash
ln -s /etc/sv/neatplan /var/service/
```

## Usage

Simply running `neatplan` will immediately set the network using default config (if present).

### Dry-run

If you would like to test your configuration before actually executing it, use the dry-run mode:

```
neatplan --dry-run
```

Neatplan will only print a parsed configuration, so you can verify it before execution.

### Custom config path

You can also point neatplan to a different config file using `--config` option:

```
neatplan --config /path/to/file.conf
```

### Help

Run with `--help` to see this help message:

```
usage: neatplan [-h] [-c CONFIG] [-v] [--dry-run]

nginx-style network configuration

options:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Config file absolute path
  -v, --version         Show version and exit
  --dry-run             Don't execute, only show what you've got
```

## Configuration

#### Config path

`/etc/neatplan/default.conf`

#### Quick example

* IPv4 using DHCP
* Static IPv6 address
* IPv6-only CloudFlare DNS

```nginx
network {
    backend iproute2;
    ethernet {
        eth0 {
            dhcp4 {
                enable true;
            }
            addresses {
                address fe80:ffff:eeee:dddd::1/64;
            }
            routes {
                route fe80::1 default;
            }
        }
    }
    dns {
        nameserver 2606:4700:4700::1111;
        nameserver 2606:4700:4700::1001;
    }
}
```

Note that 

#### Full feature showcase

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

Note that `dhcp6 { enable: false; }` isn't actually necessary. It's not being run by default if not enabled explicitly.

Additionally, the ability to execute custom commands within the `before` and `after` contexts 
can be used to run arbitrary code. Make sure only root has write access to the configuration.

## Writing init scripts

* Neatplan saves all configured interfaces (including `lo`) at boot time to `/run/neatplan`.
  You can iterate through them or do whatever the hell you want with that information.
* When starting neatplan make sure it is started before services that rely on the network,
  preferably within boot runlevel (thank you captain obvious)
* If you're about to use IPv6 you have to make sure that
  [tentative states](https://www.the-art-of-web.com/system/ipv6-dad-tentative/) are gone before ending a start job
* When stopping neatplan make sure to `rm /run/neatplan` at the end.
* Handle Python venv before executing neatplan with `. /opt/neatplan/.venv/bin/activate`
  or set the `PATH=/opt/neatplan/.venv:$PATH`.

See example [OpenRC](https://github.com/c0m4r/neatplan/blob/main/etc/init.d/neatplan) 
and [runit](https://github.com/c0m4r/neatplan/blob/main/etc/sv/neatplan/run) init scripts.

## Documentation

I'm not saying it's the worst documentation I wrote, but it's the worst documentation I wrote.

![image](https://github.com/c0m4r/neatplan/assets/6292788/4aec222e-fe3e-4c11-a896-44b611c8d8d8)

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

![image](https://github.com/c0m4r/neatplan/assets/6292788/74c6156b-ffc9-434c-aeb8-5223ac229880)

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

If you found this software somewhat useful, 
please consider [making a donation](https://en.wosp.org.pl/fundacja/jak-wspierac-wosp/wesprzyj-online) 
to a [charity](https://en.wikipedia.org/wiki/Great_Orchestra_of_Christmas_Charity) on my behalf. 
Thank you.
