# neatplan

nginx-style network configuration

## Dependencies

Python >= 3.6 | iproute2 | [crossplane](https://github.com/nginxinc/crossplane)

## Usage

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
