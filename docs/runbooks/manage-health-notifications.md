# Runbook: Manage Health Notifications

## Purpose

Verify, operate, troubleshoot, and recover the LeanOps health-notification path without exposing credentials or weakening the local health and evidence record.

## Preconditions

- Key-authenticated SSH or local console access
- Root access through `sudo`
- Handler, processor, and notifier installed as `0700 root:root`
- SMTP configuration, notification state, and history stored as `0600 root:root`
- No controlled failure in progress unless the timer is paused and rollback is guaranteed

## 1. Verify the execution chain

~~~bash
systemctl cat leanops-health-monitor.service \
| grep -E '^(ExecStart|SuccessExitStatus)'

systemctl is-enabled leanops-health-monitor.timer
systemctl is-active leanops-health-monitor.timer
systemctl --failed --no-pager
~~~

Expected health codes `1` and `2` may be accepted by systemd. Pipeline code `3` must remain a service failure.

## 2. Inspect state

~~~bash
sudo python3 -m json.tool \
/var/lib/leanops-health-monitor/condition-state.json

sudo python3 -m json.tool \
/var/lib/leanops-health-monitor/notification-state.json
~~~

Do not edit live JSON manually. Delivered conditions belong in notified state; failed deliveries remain pending.

## 3. Review notification history

~~~bash
sudo tail -n 20 \
/var/log/leanops-health-events/notification-events.tsv
~~~

Compare notification transitions with the health-event history when investigating a missing or unexpected email.

## 4. Expected behavior

| Condition | Expected behavior |
|---|---|
| Warning observations 1-3 | Tally only |
| Warning observation 4 | Evidence and one queued alert |
| Continued warning | Tally without duplicate email |
| First failure | Immediate evidence and queued alert |
| Multiple conditions | One email with separate condition sections |
| Recovery after alert | One recovery notification |
| Alert and recovery before delivery | One `ALERT_RECOVERED` notification |
| SMTP failure | Pending work retained for the next timer run |

## 5. Verify permissions without exposing secrets

~~~bash
sudo stat -c '%a %U:%G %n' \
/usr/local/sbin/leanops-health-event-handler \
/usr/local/sbin/leanops-health-event-processor \
/usr/local/sbin/leanops-health-notifier \
/etc/leanops-health-notify.conf \
/var/lib/leanops-health-monitor/notification-state.json \
/var/log/leanops-health-events/notification-events.tsv
~~~

Never print the SMTP configuration or copy it into public evidence.

## 6. Verify service and suppression

~~~bash
systemctl show leanops-health-monitor.service \
-p Result -p ExecMainCode -p ExecMainStatus

sudo journalctl -u leanops-health-monitor.service \
-n 60 --no-pager

sudo wc -l \
/var/log/leanops-health-events/notification-events.tsv
~~~

A repeated condition that was already delivered must not create another queued or sent transition.

## 7. Verify retention

~~~bash
sudo logrotate --debug \
/etc/logrotate.d/leanops-health-events

sudo systemctl reset-failed logrotate.service
sudo systemctl start logrotate.service

systemctl show logrotate.service \
-p Result -p ExecMainStatus
~~~

Both TSV paths must appear before one opening brace. Expected policy: daily, 180 rotations, 180-day maximum age, compression, and `0600 root:root` new files.

## 8. Troubleshoot delivery failure

1. Confirm health state and evidence were saved.
2. Confirm the pending notification remains in state.
3. Review the first notifier or SMTP journal error.
4. Verify DNS and outbound access without printing credentials.
5. Verify configuration ownership and mode.
6. Validate processor and notifier syntax.
7. Correct the cause and allow the next cycle to retry.
8. Confirm one delivery and an empty pending queue.

Do not delete pending state merely to clear an error.

## 9. Cross-platform staging check

~~~bash
file bin/leanops-health-event-handler
file bin/leanops-health-event-processor
file bin/leanops-health-notifier
file logrotate/leanops-health-events
~~~

Run Bash, Python, systemd, and logrotate validation after transfer. Cycle 12 repository files require LF endings.

## 10. Backup boundary

Back up the notifier and other non-secret protected components. Do not add `/etc/leanops-health-notify.conf` because it contains an SMTP credential. Create a fresh backup, verify its checksum, restore it in isolation, and compare content and metadata.

## Rollback

1. Stop the timer.
2. Preserve journals, health state, notification state, and event logs.
3. Restore the pre-change files from `/root/leanops-cycle12-rollback`.
4. Remove the notifier only after preserving pending state needed for investigation.
5. Run syntax checks and `systemctl daemon-reload`.
6. Start the timer and verify the health check, service, timer, and failed-unit list.

If file-level recovery is unclear, restore snapshot `22-PDCA12-PreEmailNotifications`.
