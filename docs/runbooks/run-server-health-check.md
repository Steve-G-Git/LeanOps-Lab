# Runbook: Run and Interpret the Server Health Check

## Purpose

Run one standardized assessment of the LeanOps Ubuntu server and respond consistently to pass, warning, and failure results.

## Preconditions

- Key-authenticated SSH or VirtualBox console access
- Proton VPN fully exited for the current host-only configuration
- `leanops-health-check` owned by `root:root` with mode `700`
- No planned maintenance currently changing the expected service state

## 1. Run the check

```bash
sudo /usr/local/sbin/leanops-health-check
health_rc=$?
echo "EXIT_CODE=$health_rc"
```

Record the UTC timestamp, summary, individual non-pass results, and exit code.

## 2. Interpret the exit code

| Exit code | Meaning | Required response |
|---:|---|---|
| `0` | All checks passed | Record result; no correction required |
| `1` | One or more warnings, no failures | Review and schedule appropriate follow-up |
| `2` | One or more failures | Investigate before declaring the server healthy |
| `126` | Direct execution denied | Run the protected script with `sudo` |

## 3. Review warnings

Current warning conditions include:

- Root filesystem usage from 80% through 89%
- Available memory from 10% through 19%
- One or more package updates listed in the current APT cache

Package warnings are based on cached metadata. Before maintenance, refresh package metadata through the approved update procedure and reassess the available updates.

## 4. Investigate failures

Use the failed line to select the smallest relevant diagnostic:

| Failure | First diagnostic |
|---|---|
| SSH inactive | `systemctl status ssh --no-pager` |
| Apache active | `systemctl status apache2 --no-pager` |
| UFW state or policy | `sudo ufw status verbose` |
| Static address | `ip -4 -br address show enp0s8` |
| Default route | `ip -4 route show default` |
| Internet | `ping -c 4 1.1.1.1` |
| DNS | `getent hosts archive.ubuntu.com` |
| Disk | `df -h /` |
| Memory | `free -h` |
| Backup integrity | Verify the latest checksum directly under `/var/backups/leanops` |

Preserve the original output before making a correction. Do not make multiple unrelated changes at once.

## 5. Verify recovery

After correcting the identified condition, rerun:

```bash
sudo /usr/local/sbin/leanops-health-check
health_rc=$?
echo "EXIT_CODE=$health_rc"
```

Confirm the original failure is gone and no new failure appeared.

## Controlled-test safeguard

Do not create a failure on a production system merely to test monitoring. In this isolated lab, the Apache test used an automatic EXIT trap:

```bash
sudo bash -c '
cleanup() {
    systemctl stop apache2
}

trap cleanup EXIT
systemctl start apache2
/usr/local/sbin/leanops-health-check
health_rc=$?
echo "HEALTH_EXIT_CODE=$health_rc"
exit "$health_rc"
'
```

Always verify Apache is inactive afterward:

```bash
systemctl is-active apache2
```

## Recovery

- If the health-check script itself is damaged, restore only that file from a verified eleven-file configuration backup into an isolated directory first.
- Validate restored ownership, mode, contents, and Bash syntax before replacing the live script.
- If file-level recovery fails, restore snapshot `13-PDCA06-HealthCheckVerified`.
- To remove the complete Cycle 06 implementation, restore snapshot `12-PDCA06-PreHealthCheck`.
