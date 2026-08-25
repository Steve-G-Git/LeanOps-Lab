# Runbook: Manage Share-Data Backups

## Purpose

Operate, verify, export, restore, and troubleshoot the protected backup of `/srv/leanops-shares`. This data backup is separate from the 21-source selected-configuration backup.

## Preconditions

- Root access through `sudo`
- `/srv/leanops-shares` available
- `/var/backups/leanops-shares` owned by `root:root` with mode `0700`
- `/usr/local/sbin/leanops-share-backup` owned by `root:root` with mode `0700`
- Current snapshot or other rollback point
- Enough free disk space for a new archive and isolated extraction

Raw archives, manifests, file inventories, and per-file hashes remain private.

## 1. Verify the scheduled service

```bash
systemctl is-enabled leanops-share-backup.timer
systemctl is-active leanops-share-backup.timer
systemctl list-timers leanops-share-backup.timer --all --no-pager
systemctl show leanops-share-backup.service \
-p Result -p ExecMainCode -p ExecMainStatus
```

The timer runs daily at 02:30, is persistent, and may delay up to five minutes. A successful run reports result `success` and exit status `0`.

## 2. Review protected storage

```bash
sudo stat -c '%a %U:%G %n' \
/usr/local/sbin/leanops-share-backup \
/etc/systemd/system/leanops-share-backup.service \
/etc/systemd/system/leanops-share-backup.timer \
/var/backups/leanops-shares

sudo find /var/backups/leanops-shares -maxdepth 1 -type f \
-printf '%m %u:%g %f\n' | sort
```

Required modes:

- script and backup directory: `0700 root:root`;
- service and timer: `0644 root:root`;
- archive, manifest, and checksum: `0600 root:root`.

## 3. Run a controlled backup

Validate the script first:

```bash
sudo bash -n /usr/local/sbin/leanops-share-backup
```

Then start one backup through systemd:

```bash
sudo systemctl start leanops-share-backup.service
systemctl show leanops-share-backup.service \
-p Result -p ExecMainCode -p ExecMainStatus
```

The script prevents overlapping execution with `flock`. It records whether Samba and the health-monitor timer were active, pauses them, and restores their prior states through an EXIT trap.

After the run:

```bash
systemctl is-active smbd
systemctl is-active leanops-health-monitor.timer
systemctl is-active leanops-share-backup.timer
systemctl --failed --no-pager
```

## 4. Verify one backup set

Set the exact UTC identifier printed by the backup:

```bash
backup_id="<UTC_TIMESTAMP>"
```

Verify archive integrity:

```bash
sudo bash -c "cd /var/backups/leanops-shares &&
sha256sum -c leanops-shares-${backup_id}.tar.gz.sha256"
```

List the archive without extraction:

```bash
sudo tar -tzf "/var/backups/leanops-shares/leanops-shares-${backup_id}.tar.gz"
```

Review the protected manifest locally with `sudo`. Do not copy its raw file inventory or hashes into public documentation.

## 5. Restore and compare in isolation

Create a uniquely named temporary directory:

```bash
restore_dir="$(mktemp -d /tmp/leanops-share-restore.XXXXXX)"
echo "$restore_dir"
```

Extract only into that directory:

```bash
sudo tar \
--acls \
--xattrs \
--same-owner \
-xzf "/var/backups/leanops-shares/leanops-shares-${backup_id}.tar.gz" \
-C "$restore_dir"
```

Compare the restored tree against the protected manifest and the intended recovery requirement. Verify content, modes, numeric ownership, ACLs, and extended attributes as applicable. Do not overwrite the live share tree merely to demonstrate restoration.

Remove only the validated temporary extraction:

```bash
case "$restore_dir" in
    /tmp/leanops-share-restore.*)
        sudo rm -rf -- "$restore_dir"
        ;;
    *)
        echo "Refusing unexpected path: $restore_dir"
        ;;
esac
```

## 6. Export a verified copy

1. Copy the selected archive, manifest, and checksum to a temporary directory owned by the administrative user with modes `0700` and `0600`.
2. Transfer the three files to the approved private Windows export folder using SCP.
3. Calculate SHA-256 independently with `Get-FileHash`.
4. Compare the calculated value to the sidecar.
5. Keep the root-owned server original and verified Windows copy.
6. Remove only the temporary server-side transfer copy.

Do not place the private export directory inside the Git repository.

## 7. Verify retention

The script retains the newest 30 `.tar.gz` archives. When an archive expires, its matching manifest and checksum are removed in the same run.

Review the set count:

```bash
sudo find /var/backups/leanops-shares -maxdepth 1 \
-type f -name 'leanops-shares-*.tar.gz' | wc -l
```

Do not manually delete one sidecar from a retained set.

## Troubleshooting order

1. Inspect the service result and journal.
2. Confirm the source and destination directories exist.
3. Check root-disk capacity.
4. Check for the lock file and an active backup process.
5. Confirm Samba and the health-monitor timer returned to their prior states.
6. Validate Bash syntax.
7. Verify archive listing and checksum.
8. Confirm artifact ownership and modes.
9. Confirm the timer remains active and enabled.
10. Confirm the three backup automation files remain in the 21-source configuration allowlist.

## Rollback

- Preserve the latest successful backup and relevant journal evidence.
- Stop and disable the share-backup timer.
- Restore the previous script and unit files from the verified configuration package.
- Run `systemctl daemon-reload`.
- Re-enable only the intended timer.
- Confirm Samba, health monitoring, and failed-unit state.
- Restore snapshot `25-PDCA13-FileServiceVerified` or `26-PDCA13-FileServiceRecoveryVerified` if configuration-level recovery is insufficient.
