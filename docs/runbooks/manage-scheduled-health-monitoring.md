# Runbook: Manage Scheduled Health Monitoring

## Purpose

Operate, verify, troubleshoot, and recover the LeanOps systemd health-monitor service and timer.

## Preconditions

- Key-authenticated SSH or VirtualBox console access
- `leanops-health-check` installed at `/usr/local/sbin/leanops-health-check`
- Service and timer owned by `root:root` with mode `644`
- No planned maintenance changing the expected service state

## 1. Verify timer state

~~~bash
printf '%s\n' \
"TIMER_ENABLED=$(systemctl is-enabled leanops-health-monitor.timer)" \
"TIMER_ACTIVE=$(systemctl is-active leanops-health-monitor.timer)"

systemctl list-timers --all leanops-health-monitor.timer --no-pager
~~~

Normal state is `enabled`, `active`, and a future activation in the timer list.

## 2. Run the monitor manually

~~~bash
sudo systemctl start leanops-health-monitor.service
start_rc=$?

systemctl show leanops-health-monitor.service \
--property=Result \
--property=ExecMainStatus \
--property=ActiveState \
--property=SubState

echo "START_EXIT_CODE=$start_rc"
~~~

| Health result | Expected systemd interpretation |
|---|---|
| Exit `0` | Success |
| Exit `1` | Success because warnings are accepted |
| Exit `2` | Failed service |

A successful oneshot returns to `inactive (dead)`. That does not mean monitoring is disabled.

## 3. Review recent runs

~~~bash
sudo journalctl \
-u leanops-health-monitor.service \
--since "1 hour ago" \
--no-pager
~~~

Record the timestamp, summary, warning or failure lines, `Result`, and `ExecMainStatus`.

## 4. Respond to failure

Do not reset the unit before reading its evidence.

~~~bash
systemctl status leanops-health-monitor.service --no-pager
sudo journalctl -u leanops-health-monitor.service -n 80 --no-pager
~~~

Use the reported `FAIL:` line to select the smallest diagnostic. If additional evidence is required:

~~~bash
sudo /usr/local/sbin/leanops-incident-collect scheduled-monitor-failure
~~~

Correct only the identified condition. Then:

~~~bash
sudo systemctl reset-failed leanops-health-monitor.service
sudo systemctl start leanops-health-monitor.service
systemctl --failed --no-pager
~~~

## 5. Controlled-test safeguard

Never create a failure on a production system merely to test monitoring. In this isolated lab, pause the timer and guarantee cleanup:

~~~bash
sudo systemctl stop leanops-health-monitor.timer

sudo bash -c '
cleanup() {
    systemctl stop apache2
    systemctl start leanops-health-monitor.timer
}
trap cleanup EXIT

systemctl start apache2
systemctl reset-failed leanops-health-monitor.service
systemctl start leanops-health-monitor.service
monitor_rc=$?
echo "MONITOR_START_EXIT_CODE=$monitor_rc"

/usr/local/sbin/leanops-incident-collect scheduled-monitor-test
'
~~~

Afterward verify Apache is inactive and the timer is active. Inspect evidence before clearing the intentional failed state.

## 6. Verify after reboot

~~~bash
printf '%s\n' \
"TIMER_ENABLED=$(systemctl is-enabled leanops-health-monitor.timer)" \
"TIMER_ACTIVE=$(systemctl is-active leanops-health-monitor.timer)" \
"APACHE=$(systemctl is-active apache2)"

systemctl list-timers --all leanops-health-monitor.timer --no-pager
sudo journalctl -b -u leanops-health-monitor.service --no-pager
~~~

Confirm the timer survived reboot and a post-boot run completed.

## 7. Disable or restore

To stop scheduling without deleting files:

~~~bash
sudo systemctl disable --now leanops-health-monitor.timer
~~~

To re-enable:

~~~bash
sudo systemctl enable --now leanops-health-monitor.timer
~~~

If a unit file is damaged, extract the latest verified eleven-source configuration archive into an isolated temporary directory. Compare content, ownership, and permissions before replacing either live file. Reload and validate systemd after replacement.

If file-level recovery fails, restore snapshot `19-PDCA09-ScheduledMonitoringComplete`. To remove the entire Cycle 09 change, restore snapshot `18-PDCA09-PreScheduledMonitoring`.
