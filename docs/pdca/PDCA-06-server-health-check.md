# PDCA 06: Standardize the Server Health Check

## Summary

The verified server state could be assessed only through a sequence of separate commands. Cycle 06 created a root-controlled Bash health check that evaluates 13 operational conditions and reports `PASS`, `WARN`, or `FAIL` with exit codes suitable for repeatable manual use and future automation.

The healthy state produced 12 passes and one legitimate package-update warning. A controlled Apache failure proved that the script returned exit code `2`, and an EXIT trap restored Apache to its required inactive state. The script was added to the configuration backup, restored in isolation, verified off the VM, and tested after reboot.

Raw screenshots are not published because they contained a personal Windows username, Windows profile paths, or generated IPv6 addresses. The evidence below is sanitized text.

## Plan

### Current condition and problem

- SSH, Apache, UFW, addressing, routing, connectivity, DNS, resources, package state, and backup integrity required separate commands.
- Results had no common severity labels or standardized exit codes.
- A technician could skip a check, interpret it inconsistently, or overlook a degraded condition.
- The Cycle 05 backup did not yet protect a health-check definition.

### Expected result

- One protected command checks the documented server standard.
- Every result uses `PASS`, `WARN`, or `FAIL`.
- Exit code `0` represents all-pass, `1` represents warning-only, and `2` represents at least one failure.
- Disk, memory, and update thresholds are documented.
- A safe controlled condition proves failure detection and rollback.
- The health check and updated eight-file backup survive reboot.

### Health standard and thresholds

| Condition | Standard |
|---|---|
| SSH | Active |
| Apache | Inactive |
| UFW | Active; default deny incoming, allow outgoing, routed disabled |
| SSH firewall rule | TCP 22 allowed from `192.168.244.1` only |
| Host-only address | `192.168.244.10/24` on `enp0s8` |
| Default route | Present through `enp0s3` |
| Internet and DNS | Successful |
| Root disk | WARN at 80%; FAIL at 90% |
| Available memory | WARN below 20%; FAIL below 10% |
| Package updates | WARN when current APT cache lists one or more |
| Latest configuration backup | SHA-256 verification passes |

### Test method

1. Capture the healthy state with read-only commands.
2. Create snapshot `12-PDCA06-PreHealthCheck`.
3. Confirm required command availability and package-state behavior.
4. Create the root-controlled health-check script.
5. Validate Bash syntax and review the complete script before execution.
6. Run the normal-state check and capture its exit code.
7. Verify direct unprivileged execution is denied.
8. Add the script to the backup allowlist.
9. Create, inspect, restore, compare, export, and independently verify an eight-file backup.
10. Temporarily start Apache, run the health check, and use an automatic cleanup trap.
11. Recheck the normal state.
12. Reboot and repeat the health check.

### Risks and rollback

- A false positive could create unnecessary work; a false negative could hide a real failure.
- A failure test could leave the server outside its standard state.
- The script requires privileged access and must not disclose protected content.
- Snapshot `12-PDCA06-PreHealthCheck` preserved the completed Cycle 05 state.
- The Apache test used an EXIT trap that stopped the service regardless of the health-check exit code.
- UFW remained active and no port forwarding or public exposure was configured.

## Do

### Built the health check

`/usr/local/sbin/leanops-health-check` was installed as `700 root:root`. The script:

- requires effective user ID zero;
- counts passes, warnings, and failures;
- validates the documented service, firewall, network, resource, update, and backup states;
- prints a UTC execution time;
- returns the highest applicable severity through its exit code;
- suppresses checksum values and configuration contents.

`bash -n` returned zero, and the script was reviewed in full before execution. Direct execution as `leanopsadmin` was denied with shell exit code `126`, confirming the file's protected mode.

### Classified the package state

The current APT cache listed two upgradable packages and no manually held packages. A normal simulated upgrade reported zero immediately selected upgrades and two not upgraded. The health check therefore classifies the condition as a warning, not a failure.

### Expanded configuration recovery

The health-check path became the eighth approved backup source. The updated package passed:

- source validation;
- SHA-256 verification;
- exact eight-path archive inspection;
- eight isolated content comparisons;
- eight ownership and permission comparisons;
- Windows SHA-256 comparison;
- post-reboot selection as the latest verified backup.

Temporary restore and Ubuntu export directories were removed after verification.

### Performed a controlled failure

Apache was temporarily started because its required state is inactive. The health check detected the condition, returned exit code `2`, and an EXIT trap stopped Apache. A normal-state health check immediately followed and confirmed recovery.

## Check

### Sanitized evidence summary

```text
NORMAL STATE
12 PASS, 1 WARN, 0 FAIL
warning: 2 package updates available in current APT cache
exit code: 1

CONTROLLED APACHE FAILURE
11 PASS, 1 WARN, 1 FAIL
failure: Apache active but required inactive
health-check exit code: 2
wrapper exit code: 2
Apache after automatic cleanup: inactive

POST-REBOOT
12 PASS, 1 WARN, 0 FAIL
exit code: 1
latest eight-file backup verification: PASS
```

| Verification | Result |
|---|---|
| Syntax validation | Passed |
| Script ownership and mode | `700 root:root` |
| Normal-state classification | 12 PASS, 1 WARN, 0 FAIL |
| Warning exit code | `1` |
| Direct unprivileged execution | Denied |
| Controlled failure classification | 11 PASS, 1 WARN, 1 FAIL |
| Failure exit code | `2` |
| Automatic rollback | Apache returned to inactive |
| Eight-file recovery test | Content and metadata matched |
| Off-VM backup verification | Windows SHA-256 comparison passed |
| Post-reboot health check | Expected warning-only result persisted |

## Act

### Final standard

- Run the health check with `sudo /usr/local/sbin/leanops-health-check`.
- Record the UTC timestamp, summary, individual warning or failure, and exit code.
- Exit code `0` requires no corrective action.
- Exit code `1` requires review and planned follow-up.
- Exit code `2` requires investigation before declaring the server healthy.
- Do not silence a warning or failure without correcting the condition or formally changing the documented standard.
- The health-check script remains in the protected eight-file backup allowlist.
- The completed state is preserved in snapshot `13-PDCA06-HealthCheckVerified`.

### Standard work and recovery

Execution, interpretation, escalation, and recovery steps are documented in [`../runbooks/run-server-health-check.md`](../runbooks/run-server-health-check.md).

### Remaining risks

- Package results depend on the current local APT cache and do not prove it was freshly updated.
- The internet test uses ICMP to one public address; ICMP filtering could create a false failure.
- Thresholds are initial lab standards and have not been tuned from long-term operating history.
- The check runs on demand. Scheduling and retained historical results have not been implemented.
