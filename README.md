# LeanOps Lab: Improving a Small-Business Network with PDCA

LeanOps Lab is a hands-on learning project that applies PDCA and practical Lean methods to a small virtual network. The lab simulates a poorly documented small-business environment, establishes its current condition, makes one controlled improvement at a time, and verifies each result.

This is a self-directed lab project. It does not represent professional employment in networking, cybersecurity, or system administration.

## Current status

**Status: Active development, 2 PDCA cycles completed**

Cycle 03 is in progress: establish and verify SSH key authentication before considering whether to disable password authentication.

## Verified outcomes

| Cycle | Problem | Improvement | Verified result |
|---|---|---|---|
| 01 | Unnecessary HTTP service | Stopped and disabled Apache | Port 80 closed; SSH retained after reboot |
| 02 | Administration address could change | Assigned a static host-only address | Address, SSH, routing, DNS, and NAT persisted |

## Skills demonstrated

- Linux administration
- TCP/IP and service validation
- Nmap and PowerShell testing
- SSH administration
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
- [`docs/runbooks/verify-host-only-connectivity.md`](docs/runbooks/verify-host-only-connectivity.md): standardized connectivity verification
- [`docs/runbooks/configure-static-host-only-address.md`](docs/runbooks/configure-static-host-only-address.md): repeatable static-address configuration and recovery procedure
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
- Linux command-line tools including `systemctl`, `ss`, `ip`, `lsblk`, and `free`

## Evidence policy

Public evidence will be sanitized before it is added. Passwords, authentication material, real home-network information, personal usernames, unique system identifiers, and unnecessary MAC addresses will not be published.

## Current improvement

Cycle 03 is in progress. The current rollback point is snapshot `05-PDCA02-StaticAddressVerified`. Key authentication will be established and verified in a separate session before any decision is made about password authentication.
