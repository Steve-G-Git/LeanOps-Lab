# Runbook: Back Up and Restore LeanOps Configuration

## Purpose

Create, verify, export, and test a protected backup of approved LeanOps configuration files. This procedure supports selected-configuration recovery and does not replace a full-system backup.

## Preconditions

- Ubuntu administration through a verified key-authenticated session or the VirtualBox console
- Current recovery snapshot
- `/etc/leanops-backup-files` reviewed and owned by `root:root` with mode `600`
- `/usr/local/sbin/leanops-config-backup` reviewed and owned by `root:root` with mode `700`
- `/var/backups/leanops` owned by `root:root` with mode `700`
- Enough free space for the package and isolated test extraction

Never add private keys, `authorized_keys`, `/etc/shadow`, authentication secrets, logs, or machine-specific identifiers to the allowlist.

## 1. Review and validate the sources

Display the numbered allowlist:

```bash
sudo cat -n /etc/leanops-backup-files
```

Validate every path:

```bash
sudo bash -c 'while IFS= read -r path; do
    if [ -f "/$path" ] && [ ! -L "/$path" ]; then
        echo "OK: $path"
    else
        echo "INVALID: $path"
    fi
done < /etc/leanops-backup-files'
```

Stop if any entry is blank, absolute, contains `..`, is missing, or is a symbolic link.

## 2. Create the backup

Validate script syntax:

```bash
sudo bash -n /usr/local/sbin/leanops-config-backup
```

Run the script:

```bash
sudo /usr/local/sbin/leanops-config-backup
```

Record the three generated filenames. Do not assume the latest filename if more than one package exists.

## 3. Verify integrity and scope

Set the generated identifier for the current package:

```bash
backup_id="<UTC_TIMESTAMP>"
```

Verify the checksum:

```bash
sudo bash -c "cd /var/backups/leanops && sha256sum -c leanops-config-${backup_id}.tar.gz.sha256"
```

List the archive without extracting it:

```bash
sudo tar -tzf "/var/backups/leanops/leanops-config-${backup_id}.tar.gz"
```

Stop if the checksum fails or the archive contains anything outside the reviewed allowlist.

## 4. Test restoration in isolation

Create a unique temporary directory:

```bash
restore_dir="$(mktemp -d /tmp/leanops-restore-test.XXXXXX)"
echo "$restore_dir"
```

Extract only into that directory:

```bash
sudo tar -xzf "/var/backups/leanops/leanops-config-${backup_id}.tar.gz" -C "$restore_dir"
```

Compare contents:

```bash
sudo bash -c 'while IFS= read -r path; do
    if cmp -s "/$path" "'"$restore_dir"'/$path"; then
        echo "MATCH: $path"
    else
        echo "DIFFERENT: $path"
    fi
done < /etc/leanops-backup-files'
```

Compare ownership and permissions:

```bash
sudo bash -c 'while IFS= read -r path; do
    live="$(stat -c "%a %U:%G" "/$path")"
    restored="$(stat -c "%a %U:%G" "'"$restore_dir"'/$path")"
    if [[ "$live" == "$restored" ]]; then
        echo "METADATA MATCH: $path"
    else
        echo "METADATA DIFFERENT: $path"
    fi
done < /etc/leanops-backup-files'
```

Do not proceed if any comparison differs.

Remove only the isolated extraction:

```bash
case "$restore_dir" in
    /tmp/leanops-restore-test.*)
        sudo rm -rf -- "$restore_dir"
        ;;
    *)
        echo "Refusing unexpected path: $restore_dir"
        ;;
esac
```

## 5. Export a verified copy

Create a temporary protected export directory and copy the three artifacts with mode `600`. Transfer them to the approved off-VM destination using SCP. Independently calculate SHA-256 on the destination and compare it with the checksum file.

After the destination passes verification, remove only the temporary export copy. Keep the root-owned original and verified off-VM package.

## 6. Controlled live recovery

Live recovery is required only when a configuration is damaged or missing. Do not overwrite a healthy system merely to demonstrate restoration.

Before restoring:

1. Use the VirtualBox console or keep an existing administrative session open.
2. Create a current snapshot or equivalent rollback point.
3. Verify the package checksum and archive scope.
4. Restore into an isolated directory and inspect the intended differences.
5. Confirm the destination Ubuntu version and service layout are compatible.
6. Provision and verify the administrator's public key before restoring `00-leanops-auth.conf`. The backup deliberately excludes `authorized_keys`.

Copy only the required file from the isolated directory to its exact destination while preserving ownership and permissions. Validate its service-specific syntax before reloading or restarting anything.

Examples of required validation:

```bash
sudo sshd -t
sudo ufw status verbose
sudo networkctl status enp0s8 --no-pager
```

Keep console access available until a fresh key-authenticated SSH session succeeds.

## Recovery from a failed restore

- Revert the individual file from the pre-restore copy if available.
- Use the VirtualBox console if SSH becomes unavailable.
- Restore the current pre-recovery snapshot if file-level rollback fails.
- Snapshot `10-PDCA05-PreConfigBackup` removes the entire Cycle 05 implementation.
- Snapshot `11-PDCA05-ConfigBackupVerified` restores the completed verified backup state.
