# PDCA 09: Scheduled Health Monitoring

## Summary

Cycle 09 converted the manually initiated LeanOps health check into a scheduled control. A root-controlled systemd oneshot service now runs the existing check, while a persistent timer activates it approximately every 15 minutes and five minutes after boot.

The service preserves the health script's three-state result: exit code `0` is all-pass, `1` is warning-only and accepted by systemd as success, and `2` remains a failed unit. A controlled Apache-active test proved failure detection, journal recording, evidence collection, automatic rollback, and recovery. Reboot testing proved that the timer remained enabled, became active, and ran the monitor automatically.

Raw archives and screenshots are not published. They contain protected operational evidence and personal workstation paths. This document uses sanitized results and fictional lab addresses only.

## Plan

### Current condition and problem

The Cycle 06 health check produced useful status and exit codes, but it ran only when an administrator remembered to execute it. Cycles 07 and 08 added evidence collection and incident response, but neither provided recurring health assessment.

### Expected result

- Run the existing health check automatically without changing its logic.
- Record each run in the system journal.
- Treat warning-only exit code `1` as a successful service execution.
- Keep required-state exit code `2` as a failed service.
- Preserve useful service hardening without blocking required UFW inspection.
- Prove timer activation, controlled-failure handling, rollback, reboot persistence, backup coverage, and off-VM evidence integrity.

### Test method

1. Verify a healthy Cycle 08 baseline and confirm no conflicting LeanOps units or timers.
2. Create snapshot `18-PDCA09-PreScheduledMonitoring`.
3. Create and validate the oneshot service before adding the timer.
4. Manually test warning-only handling.
5. Diagnose and correct any sandbox conflict using journal evidence.
6. Create, enable, and inspect the persistent timer.
7. Confirm an automatic timer-triggered run.
8. Introduce a controlled Apache-active failure with an EXIT rollback trap.
9. Preserve and verify the detected failure package.
10. Restore the healthy state.
11. Expand the configuration backup from nine to eleven protected sources.
12. Verify archive integrity, scope, metadata, isolated restoration, and Windows checksums.
13. Reboot and confirm timer persistence and automatic execution.
14. Preserve and verify post-reboot evidence.
15. Create snapshot `19-PDCA09-ScheduledMonitoringComplete`.

### Risks and rollback

- A systemd sandbox could prevent the root health script from reading UFW state.
- Incorrect exit-code handling could hide a failure or treat normal warnings as failure.
- A timer could overlap controlled testing or remain disabled after rollback.
- The timer was stopped during the Apache test and restarted by an EXIT trap.
- Unit files were validated before enablement.
- Snapshot 18 preserved the verified pre-change state.
- Disabling and removing both Cycle 09 units provides file-level rollback.

## Do

### Created the service

The new unit runs the existing script as a root-owned oneshot service:

~~~ini
[Unit]
Description=LeanOps scheduled server health check
Documentation=https://github.com/Steve-G-Git/leanops-lab
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=root
Group=root
ExecStart=/usr/local/sbin/leanops-health-check
SuccessExitStatus=1
StandardOutput=journal
StandardError=journal
SyslogIdentifier=leanops-health-monitor
NoNewPrivileges=true
PrivateTmp=true
ProtectHome=true
ProtectSystem=full
~~~

`SuccessExitStatus=1` accepts the existing warning state without changing the script. Exit code `2` is still a service failure.

### Diagnosed the initial sandbox failure

The first service run returned exit code `2`. Journal output showed all UFW checks failing together. A transient diagnostic unit revealed that `ProtectSystem=strict` made `/run` read-only and prevented UFW from creating its runtime lock.

A file-specific exception was rejected because `/run/ufw.lock` does not exist until UFW runs. A transient test with `ProtectSystem=full` passed. The permanent service changed only that protection level. This retains read-only protection for `/usr`, `/boot`, and `/etc` while permitting required runtime writes under `/run`.

### Created the timer

~~~ini
[Unit]
Description=Run the LeanOps server health check every 15 minutes
Documentation=https://github.com/Steve-G-Git/leanops-lab

[Timer]
OnBootSec=5min
OnUnitActiveSec=15min
AccuracySec=1min
RandomizedDelaySec=30s
Persistent=true
Unit=leanops-health-monitor.service

[Install]
WantedBy=timers.target
~~~

The timer was enabled immediately and showed a future activation.

### Tested a real failure

The timer was paused to prevent overlap. Apache was started intentionally, the monitor was run, and an incident package was collected before an EXIT trap stopped Apache and restarted the timer.

The service recorded `ExecMainStatus=2`, `Result=exit-code`, and a failed state. Evidence independently captured Apache as active, the health failure, and the embedded command exit code.

### Expanded recovery coverage

Both unit files were added to `/etc/leanops-backup-files`, increasing the protected source count from nine to eleven. The resulting configuration package passed SHA-256, exact scope, mode, ownership, isolated content comparison, isolated metadata comparison, and Windows-side integrity tests.

## Check

### Sanitized results

~~~text
MANUAL WARNING-ONLY RUN
health: 12 PASS, 1 WARN, 0 FAIL
health exit code: 1
systemd result: success
service state after run: inactive (dead)

AUTOMATIC TIMER RUN
timer: enabled and active
health: 12 PASS, 1 WARN, 0 FAIL
service completion: success
next activation: scheduled

CONTROLLED APACHE FAILURE
health: 11 PASS, 1 WARN, 1 FAIL
health exit code: 2
systemd result: exit-code
Apache at evidence collection: active
incident archive checksum: OK
automatic rollback: Apache inactive, timer active

RECOVERY
health: 12 PASS, 1 WARN, 0 FAIL
systemd result: success
failed-unit list: clear

BACKUP
protected sources: 11
archive checksum: OK
content comparison: 11 MATCH
metadata comparison: 11 MATCH
Windows checksum: PASS

POST-REBOOT
timer: enabled and active
Apache: inactive
automatic monitoring run: successful
health: 12 PASS, 1 WARN, 0 FAIL
post-reboot evidence checksum: OK
Windows checksum: PASS
~~~

| Verification | Result |
|---|---|
| Service and timer syntax | Passed |
| Unit ownership and mode | `644 root:root` |
| Warning code accepted as success | Passed |
| Failure code retained as failed service | Passed |
| Journal recorded health output | Passed |
| Automatic timer activation | Passed |
| Controlled Apache detection | Passed |
| Automatic rollback | Passed |
| Eleven-source backup and isolated restore | Passed |
| Reboot persistence and automatic post-boot run | Passed |
| Final failed-unit list | Zero units |

The expected result was achieved.

## Act

### Final standard

- Use `leanops-health-monitor.timer` as the normal recurring trigger.
- Keep `leanops-health-monitor.service` as a oneshot unit.
- Preserve `SuccessExitStatus=1`; do not accept exit code `2`.
- Keep `ProtectSystem=full` because UFW requires a runtime lock under `/run`.
- Treat a failed monitor as an investigation trigger, not proof of root cause.
- Inspect the service journal before resetting a failed state.
- Pause the timer during controlled tests and guarantee restart with a cleanup trap.
- Verify Apache inactive, timer active, and no failed units after testing.
- Protect both unit files through the eleven-source configuration backup.
- Verify timer enablement, activation, and a completed monitor run after reboot.
- The completed state is preserved in snapshot `19-PDCA09-ScheduledMonitoringComplete`.

### Standard work and recovery

The tested procedure is documented in [`../runbooks/manage-scheduled-health-monitoring.md`](../runbooks/manage-scheduled-health-monitoring.md).

### Remaining risks

- This is scheduled local monitoring, not centralized alerting.
- A failed service is visible through systemd and the journal but does not notify an administrator remotely.
- Monotonic scheduling is approximate because accuracy and randomized-delay settings intentionally permit variation.
- The monitor relies on the existing health-check targets and cached APT metadata.
- Local journal and evidence files are not tamper-resistant remote records.
