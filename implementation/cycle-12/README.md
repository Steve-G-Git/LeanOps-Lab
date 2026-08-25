# PDCA 12 notification implementation

This directory contains the sanitized implementation for controlled
LeanOps-Lab health notifications. Server-side acceptance, expanded backup
coverage, isolated restoration, and the final recovery checkpoint passed.

The verified code was reviewed and merged into `main` from the
`pdca-12-email-notifications` branch. It contains no email address, SMTP login, SMTP
key, IP address, or live notification configuration.

## Layout

- `bin/leanops-health-event-handler`: orchestration and exit-code handling
- `bin/leanops-health-event-processor`: condition state, evidence, and queuing
- `bin/leanops-health-notifier`: grouped SMTP delivery and retry state
- `systemd/leanops-health-monitor.service`: hardened oneshot service
- `logrotate/leanops-health-events`: 180-day health and notification log policy
- `tests/test_cycle12_logic.py`: pre-installation state-transition tests

## Controlled behavior

| Condition | Action |
| --- | --- |
| Warning occurrences 1 through 3 | Record only |
| Warning occurrence 4 | Collect evidence and queue one alert |
| Existing warning already above 4 | Queue once if never previously notified |
| Continued warning after delivery | Record without duplicate email |
| Failure occurrence 1 | Collect evidence and queue an immediate alert |
| Recovery after an alert | Queue one recovery message |
| Alert and recovery while SMTP is unavailable | Coalesce as `ALERT_RECOVERED` |
| SMTP failure | Retain pending work for the next timer cycle |
| Processor or health-check error | Attempt an immediate pipeline-error email |

The event processor saves condition state and evidence history before the
notifier attempts SMTP delivery. The SMTP configuration remains only on the VM
at `/etc/leanops-health-notify.conf` with mode `0600 root:root`.

## Acceptance status

Six controlled logic tests, live SMTP delivery, duplicate suppression, retry
retention, protected notification records, service integration, timer
operation, corrected 180-day log rotation, 17-source backup coverage,
SHA-256 verification, and a 17-of-17 isolated restore passed.

## Promotion status

Cycle 12 passed branch review, was merged into `main`, and is closed.
