# PDCA 13: Role-Based File Service and Share-Data Backup

## Summary

Cycle 13 added a controlled Samba file service for a fictional small-business environment. Access is limited to the isolated host-only network and divided into company-wide, department, and per-user shares. The cycle also added a separate protected backup process for share data, because the existing selected-configuration backup did not protect user-created files.

The file service, role-based access, firewall boundary, health-monitor integration, alert recovery, daily backup timer, archive integrity, isolated restoration, off-VM transfer, and final recovery coverage passed. During documentation review, the configuration-backup allowlist was found to protect Samba configuration but not the new share-backup script or units. Those three sources were added, expanding configuration recovery from 18 to 21 approved non-secret files. The corrected package passed checksum, exact-scope, content, metadata, and Windows transfer verification.

## Plan

### Current condition and problem

The lab had secure administration, monitoring, notification, incident evidence, and selected-configuration recovery, but it did not provide a business file service. Adding a file service would introduce new risks:

- TCP 445 could be exposed too broadly.
- Department or private data could be readable by the wrong fictional user.
- Shared files could receive inconsistent ownership or permissions.
- A backup taken during writes could be inconsistent.
- The data backup could overlap with monitoring or another backup.
- Local backups could accumulate without a defined limit.
- New backup automation could remain outside the existing configuration-recovery boundary.

### Expected result

- Provide one company share for all approved fictional users.
- Provide department shares limited to their matching groups.
- Provide a private share that resolves separately for each authenticated user.
- Require authenticated SMB2 or newer.
- Bind Samba to loopback and the host-only interface only.
- Permit TCP 445 only from the approved Windows host-only address.
- Disable NetBIOS, printing, guest access, and unnecessary Samba services.
- Apply setgid group directories and controlled file-creation modes.
- Back up share data daily into root-only archives, manifests, and checksums.
- Prevent overlapping backup runs.
- Stop Samba and the health-monitor timer during archive creation, then restore their prior states even after failure.
- Preserve ACLs, extended attributes, numeric ownership, permissions, and file hashes.
- Retain the newest 30 share-data backup sets.
- Verify restoration in isolation before adopting the process.
- Transfer a verified backup copy off the VM.
- Protect all new non-secret configuration and automation through the selected-configuration backup.

### Test and rollback plan

- Preserve snapshot `24-PDCA13-PreFileService`.
- Validate Samba configuration before service activation.
- Verify allowed and denied access with fictional user accounts.
- Confirm Windows-created files receive the required ownership and modes.
- Verify only TCP 22 and source-restricted TCP 445 are permitted through UFW.
- Confirm the health-monitor pipeline detects the new required service and returns to normal after controlled testing.
- Validate the backup script, systemd units, lock behavior, service restoration, archive integrity, retention, and timer state.
- Restore the archive only into an isolated directory and compare expected data and metadata.
- Independently verify the exported archive on Windows.
- Preserve snapshot `25-PDCA13-FileServiceVerified`.
- Audit recovery coverage, correct any gap, reverify, and preserve the final closure snapshot.

Rollback options were, in order:

1. Stop and disable the share-backup timer.
2. Remove the TCP 445 UFW rule.
3. Stop and disable Samba.
4. Restore pre-change Samba, firewall, monitoring, and backup files.
5. Preserve share data before removing any service configuration.
6. Restore snapshot `24-PDCA13-PreFileService` if file-level rollback was insufficient.

## Do

### Added a host-only Samba service

The effective Samba standard uses:

- standalone user security;
- SMB2 as the minimum protocol;
- direct hosting on TCP 445;
- loopback and `enp0s8` binding only;
- an allowlist for loopback and the host-only subnet;
- a deny-all fallback;
- disabled NetBIOS, printing, spooler, and DNS proxy functions;
- access-based share enumeration.

UFW allows TCP 445 on `enp0s8` only from the approved Windows host-only address. No router port forwarding or public exposure was added.

### Added role-based shares

| Share | Filesystem path | Authorized identity | New file mode | New directory mode |
|---|---|---|---:|---:|
| `CompanyShared` | `/srv/leanops-shares/company-shared` | `@leanops-users` | `0660` | `02770` |
| `Operations` | `/srv/leanops-shares/operations` | `@operations` | `0660` | `02770` |
| `Management` | `/srv/leanops-shares/management` | `@management` | `0660` | `02770` |
| `Private` | `/srv/leanops-shares/users/%U` | authenticated `%U` only | `0600` | `0700` |

The fictional users are Alex, Jordan, and Morgan. Department membership separates operations and management access. The company share forces the common group; department shares force their department group; private directories remain owned and accessible by the individual user.

### Added protected share-data backup automation

`/usr/local/sbin/leanops-share-backup`:

- runs as root with `umask 077`;
- uses a non-blocking `flock` lock;
- refuses a missing source directory;
- creates `/var/backups/leanops-shares` as `0700 root:root`;
- records whether Samba and the health-monitor timer were active;
- pauses both services for a consistent backup boundary;
- uses an EXIT trap to restore their prior states;
- writes temporary artifacts before atomic promotion;
- records filesystem metadata and per-file SHA-256 hashes in a protected manifest;
- archives ACLs, extended attributes, and numeric ownership;
- lists the archive to reject a corrupt output;
- creates an archive SHA-256 sidecar;
- protects all artifacts as `0600 root:root`;
- retains the newest 30 archive sets with their matching manifests and checksums.

The persistent systemd timer schedules the service daily at 02:30 with up to five minutes of randomized delay.

### Closed the configuration-recovery gap

Initial Cycle 13 closure had expanded the selected-configuration allowlist from 17 to 18 sources by adding `/etc/samba/smb.conf`. Documentation review found that the new backup script, service, and timer were still outside that recovery package.

The following were added:

- `usr/local/sbin/leanops-share-backup`
- `etc/systemd/system/leanops-share-backup.service`
- `etc/systemd/system/leanops-share-backup.timer`

The final selected-configuration scope is 21 approved non-secret sources.

## Check

### Before and after

| Before | After |
|---|---|
| No business file-sharing service | Authenticated, role-based Samba shares on the isolated network |
| No department separation | Operations and management shares enforce group membership |
| No per-user network storage | Private share resolves to the authenticated user's directory |
| No inbound SMB rule | TCP 445 permitted only on `enp0s8` from the approved Windows host |
| Selected-configuration backup intentionally excluded user data | Separate protected share-data backup preserves files and metadata |
| No scheduled share-data recovery point | Persistent daily timer creates a consistent archive set |
| New backup automation was initially outside configuration recovery | Corrected 21-source configuration package protects Samba and backup automation |
| Latest recovery point was Cycle 12 | Snapshot `26-PDCA13-FileServiceRecoveryVerified` preserves final Cycle 13 closure |

### Sanitized validation evidence

See [`../../evidence/sanitized/pdca-13-file-service-validation.txt`](../../evidence/sanitized/pdca-13-file-service-validation.txt).

| Verification | Result |
|---|---|
| Effective Samba configuration | Passed |
| Samba service enabled and active | Passed |
| SMB2 minimum and TCP 445 direct hosting | Passed |
| Host-only binding and subnet allowlist | Passed |
| Source-restricted UFW rule for TCP 445 | Passed |
| Company, department, and private access behavior | Passed |
| Share directory ownership and permission model | Passed |
| Windows file creation through approved shares | Passed |
| Health monitoring and alert recovery | Passed |
| Share-backup script and systemd units | Passed |
| Backup lock and prior-service restoration | Passed |
| Protected archive, manifest, and checksum modes | Passed; `0600 root:root` |
| Daily persistent timer | Passed; enabled and active |
| Latest scheduled backup service result | Passed; exit status 0 |
| Share-data archive integrity and isolated restoration | Passed |
| Share-data Windows transfer checksum | Passed |
| Final configuration-backup scope | Passed; 21 approved sources |
| Configuration archive checksum | Passed |
| Configuration archive exact scope | Passed; 21 entries |
| Isolated configuration restore | Passed; 21 of 21 present |
| Restored configuration content | Passed; zero mismatches |
| Restored configuration metadata | Passed; zero mismatches |
| Configuration Windows transfer checksum | Passed |
| Final service state | Passed; Samba and both timers active and enabled |
| Failed units | Zero |
| Final recovery checkpoint | Snapshot `26-PDCA13-FileServiceRecoveryVerified` created |

## Act

### Adopted standard

- Run Samba only on loopback and the isolated host-only interface.
- Permit SMB only from the approved Windows host through UFW.
- Require authenticated SMB2 or newer and disable unnecessary legacy functions.
- Use groups for company and department authorization.
- Use `%U` with `0700` directories and `0600` files for private shares.
- Use setgid department directories and forced groups for collaborative shares.
- Run the share-data backup daily through the persistent timer.
- Prevent overlapping runs and restore paused services through the EXIT trap.
- Protect backup directories as `0700` and artifacts as `0600`.
- Retain the newest 30 share-data backup sets.
- Keep raw share archives, manifests, file inventories, and hashes out of Git.
- Verify archives before restoration and restore into isolation first.
- Maintain an independently verified off-VM copy.
- Include all non-secret Samba and share-backup automation in the 21-source configuration backup.

### Recovery points

- `24-PDCA13-PreFileService`: pre-change Cycle 12 baseline.
- `25-PDCA13-FileServiceVerified`: file service and initial recovery controls verified.
- `26-PDCA13-FileServiceRecoveryVerified`: final 21-source recovery coverage and off-VM verification passed.

### Standard work

- [Manage the role-based file service](../runbooks/manage-role-based-file-service.md)
- [Manage share-data backups](../runbooks/manage-share-data-backups.md)

Cycle 13 is technically verified, documented on `pdca-13-file-service`, and ready for branch review.
