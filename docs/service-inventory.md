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
| 53 | TCP/UDP | Loopback only | `systemd-resolved` | Not exposed | Supporting local DNS service |
| 68 | UDP | NAT interface | `systemd-networkd` DHCP client | Not evaluated as a listening server | Supporting NAT address assignment on `enp0s3` |
| 323 | UDP | Loopback only | `chronyd` control socket | Not exposed | Supporting local time service |

The initial Nmap scan found only TCP port 22 open among the 1,000 commonly scanned TCP ports.

## Temporary simulated legacy condition

Apache 2.4.66 was installed from Ubuntu's official package repositories to simulate an inherited service with no current business requirement.

| Port | Service | Internal observation | External observation |
|---:|---|---|---|
| 22/TCP | OpenSSH | Listening | Open |
| 80/TCP | Apache HTTP | Listening on `*:80` | Open, HTTP `200 OK` |

## Improved service standard

Apache remains installed for simple rollback, but it is stopped and disabled.

| Port | Required state | Verified state |
|---:|---|---|
| 22/TCP | Open | Open after change and reboot |
| 80/TCP | Closed | Closed after change and reboot |

The final Cycle 03 Nmap scan against `192.168.244.10` found TCP port 22 open and 999 commonly scanned TCP ports closed.

## SSH authentication standard

| Setting | Verified state |
|---|---|
| Public-key authentication | Enabled |
| Password authentication | Disabled |
| Keyboard-interactive authentication | Disabled |
| PAM | Enabled for account and session handling |
| Remote access test | Key-only login successful after reboot |
| Negative test | Password-only login rejected |

Authentication hardening changed how SSH validates users but did not add another listening service or port.

## Host firewall standard

| Control | Verified state |
|---|---|
| UFW status | Active and enabled at startup |
| Default incoming policy | Deny |
| Default outgoing policy | Allow |
| Routed traffic | Disabled |
| SSH rule | Allow TCP 22 from `192.168.244.1` only |
| Nmap from approved workstation | TCP 22 open; 999 commonly scanned TCP ports filtered |
| Outbound routing | Successful |
| DNS resolution | Successful after reboot |

Before UFW was enabled, the 999 non-listening commonly scanned TCP ports were reported as closed with resets. With UFW active, the same ports were reported as filtered with no response. The approved SSH path remained available.

## Configuration recovery standard

The backup process does not add a listening service or network port.

| Control | Verified state |
|---|---|
| Source definition | Root-controlled nine-file allowlist |
| Backup destination | `/var/backups/leanops` with mode `700` |
| Backup artifacts | Archive, manifest, and SHA-256 checksum with mode `600` |
| Scope validation | Approved regular files only; symbolic-link sources rejected |
| Archive inspection | Exactly nine expected paths listed |
| Isolated restore | Nine byte-for-byte content matches |
| Restored metadata | Nine ownership and permission matches |
| Off-VM verification | SHA-256 comparison passed on Windows |
| Post-reboot state | Script, allowlist, protected archive, SSH, UFW, networking, and DNS verified |

This is a selected-configuration recovery control, not a complete server or disaster-recovery backup.

## Operational health-check standard

The health check does not add a listening service or scheduled background process. It runs on demand with `sudo`.

| Check | Required interpretation |
|---|---|
| SSH | Active, otherwise FAIL |
| Apache | Inactive, otherwise FAIL |
| UFW | Active with documented defaults and restricted TCP 22 rule, otherwise FAIL |
| Host-only address | `192.168.244.10/24` present on `enp0s8`, otherwise FAIL |
| Default route | Present through NAT interface `enp0s3`, otherwise FAIL |
| Internet and DNS | Reachable and resolvable, otherwise FAIL |
| Root filesystem | WARN at 80%; FAIL at 90% |
| Available memory | WARN below 20%; FAIL below 10% |
| Package updates | WARN when the current APT cache lists updates |
| Latest backup | SHA-256 verification required, otherwise FAIL |

Exit code `0` means all checks passed, `1` means at least one warning and no failures, and `2` means at least one failure.

## Incident-evidence collection standard

The collector runs on demand and does not add a listening port or scheduled service.

| Control | Verified state |
|---|---|
| Output directory | `/var/log/leanops-incidents`, mode `700 root:root` |
| Collector | `/usr/local/sbin/leanops-incident-collect`, mode `700 root:root` |
| Evidence scope | 12 defined text sources plus one manifest |
| Journal window | SSH and Apache events from the previous 30 minutes |
| Authentication scope | Up to 100 recent `sshd` log entries |
| UFW scope | Up to 100 recent UFW log entries |
| Sanitization | MAC addresses and UFW `SRC` and `DST` fields replaced |
| Integrity | SHA-256 checksum for every archive |
| Healthy collection | 12 PASS, 1 WARN, 0 FAIL embedded in package |
| Controlled incident | Apache failure, health exit code 2, active service state, and start event preserved |
| Recovery | EXIT trap restored Apache to inactive |
| Off-VM verification | Configuration and controlled-incident packages passed on Windows |

The collector supports local incident triage and evidence preservation. It is not centralized logging, monitoring, or a security information and event management platform.
