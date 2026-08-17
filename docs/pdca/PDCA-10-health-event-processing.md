# PDCA 10: Health Event Processing and Retention

## Summary

Cycle 10 extended the scheduled health monitor with durable abnormal-condition state, event history, recovery tracking, evidence thresholds, and bounded retention. A root-controlled Bash handler owns locking and health-check execution. A Python processor validates results, maps changing messages to stable condition identifiers, records every abnormal cycle, and distinguishes health results from monitoring-pipeline errors.

Warning evidence is due on the fourth consecutive occurrence of the same condition. Failures are due immediately. Recovery resets the consecutive count and evidence latch. Ordinary healthy runs remain in the system journal but are not duplicated in the health-event log.

The counting, recovery, file protection, timer integration, and 180-day retention policies passed. The final automatic collector invocation after the integrated threshold remains an open validation item, so this cycle is documented as implemented but not yet fully closed.

## Plan

### Current condition and problem

Cycle 09 ran the health check every 15 minutes, but each execution was independent. Repeated warnings had no durable count, related messages containing different numbers could fragment into separate histories, and automated evidence could be duplicated. Health-event and incident-evidence storage also had no formal retention boundary.

### Expected result

- Preserve the existing health-check logic and exit codes.
- Record every warning and failure without recording generic healthy runs.
- Track each condition independently through a stable identifier.
- Trigger evidence on warning occurrence four and failure occurrence one.
- Prevent duplicate evidence until recovery.
- Record recovery and reset the active count and latch.
- Return code `3` for locking, parsing, state, logging, or evidence-pipeline errors.
- Retain detailed health-event and raw incident evidence for 180 days.
- Keep the timer operational and preserve rollback paths.

### Test method

1. Preserve snapshot `20-PDCA10-PreHealthEventHandling`.
2. Verify Python and required standard-library modules.
3. Build and syntax-check the processor before live integration.
4. Test missing arguments, missing files, invalid codes, unknown conditions, and mismatched output.
5. Test known condition mapping with current health output.
6. Simulate four consecutive warning observations and one recovery.
7. Clear synthetic records before live activation.
8. Connect the processor to a locking Bash handler.
9. Connect the systemd service to the handler and verify timer operation.
10. Add and validate 180-day retention policies.
11. Preserve snapshot `Health Monitor Retention Verified - 2026-08-17`.
12. At the next available threshold, verify exactly one automatic evidence package and duplicate suppression.

### Risks and rollback

- A malformed processor could hide or misclassify a health result.
- Concurrent runs could corrupt counts or produce duplicate evidence.
- State or log files could expose operational data if permissions were too broad.
- Incorrect retention could delete evidence too early.
- Multiple pre-change copies were retained for the handler, processor, and service.
- Syntax, runtime, permission, and controlled state tests preceded live service integration.
- Snapshot 20 preserves the Cycle 09 baseline, and the final retention snapshot preserves the current implementation.

## Do

### Added a locked execution handler

The Bash handler validates required executables, applies a restrictive `umask`, waits up to 30 seconds for an exclusive lock, captures health output in a temporary file, and passes the output and health exit code to the Python processor. Cleanup is limited to the expected temporary-file prefix.

### Added a Python condition processor

The processor uses only the Python standard library. It:

- accepts health codes `0`, `1`, and `2`;
- rejects unknown abnormal messages;
- verifies that parsed severity agrees with the supplied health code;
- maps dynamic messages to stable identifiers such as `package_updates`;
- writes condition state atomically;
- appends tab-separated `OBSERVED`, `RECOVERED`, and evidence-action records;
- keeps an evidence latch for each active condition;
- reserves code `3` for a monitoring-pipeline error.

### Updated scheduled execution

The existing systemd service now launches the handler. `SuccessExitStatus=1 2` prevents expected health warnings and processed health failures from becoming failed infrastructure units. Pipeline code `3` is not accepted and remains visible as a failed service.

### Added bounded retention

The event log uses a root-owned logrotate policy:

~~~text
frequency: daily
rotations: 180
maximum age: 180 days
older rotations: compressed
new file: 0600 root:root
~~~

Raw evidence under `/var/log/leanops-incidents` uses a `systemd-tmpfiles` age rule of `180d`.

## Check

### Before and after

| Before | After |
|---|---|
| Scheduled runs were independent | Active abnormal conditions retain state across runs |
| Repeated warnings had no consecutive count | Each warning increments a stable condition count |
| Healthy recovery was not represented in condition state | Recovery writes one record and clears active state |
| No evidence threshold or latch | Warning threshold is four; failure threshold is one; latch resets on recovery |
| Unknown messages could not be classified safely | Unknown or inconsistent results return pipeline code `3` |
| Event and raw-evidence storage had no formal limit | Detailed records are bounded at 180 days |

### Sanitized validation evidence

The reusable public excerpt is stored at [`../../evidence/sanitized/pdca-10-health-event-retention.txt`](../../evidence/sanitized/pdca-10-health-event-retention.txt).

~~~text
PROCESSOR VALIDATION
syntax exit code: 0
missing arguments: pipeline code 3
missing input file: pipeline code 3
invalid health code: pipeline code 3
unknown abnormal condition: pipeline code 3
health-code mismatch: pipeline code 3
known warning mapped to: package_updates

CONDITION STATE TEST
warning observations: 1, 2, 3, 4
evidence due at occurrence: 4
active count after recovery: 0
recovery event: recorded
generic healthy event: not recorded

LIVE SERVICE
service result: success
failed units: 0
timer: active and scheduled
state/event permissions: 0600 root:root

RETENTION
event rotation: daily
rotations retained: 180
maximum age: 180 days
raw evidence age: 180 days
policy ownership: 0644 root:root
configuration validation: passed
~~~

| Verification | Result |
|---|---|
| Processor and handler syntax | Passed |
| Known and unknown condition handling | Passed |
| Exit-code consistency enforcement | Passed |
| Four-occurrence warning count | Passed |
| Recovery reset and recovery record | Passed |
| Protected state and event files | Passed |
| Service and timer operation | Passed |
| Event-log retention policy | Passed |
| Raw-evidence retention policy | Passed |
| Integrated collector invocation at threshold | Not yet observed |
| Duplicate suppression after automatic collection | Not yet observed |

The implementation met the state, recording, recovery, service, and retention objectives. The cycle remains open until the final two evidence-trigger checks pass.

## Act

### Current standard

- Use the systemd timer as the normal trigger.
- Let the Bash handler own locking and health-check execution.
- Treat code `3` as a monitoring-pipeline failure requiring immediate investigation.
- Review condition state and event history before resetting or deleting anything.
- Record every abnormal observation and every recovery, but not generic healthy runs.
- Retain raw event and incident evidence for 180 days.
- Keep confirmed causes, corrections, runbooks, and PDCA records permanently in sanitized form.

### Remaining validation

Allow a real warning to reach four scheduled occurrences or introduce one controlled failure. Confirm that:

1. exactly one evidence package is created;
2. the state latch changes to `true`;
3. another occurrence does not create another package;
4. recovery clears the latch;
5. a new episode can create new evidence.

Afterward, expand and verify configuration-backup coverage for the handler, processor, service change, logrotate policy, and tmpfiles policy.

### Standard work and recovery

See [`../runbooks/manage-health-event-processing.md`](../runbooks/manage-health-event-processing.md).

### Recovery point

Snapshot `Health Monitor Retention Verified - 2026-08-17` preserves the verified state at shutdown. Snapshot `20-PDCA10-PreHealthEventHandling` remains the pre-change rollback point.
