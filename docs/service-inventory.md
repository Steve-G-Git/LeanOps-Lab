# Service Inventory

## Initial clean baseline

Internal inspection used:

```bash
sudo ss -lntup
```

External inspection used from Windows:

```powershell
nmap -sT -sV -Pn 192.168.244.10
```

| Port | Protocol | Binding or scope | Process or service | External result | Classification |
|---:|---|---|---|---|---|
| 22 | TCP | All IPv4 and IPv6 interfaces | OpenSSH through systemd socket activation | Open | Required for remote administration |
| 53 | TCP/UDP | Loopback only | `systemd-resolved` | Not exposed | Required local DNS resolver |
| 68 | UDP | NAT interface | `systemd-networkd` DHCP client | Not evaluated as a listening server | Required for NAT address assignment on `enp0s3` |
| 323 | UDP | Loopback only | `chronyd` control socket | Not exposed | Required local time-service control |

The initial Nmap scan found only TCP port 22 open among the 1,000 commonly scanned TCP ports.

## Temporary simulated legacy condition

Apache 2.4.66 was installed from Ubuntu's official package repositories to simulate an inherited service with no current business requirement.

| Port | Service | Internal observation | External observation |
|---:|---|---|---|
| 22/TCP | OpenSSH | Listening | Open |
| 80/TCP | Apache HTTP | Listening on `*:80` | Open, HTTP `200 OK` |

## Improved standard

Apache remains installed for simple rollback, but it is stopped and disabled.

| Port | Required state | Verified state |
|---:|---|---|
| 22/TCP | Open | Open after change and reboot |
| 80/TCP | Closed | Closed after change and reboot |

The final Cycle 02 Nmap scan against `192.168.244.10` found TCP port 22 open and 999 commonly scanned TCP ports closed.
