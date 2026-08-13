# Asset Inventory

Observed during the initial lab build on August 12 and 13, 2026.

## Windows host

| Item | Observed value |
|---|---|
| Role | Physical host, test workstation, and SSH client |
| Processor | AMD Ryzen 7 7735HS with Radeon Graphics |
| Host CPU resources | 8 cores, 16 logical processors |
| Virtualization | Enabled |
| Installed RAM | 16 GB DDR5 |
| VM storage | NVMe SSD |
| Hypervisor | Oracle VirtualBox 7.2.2 r170484 |
| Scan utility | Nmap 7.99 with Npcap 1.87 |

## Ubuntu virtual server

| Item | Observed value |
|---|---|
| VirtualBox name | `LeanOpsUbuntuServer` |
| Hostname | `leanops-server` |
| Operating system | Ubuntu Server 26.04 LTS, Resolute Raccoon |
| Architecture | x86-64 |
| Virtual CPU | 2 processing threads |
| Assigned memory | 2048 MB in VirtualBox |
| Memory visible to Ubuntu | Approximately 1.6 GiB |
| Swap | 2 GiB |
| Virtual disk | 30 GB, dynamically allocated |
| Root filesystem | 24 GB ext4 logical volume mounted at `/` |
| Boot filesystem | 2 GB ext4 partition mounted at `/boot` |
| Storage management | LVM |
| Administrative account | `leanopsadmin` |

## Network interfaces

| Interface | Purpose | Observed address | Addressing |
|---|---|---|---|
| `enp0s3` | Controlled outbound access through VirtualBox NAT | `10.0.2.15/24` | DHCP |
| `enp0s8` | Isolated host-only lab traffic | `192.168.244.100/24` | VirtualBox DHCP |
| Windows host-only adapter | Windows endpoint on isolated lab network | `192.168.244.1/24` | Manually configured by VirtualBox |
| VirtualBox DHCP server | Address assignment for host-only guests | `192.168.244.2/24` | VirtualBox configuration |

The host-only DHCP pool is `192.168.244.100` through `192.168.244.200`.

## Routing observations

- Ubuntu's default route uses `10.0.2.2` through `enp0s3`.
- The `192.168.244.0/24` route is directly connected through `enp0s8`.
- The host-only interface has no default gateway.
- Host-only traffic does not replace the NAT route for outbound internet access.
