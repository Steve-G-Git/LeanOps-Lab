# PDCA 12: Controlled Email Notifications

## Summary

Cycle 12 extends the local health-monitoring pipeline with controlled SMTP notifications. Health state, incident evidence, and delivery state remain separate so an email failure cannot erase or hide the underlying condition.

Warnings are tallied without email for the first three consecutive observations. Observation four queues one alert and evidence. Failures queue an alert and evidence immediately. Continued conditions are recorded without duplicate messages, while recovery generates one notification. Different conditions from the same run are grouped into one email but remain visibly separate.

The state-transition tests, live delivery, duplicate suppression, retry retention, recovery handling, protected file permissions, service integration, timer operation, 180-day log retention, backup expansion, SHA-256 verification, isolated restoration, and final recovery checkpoint passed. Cycle 12 is verified, merged into `main`, and closed.

## Plan

### Current condition and problem

Cycle 10 could detect, tally, preserve, and collect evidence for abnormal conditions, but the administrator still had to inspect the server to know something occurred. Emailing every warning would create noise, while making local state dependent on SMTP would risk losing evidence during a delivery outage.

### Expected result

- Tally warning observations one through three without email.
- On warning observation four, collect evidence and queue one alert.
- Queue an immediate alert and evidence for a first failure.
- Group different conditions from one run into one clearly separated message.
- Suppress repeated alerts until recovery.
- Send one recovery notification after an alerted condition clears.
- Coalesce an unsent alert and recovery as `ALERT_RECOVERED`.
- Retain failed deliveries for retry on the next timer run.
- Save health state and evidence before attempting external delivery.
- Keep notification state and history separate from health-event records.
- Protect SMTP configuration and operational records with root-only access.
- Retain health and notification event logs for 180 days.
- Preserve rollback to the completed Cycle 10 baseline.

### Test method

1. Preserve snapshot `22-PDCA12-PreEmailNotifications`.
2. Build and validate the handler, processor, notifier, service, retention policy, and isolated tests on the feature branch.
3. Preserve file-level rollback copies and pause the timer.
4. Install non-secret components with root ownership.
5. Configure SMTP only on the VM in a protected file.
6. Verify standalone delivery.
7. Run the live health service and confirm a grouped notification.
8. Repeat the condition and verify duplicate suppression.
9. Inspect notification state, event history, permissions, service result, timer state, and failed units.
10. Validate the combined 180-day logrotate declaration.
11. Expand backup coverage, perform isolated restoration, audit the branch, and preserve the final recovery checkpoint.

### Risks and rollback

- SMTP failure could delay notification.
- Repeated conditions could create message noise.
- Multiple conditions could be mistaken for one recurrence.
- Credentials could be exposed through Git, evidence, or backups.
- Cross-platform line endings could break scripts or configuration.
- Invalid retention syntax could fail the system logrotate service.

The SMTP configuration is excluded from Git and protected as `0600 root:root`. Local health state and evidence are saved before delivery. Pending notifications survive delivery failure. Pre-change files are retained under `/root/leanops-cycle12-rollback`, and snapshot `22-PDCA12-PreEmailNotifications` preserves the completed Cycle 10 baseline.

## Do

### Added condition-aware notification state

The processor keeps health condition state separate from notification state. It queues alerts and recoveries only when a condition crosses a defined transition. Each item includes the stable condition identifier, severity, message, count, evidence status, and timing needed for an actionable notification.

### Added grouped SMTP delivery

The notifier reads a root-only configuration file stored only on the VM. One run produces at most one email, with each condition shown in a separate numbered section. Evidence is referenced but not attached. Successful delivery updates notified state; failed delivery leaves the item pending for retry.

### Preserved control boundaries

- Local detection and evidence do not depend on SMTP success.
- Warning noise is reduced through the four-observation threshold.
- Failures remain immediate.
- Different problems remain visibly distinct inside a grouped message.
- Continued observations remain tallied without duplicate email.
- Recovery closes the notification loop.
- Healthy runs are not duplicated into operational event logs.

### Updated scheduled execution and retention

The handler invokes the processor and notifier as one locked execution chain. Expected health exit codes remain accepted by systemd, while pipeline code `3` remains a visible service failure.

The health-event and notification-event TSV files share one daily logrotate policy with 180 rotations, a 180-day maximum age, compression, delayed compression, and new-file mode `0600 root:root`.

## Check

### Before and after

| Before | After |
|---|---|
| Abnormal conditions required manual server review | Alert-worthy transitions produce a controlled email |
| Repeated warnings had no notification threshold | Observations 1-3 tally; observation 4 alerts once |
| Failures were preserved locally | First failure is preserved and queued immediately |
| Different conditions could only be reviewed locally | One email groups the run while separating each condition |
| No delivery state or retry queue | Failed delivery remains pending for the next cycle |
| Recovery existed only in health-event history | One recovery notification closes an alerted condition |
| Only the health-event log had a rotation target | Both event logs share the 180-day policy |

### Sanitized validation evidence

See [`../../evidence/sanitized/pdca-12-email-notifications.txt`](../../evidence/sanitized/pdca-12-email-notifications.txt).

| Verification | Result |
|---|---|
| Handler Bash syntax | Passed |
| Processor, notifier, and test Python syntax | Passed |
| systemd unit verification | Passed |
| Six isolated state-transition tests | Passed |
| Standalone authenticated SMTP delivery | Passed |
| Live grouped warning notification | Passed |
| Distinct grouped conditions | Passed in isolated testing |
| Duplicate suppression on repeated live warning | Passed; event count did not increase |
| Delivery failure retains pending work | Passed |
| Later success clears pending work | Passed |
| Notification state and event permissions | Passed; `0600 root:root` |
| Service result and timer operation | Passed |
| Combined event-log retention policy | Passed |
| Protected backup scope | Passed; expanded from 15 to 17 non-secret sources |
| Fresh backup SHA-256 verification | Passed |
| Isolated restore | Passed; 17 of 17 sources restored |
| Restored content and metadata | Passed; zero mismatches |
| SMTP credential configuration excluded | Passed; absent from backup and public evidence |
| Final recovery checkpoint | Passed; snapshot `23-PDCA12-EmailNotificationsVerified` created |
| Failed units after correction | Zero |

### Corrections found during Check

1. Files transferred from Windows contained CRLF line endings. Bash and Python validation exposed the problem. Live copies were normalized, retested, and the repository path remains governed by `.gitattributes` with LF endings.
2. The two log paths in the logrotate policy were initially split across lines. The scheduled service rejected the file. The paths were combined into one valid declaration, debug validation passed, the service returned success, and zero failed units remained.
3. A host-access interruption was traced to a host-side network filter rather than the VM, SSH, firewall, or Cycle 12 code. It is retained as a lab lesson but excluded from product acceptance results.

## Act

### Candidate standard

- Use the 15-minute timer as the normal trigger.
- Record abnormal conditions before attempting notification.
- Alert on warning observation four and failure observation one.
- Group conditions by run while keeping each visibly separate.
- Suppress duplicates until recovery.
- Send one recovery notification.
- Retain failed deliveries for retry without discarding local evidence.
- Keep SMTP credentials out of Git, evidence, and backups.
- Protect notification state and history as `0600 root:root`.
- Retain operational health and notification history for 180 days.
- Treat processor, notifier, SMTP, or retention failures as visible problems.

### Closure result

- Protected backup coverage expanded from 15 to 17 sources by adding the notifier and AppArmor local rule.
- The SMTP credential configuration remained excluded from the backup archive.
- A fresh backup passed SHA-256 verification.
- All 17 approved sources restored in isolation with zero missing files, content mismatches, or metadata mismatches.
- Final service, timer, state-file, retention, and failed-unit checks passed.
- Snapshot `23-PDCA12-EmailNotificationsVerified` preserves the verified recovery point.
- Public documentation was audited for credentials and unnecessary identifiers.
- Cycle 12 is closed on `pdca-12-email-notifications` and remains unmerged until normal branch review.

### Standard work and recovery

See [`../runbooks/manage-health-notifications.md`](../runbooks/manage-health-notifications.md).
