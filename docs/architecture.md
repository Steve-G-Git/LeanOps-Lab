# Architecture and Control Flow

## Purpose

This document provides the current-state view of LeanOps-Lab after Cycle 13. It explains how the isolated network, security controls, scheduled monitoring, event processing, evidence collection, controlled notification, retention, backup, and recovery controls fit together.

The architecture reflects the verified operational standard through Cycle 13. Notification delivery extends through an authenticated TLS SMTP relay. Samba is limited to the isolated host-only network, and both selected configuration and share data have separate protected recovery paths.

## Network boundary

```mermaid
flowchart LR
    Internet["Internet"] --> NAT["VirtualBox NAT<br/>outbound access only"]
    NAT --> Ubuntu["Ubuntu Server VM"]
    Windows["Windows host<br/>administration and verification"] <--> HostOnly["VirtualBox host-only network"]
    HostOnly <--> Ubuntu
    Ubuntu --> Backup["Protected local backup"]
    Backup -. "verified copy" .-> Windows
```

| Component | Responsibility | Boundary or control |
|---|---|---|
| Windows host | Administration, independent testing, off-VM verification | Connects through the isolated host-only network |
| Ubuntu Server VM | Provides the managed lab system | No router port forwarding or public service exposure |
| NAT adapter | Supplies controlled outbound update access | Not used for inbound administration |
| Host-only adapter | Supplies the approved administration path | Isolated from the physical home network |
| UFW | Enforces default-deny inbound policy | SSH is restricted to the approved administration source |
| OpenSSH | Provides remote administration | Public-key authentication only; passwords disabled |
| Samba | Provides role-based company, department, and private shares | Binds to loopback and `enp0s8`; UFW restricts TCP 445 to the approved Windows host |

## File-service and backup flow

```mermaid
flowchart TD
    Windows["Windows host"] --> Boundary["Host-only network and UFW"]
    Boundary --> Samba["Authenticated Samba service"]
    Samba --> Shares["Company, department, and private shares"]
    Shares --> Backup["Locked daily backup"]
    Backup --> Recovery["Protected archive, manifest, and SHA-256"]
```

- Company access is controlled by `leanops-users`.
- Operations and management access are controlled by their department groups.
- Private access resolves to `/srv/leanops-shares/users/%U`.
- The backup pauses Samba and the health-monitor timer, preserves their prior states, and retains the newest 30 sets.

## Monitoring and evidence flow

```mermaid
flowchart TD
    Timer["systemd timer"] --> Service["oneshot service"]
    Service --> Handler["Bash handler<br/>lock and temporary output"]
    Handler --> Health["Health check<br/>PASS, WARN, FAIL"]
    Health --> Processor["Python processor<br/>validate and classify"]
    Processor --> State["Condition state JSON"]
    Processor --> Events["Health-event TSV"]
    Processor --> Threshold{"Evidence threshold"}
    Threshold -->|"WARN x4"| Collector["Incident collector"]
    Threshold -->|"FAIL x1"| Collector
    Collector --> Package["Manifest, archive, SHA-256"]
    Processor --> Notify{"Notification transition"}
    Notify -->|"Alert or recovery"| Notifier["Python notifier"]
    Notify -->|"Duplicate"| End["Record and exit"]
    Notifier --> SMTP["Authenticated TLS SMTP relay"]
    Notifier --> NotifyState["Notification state and TSV"]
```

### Component responsibilities

| Component | Role | Failure visibility |
|---|---|---|
| `leanops-health-monitor.timer` | Starts the monitoring cycle approximately every 15 minutes | Missing or inactive timer is visible through systemd checks |
| `leanops-health-monitor.service` | Runs one health-monitor cycle | Processing code `3` remains a failed unit |
| `leanops-health-event-handler` | Enforces one-at-a-time execution and controls temporary output | Lock, dependency, or execution errors return code `3` |
| `leanops-health-check` | Tests required services, firewall, networking, resources, updates, and backup integrity | Returns `0`, `1`, or `2` for healthy, warning, or failure state |
| `leanops-health-event-processor` | Validates results, assigns stable condition IDs, updates state, records events, and decides whether evidence is due | Unknown or inconsistent input returns code `3` |
| `leanops-incident-collect` | Collects a bounded, sanitized diagnostic package | Manifest records command exit codes; package receives a checksum |
| `leanops-health-notifier` | Groups alert-worthy transitions, sends one SMTP message, records delivery, and retains failed sends for retry | Delivery failure remains pending and returns a visible pipeline error |
| `smbd` | Serves authenticated company, department, and private shares | Required service state, binding, UFW scope, and access tests make drift visible |
| `leanops-share-backup.timer` | Schedules one persistent daily share-data backup | Inactive or disabled timer is visible through systemd checks |
| `leanops-share-backup.service` | Runs the locked backup as root | Nonzero script exit remains a failed oneshot result |
| `leanops-share-backup` | Pauses writers, records metadata and hashes, creates and verifies the archive, restores prior service states, and enforces 30-set retention | Lock, source, archive, checksum, or cleanup failures return a visible error |

## Condition lifecycle

```mermaid
stateDiagram-v2
    [*] --> Healthy
    Healthy --> Observed: warning or failure
    Observed --> Observed: repeated abnormal result
    Observed --> EvidenceCollected: WARN occurrence 4 or FAIL occurrence 1
    EvidenceCollected --> EvidenceCollected: continued abnormal result
    Observed --> Recovered: normal result
    EvidenceCollected --> Recovered: normal result
    Recovered --> Healthy: state cleared
```

- Every warning and failure is recorded.
- Generic healthy runs remain in the system journal and are not duplicated in the health-event history.
- Warnings collect evidence at the fourth consecutive occurrence.
- Failures collect evidence immediately.
- The evidence latch prevents duplicate packages while the same condition remains active.
- Recovery writes one event, clears the active condition, and resets the latch.

## Protected data and retention

| Data | Location type | Protection | Retention |
|---|---|---|---|
| Active condition state | Root-controlled state directory | Directory `0700`; file `0600`; atomic replacement | Active operational state |
| Health-event history | Root-controlled log directory | Directory `0700`; file `0600` | Daily rotation; maximum 180 days; older rotations compressed |
| Incident packages | Root-controlled incident directory | Directory `0700`; artifacts `0600`; SHA-256 sidecar | Maximum 180 days |
| Notification state and event history | Root-controlled state and log directories | Files `0600`; atomic state replacement; no credential values recorded | Daily log rotation; maximum 180 days |
| SMTP client configuration | Root-controlled configuration file | Mode `0600`; excluded from Git and configuration backups | Active secret-bearing configuration |
| Configuration backups | Root-controlled backup directory | 21 allowlisted non-secret sources; archives, manifests, and checksums `0600` | Retained as controlled recovery artifacts |
| Active share data | Root-controlled share hierarchy | Group authorization, setgid collaborative directories, and `0700` private directories | Active fictional business data |
| Share-data backups | Root-controlled backup directory | Directory `0700`; archives, manifests, and checksums `0600` | Newest 30 backup sets |
| PDCA records and runbooks | Git repository | Sanitized, reviewed, and versioned | Permanent project knowledge |

## Backup and recovery boundary

The configuration backup protects 21 approved non-secret sources, including network, SSH, firewall, monitoring, evidence, notification, Samba, and share-backup automation. The secret-bearing SMTP configuration remains excluded.

A separate share-data backup protects `/srv/leanops-shares`, including ACLs, extended attributes, numeric ownership, filesystem metadata, and per-file hashes. It retains 30 sets and is manually copied to the Windows host after selected closure tests. Raw share-data artifacts are excluded from Git. Neither package is a full-system backup.

Recovery is layered:

1. Use the relevant runbook to diagnose and reverse the specific change.
2. Verify a configuration archive checksum and restore into an isolated directory before considering live replacement.
3. Use the verified off-VM copy if the server copy is unavailable.
4. Restore the appropriate VirtualBox snapshot when configuration-level recovery is insufficient.

## Lean control model

| Lean objective | Technical control |
|---|---|
| See the abnormal condition | Explicit warning, failure, recovery, delivery, and pipeline-error states |
| Avoid reaction to one noisy signal | Four-consecutive-occurrence warning threshold |
| Never hide a defect | Every abnormal occurrence is tallied; pipeline errors fail visibly |
| Avoid repeated waste | Duplicate evidence is suppressed until recovery |
| Preserve learning | Confirmed causes, corrections, runbooks, and PDCA records remain versioned |
| Limit inventory | Raw operational records expire after 180 days |
| Standardize the improved method | Successful changes update runbooks, inventories, security notes, and the README |

## Current limitations

- SMTP notifications depend on an external relay and outbound internet access; local event and retry records preserve visibility when delivery fails.
- The Windows copies are off-VM but are not encrypted, automatically replicated, or versioned off-site.
- The incident collector is bounded and sanitized for observed risks, not a universal data-loss-prevention system.
- Samba identities are local fictional accounts rather than centralized directory identities.
- The share backup briefly pauses Samba and health-monitor scheduling to establish a consistent archive boundary.
- The lab contains one managed server and one administrative workstation, not a production monitoring or file-service fleet.

These limitations define logical future PDCA work. Any next cycle should address a newly observed problem rather than extend the system without evidence of need.
