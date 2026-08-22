# Project Scope

## Fictional business scenario

LeanOps Lab represents a small business with limited IT staffing, inconsistent network documentation, and services that may remain enabled after their business purpose has ended. The lab treats each improvement as a controlled change that must preserve required functions.

## Initial milestone

The first milestone used the smallest viable environment:

- One Windows host used as the test and administrative workstation
- One Ubuntu Server virtual machine
- One VirtualBox NAT connection for controlled outbound updates
- One VirtualBox host-only network for isolated lab traffic

The initial milestone intentionally excluded dashboards, automation, virtual routing, multiple network segments, and publicly exposed services. Later PDCA cycles may add controlled automation when it solves an observed problem and includes validation and rollback.

## Current scope

- System, asset, and service inventory
- Basic IPv4 connectivity and routing
- Internal socket inspection and external scanning of the owned lab VM
- SSH authentication and host-firewall controls
- Protected configuration backup and isolated restoration
- Repeatable server health checks and scheduled monitoring
- Health-event processing, condition state, recovery records, and evidence thresholds
- Grouped authenticated SMTP notifications for alert and recovery transitions
- Notification duplicate suppression, protected delivery state, and retry after delivery failure
- Bounded health, notification, and raw-evidence retention
- Controlled failure testing and incident response
- Rollback planning and VirtualBox snapshots
- Repeatable runbooks and sanitized technical evidence
- PDCA records, lessons learned, and standard-work updates

## Out of scope

- Publicly exposed services
- Scanning devices outside the owned lab
- Exploitation or intentionally vulnerable public services
- Production credentials or personal data
- A production monitoring or alerting platform
- Claims that lab work represents professional IT employment

Future dashboards, additional network segments, centralized logging, or production-scale alerting require a separate PDCA cycle with a defined problem, success criteria, risk controls, and rollback plan.

## Safety boundaries

- Intentionally insecure configurations must remain inside the isolated virtual lab.
- NAT port forwarding is not configured.
- Tests target only the owned Ubuntu lab VM and approved administration workstation.
- Passwords, keys, tokens, fingerprints, real home-network details, and personal identifiers are excluded from public documentation.
- Specific isolated-lab addresses may appear only when necessary to reproduce or explain a technical control.
- Risky changes require a rollback method before execution.

## Accuracy statement

Documentation distinguishes planned work from actions personally performed and results actually observed. Manufacturing experience with PDCA, standardized work, troubleshooting, and corrective action is applied as transferable process knowledge. The lab is not presented as professional IT employment.
