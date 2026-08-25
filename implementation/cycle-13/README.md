# PDCA 13 File-Service Implementation

This directory contains the sanitized, non-secret implementation used for the
LeanOps-Lab role-based Samba service and scheduled share-data backup.

The public files contain fictional users and isolated lab addresses only. They
do not contain Samba passwords, raw share data, backup archives, raw manifests,
per-file hashes, or private export packages.

## Layout

- `samba/smb.conf`: verified effective Samba settings for the lab
- `bin/leanops-share-backup`: locked, integrity-checked share-data backup
- `systemd/leanops-share-backup.service`: root-owned oneshot service
- `systemd/leanops-share-backup.timer`: persistent daily schedule

## Control boundary

Samba binds only to loopback and the VirtualBox host-only interface. UFW
separately restricts TCP 445 to the approved Windows host-only address.

The share-data backup is separate from the selected-configuration backup. It
temporarily pauses Samba and the health-monitor timer, preserves the prior
service states, writes protected metadata and integrity artifacts, and retains
the newest 30 backup sets.

## Recovery coverage

The final 21-source selected-configuration package protects:

- `/etc/samba/smb.conf`
- `/usr/local/sbin/leanops-share-backup`
- `/etc/systemd/system/leanops-share-backup.service`
- `/etc/systemd/system/leanops-share-backup.timer`

Snapshot `26-PDCA13-FileServiceRecoveryVerified` preserves the final verified
Cycle 13 state.
