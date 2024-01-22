# neatplan

nginx-style network configuration

## Dependencies

Python >= 3.6 | iproute2 | [crossplane](https://github.com/nginxinc/crossplane)

## Features

So far:

- Set link up (`ip link set <iface> up`)
- Set IP address for a given interface (`ip addr add <ip/mask> dev <iface>`)
- Set default IP route for a given interface (`ip ro add default via <ip> dev <iface>`)
- Set nameservers (/etc/resolv.conf)

## Installation

### Alpine Linux

```
cd /opt
git clone https://github.com/c0m4r/neatplan.git
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
    ethernet {
        eth0 {
            addresses {
                address fe80:ffff:eeee:dddd::1/64;
                address fe80:ffff:eeee:dddd::2/64;
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
