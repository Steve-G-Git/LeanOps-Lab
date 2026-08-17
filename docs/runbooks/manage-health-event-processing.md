# Runbook: Manage Health Event Processing

## Purpose

Inspect, verify, troubleshoot, and recover the LeanOps health-event handler, condition processor, event history, evidence thresholds, and retention policies.

## Preconditions

- Key-authenticated SSH or VirtualBox console access
- Root access through `sudo`
- `leanops-health-event-handler` and `leanops-health-event-processor` installed with mode `700 root:root`
- State and event directories installed with mode `700 root:root`
- No controlled failure in progress unless the timer is paused and rollback is guaranteed

## 1. Verify the execution chain

~~~bash
systemctl cat leanops-health-monitor.service \
| grep -E '^(ExecStart|SuccessExitStatus)'

systemctl is-active leanops-health-monitor.timer
systemctl --failed --no-pager
~~~

Required service values:

~~~text
ExecStart=/usr/local/sbin/leanops-health-event-handler
SuccessExitStatus=1 2
~~~

Code `3` must not appear in `SuccessExitStatus`.

## 2. Inspect current condition state

~~~bash
sudo python3 -m json.tool \
/var/lib/leanops-health-monitor/condition-state.json
~~~

Review each active condition's severity, consecutive count, first and last observation, last message, and evidence latch. Do not edit the live JSON manually.

## 3. Review event history

~~~bash
sudo tail -n 20 \
/var/log/leanops-health-events/health-events.tsv
~~~

Expected event types include `OBSERVED`, `RECOVERED`, and `EVIDENCE_COLLECTED`. Ordinary healthy runs are intentionally absent; use the system journal to verify them.

## 4. Interpret results

| Code | Meaning | Response |
|---:|---|---|
| `0` | Healthy run processed | No health-event record unless a prior condition recovered |
| `1` | Warning processed | Review count and scheduled follow-up |
| `2` | Health failure processed | Confirm immediate evidence and investigate the condition |
| `3` | Monitoring pipeline failed | Inspect locking, parsing, state, log, and collector errors immediately |

## 5. Verify permissions

~~~bash
sudo stat -c '%a %U:%G %n' \
/usr/local/sbin/leanops-health-event-handler \
/usr/local/sbin/leanops-health-event-processor \
/var/lib/leanops-health-monitor \
/var/log/leanops-health-events \
/var/lib/leanops-health-monitor/condition-state.json \
/var/log/leanops-health-events/health-events.tsv
~~~

Scripts and directories require `700 root:root`. State and event files require `600 root:root`.

## 6. Verify retention

~~~bash
sudo logrotate --debug \
/etc/logrotate.d/leanops-health-events

sudo systemd-tmpfiles --clean \
--prefix=/var/log/leanops-incidents
~~~

Debug output should report daily rotation, 180 retained rotations, and 180-day maximum age. A successful tmpfiles cleanup may produce no output.

## 7. Complete the remaining evidence-trigger test

Prefer natural scheduled occurrences. If a controlled failure is required, use the isolated lab only, pause the timer, and guarantee rollback before changing service state.

Confirm one evidence package at the applicable threshold, set `evidence_collected` to `true`, then run one additional occurrence and confirm no duplicate package. Restore the healthy condition and verify a `RECOVERED` event and empty active state.

## 8. Expand configuration-backup coverage

Before closing Cycle 10, add the handler, processor, modified service unit, logrotate policy, and tmpfiles policy to the root-controlled configuration-backup allowlist. Create a fresh backup and verify its checksum, exact source scope, ownership, permissions, and isolated restoration before treating the new components as recoverable.

Do not mark this step complete from allowlist membership alone. The resulting archive and restore test must both pass.

## 9. Troubleshoot pipeline code 3

~~~bash
systemctl status leanops-health-monitor.service --no-pager
sudo journalctl -u leanops-health-monitor.service -n 100 --no-pager
sudo bash -n /usr/local/sbin/leanops-health-event-handler
sudo python3 -m py_compile \
/usr/local/sbin/leanops-health-event-processor
~~~

Check the first reported handler or processor error. Do not delete state or event history as a first response.

## Rollback

1. Disable the timer if the pipeline is repeatedly failing.
2. Preserve the current journal, state file, and event log.
3. Restore the exact pre-change copy for the affected component.
4. Restore the pre-handler systemd service if bypassing the new pipeline.
5. Run syntax checks and `systemctl daemon-reload` before re-enabling the timer.
6. Verify the direct health check, service result, timer state, and failed-unit list.

If file-level recovery is unclear, restore snapshot `Health Monitor Retention Verified - 2026-08-17` for the current verified implementation or `20-PDCA10-PreHealthEventHandling` to return to the Cycle 09 baseline.
