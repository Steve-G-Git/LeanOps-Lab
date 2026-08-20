# PDCA 12 staged implementation

This directory contains the sanitized, pre-installation implementation for
controlled LeanOps-Lab health notifications.

The code is intentionally isolated on the `pdca-12-email-notifications` branch
until server-side acceptance testing is complete. It contains no email address,
SMTP login, SMTP key, IP address, or live notification configuration.

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

## Promotion boundary

Do not merge this branch into `main` until the controlled acceptance tests pass
on the lab VM. After validation, add sanitized evidence, complete the PDCA 12
record and runbook updates, then review the full branch before merging.
