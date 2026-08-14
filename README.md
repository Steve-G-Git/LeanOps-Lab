# LeanOps Lab: Improving a Small-Business Network with PDCA

LeanOps Lab is a hands-on learning project that applies PDCA and practical Lean methods to a small virtual network. The lab simulates a poorly documented small-business environment, establishes its current condition, makes one controlled improvement at a time, and verifies each result.

This is a self-directed lab project. It does not represent professional employment in networking, cybersecurity, or system administration.

## Current status

**Status: Active development, 7 PDCA cycles completed**

Cycle 07 established a protected incident-evidence collector that preserves limited health, service, firewall, network, resource, package, backup, journal, authentication, and UFW evidence in integrity-checked packages.

## Verified outcomes

| Cycle | Problem | Improvement | Verified result |
|---|---|---|---|
| 01 | Unnecessary HTTP service | Stopped and disabled Apache | Port 80 closed; SSH retained after reboot |
| 02 | Administration address could change | Assigned a static host-only address | Address, SSH, routing, DNS, and NAT persisted |
| 03 | SSH allowed password authentication | Established key authentication and disabled SSH passwords | Key access persisted; password-only access was rejected; port baseline retained |
| 04 | No active host firewall | Enabled UFW with default-deny inbound policy and source-restricted SSH | Approved SSH persisted; 999 other common TCP ports changed from closed to filtered |
| 05 | Recovery depended on VM snapshots | Created a protected, portable configuration backup process | Seven approved files restored byte-for-byte with matching metadata; Ubuntu and Windows checksum tests passed |
| 06 | Server health required separate manual checks | Created a root-controlled health-check script | Normal state returned 12 PASS, 1 WARN, 0 FAIL; controlled Apache failure returned exit code 2 and rolled back safely |
| 07 | Incident evidence required manual collection | Created a sanitized, integrity-checked evidence collector | Healthy and controlled-failure packages verified; Apache failure preserved before automatic rollback; off-VM checks passed |

## Skills demonstrated

- Linux administration
- TCP/IP and service validation
- Nmap and PowerShell testing
- SSH administration
- SSH key-based authentication
- UFW host firewall administration
- Bash backup scripting
- SHA-256 integrity verification
- Isolated configuration restoration
- Backup scope and permission control
- Bash health-check scripting
- Operational thresholds and exit codes
- Controlled failure testing and automatic rollback
- Incident evidence collection
- Journal and authentication-log review
- Evidence sanitization and integrity verification
- VirtualBox networking
- Controlled change management
- Troubleshooting documentation
- PDCA and standardized work

## Lab topology

```mermaid
flowchart LR
    Internet["Internet"] --> NAT["VirtualBox NAT<br/>10.0.2.0/24"]
    NAT --> Server["Ubuntu Server<br/>leanops-server"]
    Windows["Windows host<br/>Test workstation"] <--> HostOnly["VirtualBox host-only network<br/>192.168.244.0/24"]
    HostOnly <--> Server
```

- Adapter 1 uses VirtualBox NAT for controlled outbound updates.
- Adapter 2 uses a host-only network for isolated administration and scanning.
- No router port forwarding or public exposure is configured.
- Proton VPN must be disconnected during current lab tests because it blocks the host-only connection in the observed configuration.

## Repository contents

- [`docs/scope.md`](docs/scope.md): fictional business scenario, boundaries, and safety rules
- [`docs/asset-inventory.md`](docs/asset-inventory.md): current hardware, operating-system, storage, and network inventory
- [`docs/service-inventory.md`](docs/service-inventory.md): internal and externally observed services
- [`docs/pdca/PDCA-01-apache-service-reduction.md`](docs/pdca/PDCA-01-apache-service-reduction.md): complete Plan, Do, Check, Act record
- [`docs/pdca/PDCA-02-static-host-only-address.md`](docs/pdca/PDCA-02-static-host-only-address.md): static-address improvement and verification record
- [`docs/pdca/PDCA-03-ssh-key-authentication.md`](docs/pdca/PDCA-03-ssh-key-authentication.md): key-authentication and SSH-hardening record
- [`docs/pdca/PDCA-04-ufw-host-firewall.md`](docs/pdca/PDCA-04-ufw-host-firewall.md): host-firewall configuration and verification record
- [`docs/pdca/PDCA-05-configuration-backup.md`](docs/pdca/PDCA-05-configuration-backup.md): protected configuration-backup and isolated-restore record
- [`docs/pdca/PDCA-06-server-health-check.md`](docs/pdca/PDCA-06-server-health-check.md): repeatable health check, warning state, controlled failure, and rollback record
- [`docs/pdca/PDCA-07-incident-evidence-collection.md`](docs/pdca/PDCA-07-incident-evidence-collection.md): healthy baseline, controlled incident, evidence sanitization, and verification record
- [`docs/runbooks/verify-host-only-connectivity.md`](docs/runbooks/verify-host-only-connectivity.md): standardized connectivity verification
- [`docs/runbooks/configure-static-host-only-address.md`](docs/runbooks/configure-static-host-only-address.md): repeatable static-address configuration and recovery procedure
- [`docs/runbooks/configure-ssh-key-authentication.md`](docs/runbooks/configure-ssh-key-authentication.md): safe key setup, hardening, verification, and recovery procedure
- [`docs/runbooks/configure-ufw-host-firewall.md`](docs/runbooks/configure-ufw-host-firewall.md): source-restricted firewall setup, testing, and recovery procedure
- [`docs/runbooks/backup-and-restore-configuration.md`](docs/runbooks/backup-and-restore-configuration.md): repeatable backup, integrity verification, isolated restore, and controlled live recovery procedure
- [`docs/runbooks/run-server-health-check.md`](docs/runbooks/run-server-health-check.md): health-check execution, interpretation, escalation, and recovery procedure
- [`docs/runbooks/collect-incident-evidence.md`](docs/runbooks/collect-incident-evidence.md): protected evidence collection, validation, interpretation, export, and cleanup procedure
- [`docs/change-log.md`](docs/change-log.md): chronological record of controlled changes
- [`docs/security-considerations.md`](docs/security-considerations.md): isolation, evidence-sanitization, and remaining risks

## Tools used

- Windows host computer
- Oracle VirtualBox 7.2.2
- Ubuntu Server 26.04 LTS
- OpenSSH
- Apache HTTP Server
- Nmap 7.99 and Npcap 1.87
- PowerShell
- Linux command-line tools including `systemctl`, `ss`, `ip`, `tar`, `sha256sum`, `stat`, `cmp`, `mktemp`, `lsblk`, and `free`

## Evidence policy

Public evidence will be sanitized before it is added. Passwords, authentication material, real home-network information, personal usernames, unique system identifiers, and unnecessary MAC addresses will not be published.

## Next improvement

Cycle 08 will run an end-to-end incident-response drill using the standardized health check, evidence collector, recovery controls, and documented verification steps. Snapshot `15-PDCA07-IncidentEvidenceVerified` is the current recovery point.
