# Project Scope

## Fictional business scenario

LeanOps Lab represents a small business with limited IT staffing, inconsistent network documentation, and services that may remain enabled after their business purpose has ended. The lab treats each improvement as a controlled change that must preserve required functions.

## Initial milestone

The first milestone uses the smallest viable environment:

- One Windows host used as the test and administrative workstation
- One Ubuntu Server virtual machine
- One VirtualBox NAT connection for controlled outbound updates
- One VirtualBox host-only network for isolated lab traffic

## In scope

- System and service inventory
- Basic IPv4 connectivity and routing
- Internal socket inspection
- External port scanning of the owned lab VM
- Controlled service changes
- Rollback planning and VirtualBox snapshots
- Repeatable runbooks
- Sanitized technical evidence
- PDCA records and lessons learned

## Out of scope for the initial milestone

- Publicly exposed services
- Scanning devices outside the owned lab
- Exploitation or intentionally vulnerable public services
- A virtual firewall or router
- Multiple network segments or VLANs
- A Windows 11 VM
- A dashboard or automation script
- Production credentials or personal data

## Safety boundaries

- Intentionally insecure configurations must remain inside the isolated virtual lab.
- NAT port forwarding is not configured.
- Tests target only `192.168.244.10`, the owned Ubuntu lab VM.
- Passwords, keys, tokens, fingerprints, real home-network details, and personal identifiers are excluded from public documentation.
- Risky changes require a rollback method before execution.

## Accuracy statement

Documentation distinguishes planned work from actions personally performed and results actually observed. Manufacturing experience with PDCA, standardized work, troubleshooting, and corrective action is applied as transferable process knowledge. The lab is not presented as professional IT employment.
