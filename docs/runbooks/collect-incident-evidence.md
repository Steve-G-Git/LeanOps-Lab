# Runbook: Collect and Verify Incident Evidence

## Purpose

Preserve a limited, sanitized snapshot of the LeanOps server's operational state before corrective work changes or removes useful evidence.

## Preconditions

- Key-authenticated SSH or VirtualBox console access
- Root access through `sudo`
- `/var/log/leanops-incidents` owned by `root:root` with mode `700`
- `/usr/local/sbin/leanops-incident-collect` owned by `root:root` with mode `700`
- Enough free space for the evidence package

## 1. Choose a label

Use a short description containing only letters, numbers, underscores, and hyphens:

```text
ssh-failure
apache-active
dns-timeout
```

Do not put usernames, passwords, ticket contents, or other sensitive data in the label.

## 2. Collect before correction

When access and safety permit, collect evidence before restarting services or changing configuration:

```bash
sudo /usr/local/sbin/leanops-incident-collect <label>
collector_rc=$?
echo "EXIT_CODE=$collector_rc"
```

Record the three generated artifact paths and collector exit code.

## 3. Verify protection and integrity

Set the exact identifier reported by the collector:

```bash
incident_id="<UTC_TIMESTAMP>-<label>"
```

```bash
sudo stat -c '%a %U:%G %n' \
"/var/log/leanops-incidents/leanops-incident-${incident_id}.tar.gz" \
"/var/log/leanops-incidents/leanops-incident-${incident_id}.manifest.txt" \
"/var/log/leanops-incidents/leanops-incident-${incident_id}.tar.gz.sha256"
```

Required mode and ownership:

```text
600 root:root
```

Verify the checksum:

```bash
sudo bash -c '
cd /var/log/leanops-incidents
sha256sum -c "leanops-incident-'"$incident_id"'.tar.gz.sha256"
'
```

## 4. Inspect in isolation

```bash
inspect_dir="$(mktemp -d /tmp/leanops-incident-inspect.XXXXXX)"

sudo tar -xzf \
"/var/log/leanops-incidents/leanops-incident-${incident_id}.tar.gz" \
-C "$inspect_dir"
```

Begin with:

- `01-health-check.txt`
- `02-failed-units.txt`
- `03-service-status.txt`
- The evidence file related to the reported failure
- Each `COMMAND_EXIT_CODE` line

Do not assume a missing result means a healthy condition. A nonzero evidence-command code may mean collection failed.

## 5. Preserve sanitization

Before any external sharing, confirm that the package contains no raw MAC addresses, UFW `SRC` or `DST` values, generated local IPv6 addresses, personal Windows paths, secrets, or unrelated personal information.

The collector's built-in replacements reduce exposure but do not replace a manual review before publication.

## 6. Remove only temporary inspection data

```bash
case "$inspect_dir" in
    /tmp/leanops-incident-inspect.*)
        sudo rm -rf -- "$inspect_dir"
        ;;
    *)
        echo "Refusing unexpected path: $inspect_dir"
        ;;
esac
```

Do not delete the protected archive merely because inspection is complete.

## 7. Transfer and verify

Create a temporary mode-`700` export directory in the administrator's Ubuntu home. Copy only the required archive, manifest, and checksum into it with mode `600`, transfer with SCP, and verify SHA-256 independently on the destination.

Remove only the temporary Ubuntu export after the destination verification passes.

## Recovery

- If collection fails, preserve the terminal error and determine which prerequisite or evidence source failed.
- If a temporary staging directory remains unexpectedly, verify its exact `/tmp/leanops-incident-*` path before removing it.
- If the collector is damaged, restore it from the verified nine-file configuration backup into an isolated directory first.
- Validate ownership, mode, Bash syntax, and contents before replacing the live script.
- Restore snapshot `15-PDCA07-IncidentEvidenceVerified` for the completed Cycle 07 state.
- Restore snapshot `14-PDCA07-PreIncidentEvidence` to remove the complete Cycle 07 implementation.
