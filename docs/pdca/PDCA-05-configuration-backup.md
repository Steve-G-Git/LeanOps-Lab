# PDCA 05: Create and Verify a Configuration Backup

## Summary

Recovery depended primarily on VirtualBox snapshots, and critical network, SSH, and firewall settings were distributed across several directories. Cycle 05 created a protected, allowlist-based Bash backup process for seven approved files. The resulting archive passed integrity and scope checks, restored into an isolated directory with matching contents and metadata, transferred to Windows, passed a second SHA-256 comparison, and remained valid after reboot.

This package supports selected-configuration recovery. It is not a full server backup or complete disaster-recovery system.

Raw screenshots are not published because observed terminal output contained personal Windows paths, generated IPv6 addresses, or other identifiers unnecessary to the result. The evidence below is a sanitized transcription.

## Plan

### Current condition and problem

- VirtualBox snapshots provided rollback but were tied to the VM.
- No portable package protected the verified network, SSH-hardening, and UFW configuration.
- No standard backup command, explicit scope control, manifest, integrity check, or restore test existed.
- A backup that collected broad directories could accidentally include private keys, authentication data, logs, or machine-specific information.

### Expected result

- A root-controlled directory stores protected backup artifacts.
- An explicit allowlist limits collection to approved regular files.
- A reusable Bash script validates its sources before creating an archive.
- The package contains a compressed archive, metadata manifest, and SHA-256 checksum.
- Archive scope and integrity are verified before restoration.
- Restoration into an isolated directory produces byte-for-byte matches with matching ownership and permissions.
- A verified copy is transferred off the VM and independently checked on Windows.
- SSH, Apache state, UFW, static addressing, outbound access, and DNS remain correct.
- Backup controls and archive integrity survive reboot.

### Approved scope

```text
etc/systemd/network/20-leanops-enp0s8.network
etc/ssh/sshd_config.d/00-leanops-auth.conf
etc/default/ufw
etc/ufw/user.rules
etc/ufw/user6.rules
etc/leanops-backup-files
usr/local/sbin/leanops-config-backup
```

Private keys, `authorized_keys`, password databases, logs, and machine-specific identifiers were excluded.

### Test method

1. Record source ownership and permissions without displaying contents.
2. Create snapshot `10-PDCA05-PreConfigBackup`.
3. Verify required tools, free space, and destination availability.
4. Create a protected backup directory and root-controlled allowlist.
5. Validate that every allowlisted source is a regular file and not a symbolic link.
6. Create the backup script and validate its Bash syntax before execution.
7. Review the script in full, then execute it.
8. Verify SHA-256 integrity and list the archive without extraction.
9. Extract into a temporary isolated directory.
10. Compare every restored file's contents, ownership, and permissions with the live source.
11. Remove only the temporary restore directory.
12. Copy protected export artifacts to Windows and independently compare SHA-256 values.
13. Remove only the temporary Ubuntu export copy.
14. Recheck services, firewall, addressing, internet access, and DNS.
15. Reboot and verify SSH, backup controls, archive integrity, and UFW.

### Risks and rollback

- An overly broad backup could collect secrets or unrelated data.
- Restoring directly over live files could damage a working configuration.
- Incorrect permissions could expose configuration or prevent administration.
- Restoring key-only SSH settings before provisioning a public key could cause lockout.
- Snapshot `10-PDCA05-PreConfigBackup` preserved the completed Cycle 04 state.
- The first restore was restricted to a `mktemp` directory under `/tmp`.
- Live restoration was not required because all source files remained healthy.

## Do

### Established protected storage and scope

The backup directory was created as `700 root:root`. The allowlist was created as `600 root:root` and expanded from five operational configuration files to seven entries so the backup definition and script could also be recovered.

Every entry passed a regular-file and symbolic-link check before the script was created.

### Created and reviewed the backup script

`/usr/local/sbin/leanops-config-backup` was installed as `700 root:root`. Its controls included:

- `set -Eeuo pipefail`
- restrictive `umask 077`
- root-execution requirement
- nonempty allowlist requirement
- rejection of absolute paths and parent-directory traversal
- rejection of missing files and symbolic-link sources
- UTC-stamped archive, manifest, and checksum names
- archive-listing validation after creation
- final artifact permissions of `600`

`bash -n` returned zero, and the full script was reviewed before execution.

### Created and exported the package

The script created three protected artifacts:

```text
leanops-config-<UTC_TIMESTAMP>.tar.gz
leanops-config-<UTC_TIMESTAMP>.manifest.txt
leanops-config-<UTC_TIMESTAMP>.tar.gz.sha256
```

The archive contained exactly the seven approved relative paths. A temporary export directory allowed the unprivileged administrative account to transfer copies with SCP. The root-owned originals remained unchanged.

### Observed corrections

- Early filename typos and an incorrect `chown` target failed safely before the correct commands were entered.
- Bash syntax validation alone could not prove filenames and variables were logically correct, so the entire script was displayed and reviewed before execution.
- The allowlist was intentionally expanded to include itself and the backup script, making the process definition recoverable with the operational configuration.

## Check

### Sanitized evidence summary

```text
SOURCE VALIDATION
7 approved regular files: OK

SCRIPT
Bash syntax result: 0
permissions: 700 root:root

BACKUP PACKAGE
archive scope: exactly 7 approved paths
Ubuntu SHA-256 verification: OK
artifacts: 600 root:root

ISOLATED RESTORE
content matches: 7 of 7
ownership and permission matches: 7 of 7
live files overwritten: none

OFF-VM COPY
3 artifacts transferred to Windows
Windows SHA-256 comparison: PASS

POST-CHANGE AND POST-REBOOT
SSH: active and accessible
Apache: inactive
UFW: active with intended restricted rule
host-only address: 192.168.244.10/24
outbound ping: 4 received, 0% loss
DNS resolution: successful
protected archive checksum after reboot: OK
```

| Verification | Result |
|---|---|
| Source validation | Seven approved regular, non-symbolic-link files |
| Archive integrity on Ubuntu | Passed |
| Archive scope | Exactly seven expected paths |
| Isolated content comparison | Seven matches |
| Isolated metadata comparison | Seven matches |
| Temporary restore cleanup | Verified |
| Off-VM transfer | Three expected artifacts received |
| Windows checksum comparison | Passed |
| Ubuntu export cleanup | Verified |
| Required service and network checks | Passed |
| Reboot persistence | Passed |

## Act

### Final standard

- Critical configuration backups use the root-controlled allowlist and `/usr/local/sbin/leanops-config-backup`.
- Backup artifacts remain protected under `/var/backups/leanops`.
- Every archive must pass checksum and scope verification.
- Restore testing occurs in an isolated directory before any live recovery.
- A verified copy is kept off the VM.
- Live recovery requires a current snapshot or other rollback point.
- Administrative public-key access must exist before restoring the key-only SSH configuration.
- The completed state is preserved in snapshot `11-PDCA05-ConfigBackupVerified`.

### Standard work and recovery

Repeatable backup, integrity verification, isolated restoration, and controlled live-recovery steps are documented in [`../runbooks/backup-and-restore-configuration.md`](../runbooks/backup-and-restore-configuration.md).

### Remaining risks

- The package does not include installed packages, user data, SSH host keys, VM settings, or full-system state.
- The checksum detects corruption or unexpected change but does not authenticate the package creator.
- One verified off-VM copy exists, but a separate encrypted or versioned destination has not been established.
- A full replacement-server recovery has not been performed.
