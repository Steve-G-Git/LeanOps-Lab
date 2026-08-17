# Evidence Handling

Only reviewed and sanitized evidence belongs in this directory.

## Structure

- `sanitized/`: screenshots or text output approved for public use
- `raw/`: local working evidence excluded by `.gitignore`

## Published evidence

- [`sanitized/pdca-10-health-event-retention.txt`](sanitized/pdca-10-health-event-retention.txt): processor, condition-state, service, retention, and open-validation results for Cycle 10

## Review checklist

Before adding evidence, remove or crop:

- Personal usernames and local profile paths
- Real home-network details
- Passwords, keys, tokens, and authentication material
- Machine IDs, boot IDs, and unnecessary MAC addresses
- SSH fingerprints unless they are essential to the documented test
- Unrelated browser tabs, notifications, and personal content

Use descriptive filenames that identify the PDCA cycle, test, and observed state without exposing unnecessary identifiers.
