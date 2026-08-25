# Service Inventory

## Initial clean baseline

Internal inspection used:

```bash
sudo ss -lntup
```

External inspection used from Windows:

```powershell
nmap -sT -sV -Pn <server-host-only-ip>
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

The final Cycle 03 Nmap scan against the server's host-only address found TCP port 22 open and 999 commonly scanned TCP ports closed.

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
| SSH rule | Allow TCP 22 from the approved host-only administration address only |
| Nmap from approved workstation | TCP 22 open; 999 commonly scanned TCP ports filtered |
| Outbound routing | Successful |
| DNS resolution | Successful after reboot |

Before UFW was enabled, the 999 non-listening commonly scanned TCP ports were reported as closed with resets. With UFW active, the same ports were reported as filtered with no response. The approved SSH path remained available.

## Role-based file-service standard

Samba adds one inbound service on the isolated host-only network. It is not exposed through NAT or router port forwarding.

| Control | Verified state |
|---|---|
| Service | `smbd`, enabled and active |
| Port | TCP 445 only |
| Binding | Loopback and `enp0s8` |
| Firewall | TCP 445 on `enp0s8` from the approved Windows host only |
| Protocol | SMB2 minimum |
| Unneeded functions | NetBIOS, printing, spooler, DNS proxy, and guest access disabled |
| Company access | `@leanops-users` |
| Operations access | `@operations` |
| Management access | `@management` |
| Private access | Authenticated `%U` only |
| Collaborative modes | `0660` files and `02770` directories |
| Private modes | `0600` files and `0700` directories |
| Unauthorized tests | Department and cross-user private access denied |
| Windows validation | Approved file creation and Linux ownership/modes passed |

## Scheduled share-data backup standard

The share-data backup adds no listening port.

| Control | Verified state |
|---|---|
| Script | `/usr/local/sbin/leanops-share-backup`, `700 root:root` |
| Service | `leanops-share-backup.service`, oneshot, `644 root:root` |
| Timer | `leanops-share-backup.timer`, enabled and active |
| Schedule | Daily 02:30, persistent, randomized delay up to 5 minutes |
| Locking | Non-blocking `flock` prevents overlap |
| Consistency boundary | Active Samba and health timer paused, then restored through EXIT trap |
| Backup destination | `/var/backups/leanops-shares`, `700 root:root` |
| Artifacts | Archive, manifest, and checksum, `600 root:root` |
| Archive metadata | ACLs, extended attributes, and numeric ownership |
| Integrity | Archive listing plus SHA-256 sidecar |
| Retention | Newest 30 backup sets |
| Isolated restore | Passed |
| Off-VM verification | Windows SHA-256 comparison passed |
| Recovery coverage | Script, service, timer, and Samba configuration included in the 21-source configuration backup |

## Configuration recovery standard

The backup process does not add a listening service or network port.

| Control | Verified state |
|---|---|
| Source definition | Root-controlled twenty-one-file allowlist |
| Backup destination | `/var/backups/leanops` with mode `700` |
| Backup artifacts | Archive, manifest, and SHA-256 checksum with mode `600` |
| Scope validation | Approved regular files only; symbolic-link sources rejected |
| Archive inspection | Exactly twenty-one expected paths listed |
| Isolated restore | Twenty-one byte-for-byte content matches |
| Restored metadata | Twenty-one ownership and permission matches |
| Off-VM verification | SHA-256 comparison passed on Windows |
| Post-reboot state | Script, allowlist, protected archive, SSH, UFW, networking, DNS, Samba, and both timers verified |

This is a selected-configuration recovery control, not a complete server or disaster-recovery backup.

## Operational health-check standard

The health check does not add a listening network service. It can run on demand with `sudo` or through the scheduled systemd service and timer.

| Check | Required interpretation |
|---|---|
| SSH | Active, otherwise FAIL |
| Apache | Inactive, otherwise FAIL |
| UFW | Active with documented defaults and restricted TCP 22 rule, otherwise FAIL |
| Host-only address | Documented static address present on `enp0s8`, otherwise FAIL |
| Default route | Present through NAT interface `enp0s3`, otherwise FAIL |
| Internet and DNS | Reachable and resolvable, otherwise FAIL |
| Root filesystem | WARN at 80%; FAIL at 90% |
| Available memory | WARN below 20%; FAIL below 10% |
| Package updates | WARN when the current APT cache lists updates |
| Latest backup | SHA-256 verification required, otherwise FAIL |

Exit code `0` means all checks passed, `1` means at least one warning and no failures, and `2` means at least one failure.

## Scheduled health-monitoring standard

The health check remains available on demand and also runs through a root-owned systemd oneshot service. A persistent timer schedules recurring execution without adding a listening network port.

| Control | Verified state |
|---|---|
| Service | `leanops-health-monitor.service`, oneshot, `644 root:root` |
| Timer | `leanops-health-monitor.timer`, enabled and active |
| Schedule | Five minutes after boot and approximately every 15 minutes |
| Warning handling | Exit code `1` accepted as a successful service run |
| Health failure handling | Exit code `2` is accepted after the processor records and escalates the condition |
| Pipeline failure handling | Exit code `3` retains a failed service state |
| Logging | Standard output and errors recorded in the system journal |
| Hardening | `NoNewPrivileges`, `PrivateTmp`, `ProtectHome`, and `ProtectSystem=full` |
| Controlled test | Apache failure detected; evidence preserved; EXIT trap restored Apache and timer |
| Reboot verification | Timer remained enabled and active; automatic health run completed |
| Recovery coverage | Service and timer included in the verified 21-source configuration backup |

## Health-event processing standard

The event handler and processor add no listening service or network port.

| Control | Verified state |
|---|---|
| Handler | `/usr/local/sbin/leanops-health-event-handler`, `700 root:root` |
| Processor | `/usr/local/sbin/leanops-health-event-processor`, `700 root:root` |
| Locking | Exclusive lock with a 30-second maximum wait |
| State | `/var/lib/leanops-health-monitor/condition-state.json`, `600 root:root` |
| Event history | `/var/log/leanops-health-events/health-events.tsv`, `600 root:root` |
| Healthy runs | Not added to the health-event log |
| Recovery | Active condition removed and one recovery record written |
| Warning threshold | Evidence due on consecutive occurrence 4 |
| Failure threshold | Evidence due on occurrence 1 |
| Duplicate control | Evidence latch retained until recovery |
| Event retention | Daily rotation, up to 180 rotations, maximum age 180 days |
| Raw evidence retention | Files under `/var/log/leanops-incidents` cleaned after 180 days |

Parsing, counting, integrated collection, duplicate suppression, recovery, permissions, live service execution, 21-source backup restoration, and retention passed.

## Controlled notification standard

The notifier adds no listening service or inbound port. It submits outbound mail through an authenticated TLS SMTP relay only when the processor queues an alert or recovery transition.

| Control | Verified state |
|---|---|
| Notifier | `/usr/local/sbin/leanops-health-notifier`, `700 root:root` |
| SMTP configuration | `/etc/leanops-health-notify.conf`, `600 root:root`, excluded from Git and backups |
| Transport | Authenticated TLS submission through `msmtp` |
| Grouping | One message per cycle containing each distinct queued condition |
| Warning alert | Queued on consecutive occurrence 4 |
| Failure alert | Queued immediately on occurrence 1 |
| Recovery alert | Queued once when an active condition returns to normal |
| Duplicate control | No repeated alert while the same condition remains active |
| Delivery failure | Pending state retained for a later retry; pipeline error remains visible |
| Notification state | `/var/lib/leanops-health-monitor/notification-state.json`, `600 root:root` |
| Delivery history | `/var/log/leanops-health-events/notification-events.tsv`, `600 root:root` |
| Retention | Notification events rotate daily and expire after 180 days |
| Recovery coverage | Notifier and local AppArmor policy included in the verified 21-source backup; SMTP secret excluded |

Six transition tests and live SMTP delivery verified threshold alerts, immediate failures, grouped distinct conditions, duplicate suppression, recovery messages, and retry behavior.

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
