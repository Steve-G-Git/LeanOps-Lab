# PDCA 07: Standardize Incident Evidence Collection

## Summary

Cycle 06 could detect operational failures, but investigation still required manually running many commands and searching separate logs. Cycle 07 created a root-controlled collector that packages 12 limited diagnostic sources, a manifest, and a SHA-256 checksum while sanitizing observed network identifiers.

A healthy package established the baseline. A controlled Apache-active condition then proved that the collector preserved the health failure, active service state, and start event before an automatic EXIT-trap rollback restored Apache to inactive. The collector was added to the configuration backup, both controlled-incident and configuration packages were verified on Windows, and the collector passed again after reboot.

Raw archives and screenshots are not published because they contain protected operational details or personal Windows paths. The evidence below is a sanitized summary of verified results.

## Plan

### Current condition and problem

- Health-check output identified a problem but did not collect supporting diagnostics.
- Relevant evidence was distributed across systemd, journald, authentication logs, UFW logs, network commands, resource commands, package state, and backup verification.
- Manual collection could omit a source, collect inconsistent time windows, or occur after the original condition disappeared.
- Broad copying of logs could expose unnecessary identifiers and unrelated historical data.

### Expected result

- One protected command creates a timestamped incident package.
- Collection includes the standardized health check and relevant supporting diagnostics.
- Original logs and configuration remain unchanged.
- Evidence scope and recent-log windows are limited.
- Observed MAC, UFW address-field, and generated local IPv6 risks are excluded or sanitized.
- Every package has a manifest, SHA-256 checksum, and protected permissions.
- A controlled failure is preserved before rollback.
- The collector is protected through the configuration-backup process and works after reboot.

### Evidence scope

1. Standardized health check
2. Failed systemd units
3. SSH, Apache, journald, and rsyslog status
4. UFW status and stored rules
5. IPv4 interfaces and routes
6. Listening TCP sockets
7. Root filesystem and memory
8. Cached package-update state
9. Latest configuration-backup verification
10. Recent SSH and Apache journal events
11. Recent `sshd` authentication entries
12. Recent UFW log entries

### Test method

1. Verify journald, rsyslog, persistent journal storage, authentication log, and UFW log.
2. Create snapshot `14-PDCA07-PreIncidentEvidence`.
3. Create a protected output directory and collector script.
4. Validate Bash syntax and review the script in full.
5. Collect and inspect a healthy baseline package.
6. Confirm artifact permissions, checksum, scope, sanitization, and embedded command results.
7. Temporarily start Apache and collect evidence before an automatic rollback.
8. Verify the incident package preserved the detected failure, active service state, and journal event.
9. Add the collector to the backup allowlist and test a nine-file configuration restore.
10. Verify the configuration and controlled-incident packages on Windows.
11. Remove temporary extractions and exports.
12. Reboot and repeat the collection and integrity checks.

### Risks and rollback

- Incident packages may expose identifiers or unrelated historical information.
- A broad or unbounded collection could consume excess storage.
- Temporary evidence could remain behind after failure.
- A controlled test could leave Apache running.
- Snapshot `14-PDCA07-PreIncidentEvidence` preserved the completed Cycle 06 state.
- The collector uses a root-only destination, restrictive permissions, limited evidence windows, sanitization, and a temporary-directory cleanup trap.
- The Apache wrapper uses its own EXIT trap to stop the service.

## Do

### Established protected collection

`/var/log/leanops-incidents` and `/usr/local/sbin/leanops-incident-collect` were created as `700 root:root`. Each run:

- validates a restricted label;
- creates a unique UTC incident identifier;
- stages evidence under a unique `/tmp` directory;
- records each command's exit code;
- sanitizes staged text before packaging;
- creates a compressed archive, external manifest, and checksum with mode `600`;
- removes the temporary staging directory through an EXIT trap.

### Limited and sanitized the evidence

The collector does not copy entire configuration directories or unrestricted logs. It uses IPv4-only network commands, a 30-minute service-journal window, up to 100 recent `sshd` entries, and up to 100 recent UFW entries.

Observed MAC addresses are replaced with `[MAC_REDACTED]`. UFW `SRC` and `DST` values are replaced with `[IP_REDACTED]`. Verification found zero raw MAC values, zero raw UFW address fields, and zero generated local IPv6 values in both inspected packages.

### Captured healthy and incident conditions

The healthy package embedded the normal warning-only health state. Apache was then started temporarily. The controlled package captured:

- the Apache-active health failure;
- health-check exit code `2`;
- active service status;
- one Apache start event in the recent journal;
- successful collection from every other defined source.

The wrapper's EXIT trap stopped Apache after collection. The next live health check returned the expected normal warning-only state.

### Extended recovery and off-VM storage

The collector became the ninth approved configuration source. The newest configuration package passed checksum, scope, nine content comparisons, nine metadata comparisons, and Windows verification. The controlled incident package also passed Windows SHA-256 verification.

Two configuration backups were created accidentally in quick succession. Unique UTC identifiers prevented overwriting, and the newest verified package was used for restoration and export.

## Check

### Sanitized evidence summary

```text
HEALTHY PACKAGE
collector exit code: 0
archive: 12 evidence files plus manifest
embedded health: 12 PASS, 1 WARN, 0 FAIL
embedded health exit code: 1
raw MAC count: 0
raw UFW address-field count: 0
generated local IPv6 count: 0

CONTROLLED APACHE PACKAGE
collector exit code: 0
embedded health: 11 PASS, 1 WARN, 1 FAIL
embedded health exit code: 2
Apache active-state evidence: present
Apache start journal event: present
other evidence-command exit codes: 0
automatic rollback: Apache inactive
Windows checksum verification: PASS

POST-REBOOT PACKAGE
collector exit code: 0
embedded health: 12 PASS, 1 WARN, 0 FAIL
archive checksum: OK
collector and output directory: 700 root:root
```

| Verification | Result |
|---|---|
| Collector syntax and ownership | Passed; `700 root:root` |
| Healthy package scope and integrity | Passed |
| Healthy sanitization checks | Passed |
| Controlled failure captured | Passed |
| Active service and journal evidence | Present |
| Automatic rollback | Apache returned to inactive |
| Controlled-package sanitization | Passed |
| Nine-file configuration restore | Contents and metadata matched |
| Off-VM archive checks | Both passed on Windows |
| Post-reboot collection | Passed |

## Act

### Final standard

- Collect evidence with `sudo /usr/local/sbin/leanops-incident-collect <label>`.
- Use only labels containing letters, numbers, underscores, and hyphens.
- Preserve the collector output, manifest, checksum result, health summary, and embedded command codes.
- Collect before making corrective changes whenever safety and access permit.
- Keep incident artifacts protected and do not publish raw packages.
- Verify checksums after transfer to another system.
- The collector remains in the protected nine-file configuration allowlist.
- The completed state is preserved in snapshot `15-PDCA07-IncidentEvidenceVerified`.

### Standard work and recovery

Collection, validation, interpretation, export, and cleanup steps are documented in [`../runbooks/collect-incident-evidence.md`](../runbooks/collect-incident-evidence.md).

### Remaining risks

- This is local, on-demand collection rather than centralized or continuous logging.
- Local root compromise could alter both original logs and locally stored evidence.
- Sanitization addresses tested patterns, not every possible sensitive value.
- Retention limits and automated storage monitoring have not been established.
