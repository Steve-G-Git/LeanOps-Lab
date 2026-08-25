# Runbook: Manage the Role-Based File Service

## Purpose

Verify, operate, troubleshoot, and recover the LeanOps Samba file service without exposing it beyond the isolated host-only network or weakening role-based access.

## Preconditions

- Key-authenticated SSH or VirtualBox console access
- Root access through `sudo`
- Approved fictional Samba users and Linux groups
- UFW active with default-deny inbound policy
- Current recovery snapshot
- No uncontrolled file-service test in progress

## 1. Verify the service and configuration

```bash
systemctl is-enabled smbd
systemctl is-active smbd
sudo testparm -s
systemctl --failed --no-pager
```

Required configuration characteristics:

- standalone user security;
- SMB2 minimum;
- TCP 445 direct hosting;
- `lo` and `enp0s8` only;
- host-only subnet allowlist and deny-all fallback;
- NetBIOS, printing, spooler, and DNS proxy disabled;
- no guest shares.

Stop if `testparm` reports an error.

## 2. Verify the firewall boundary

```bash
sudo ufw status verbose
sudo ss -lntp | grep ':445'
```

TCP 445 must be allowed only on `enp0s8` from the approved Windows host-only address. Do not add router port forwarding or an unrestricted `445/tcp ALLOW Anywhere` rule.

## 3. Verify identities and groups

```bash
getent group leanops-users
getent group operations
getent group management
sudo pdbedit -L
```

Expected fictional membership:

| Group | Members |
|---|---|
| `leanops-users` | Alex, Jordan, Morgan |
| `operations` | Alex, Jordan |
| `management` | Morgan |

Do not publish Samba password material or password-setting output.

## 4. Verify filesystem permissions

```bash
sudo find /srv/leanops-shares -maxdepth 2 -type d \
-printf '%m %u:%g %p\n' | sort
```

Expected model:

| Path type | Mode | Ownership |
|---|---:|---|
| Share root | `0711` | `root:root` |
| Users root | `0711` | `root:root` |
| Company share | `2770` | `root:leanops-users` |
| Operations share | `2770` | `root:operations` |
| Management share | `2770` | `root:management` |
| Individual private directory | `0700` | matching fictional user |

The setgid bit on collaborative directories keeps new content in the correct group.

## 5. Validate access from Windows

Use only fictional lab accounts. Verify:

1. Every approved user can reach `CompanyShared`.
2. Operations members can reach `Operations`.
3. Non-operations users are denied `Operations`.
4. Management members can reach `Management`.
5. Non-management users are denied `Management`.
6. Each user reaches only their own `Private` directory.
7. A Windows-created file receives the required Linux ownership and mode.
8. Access-based enumeration does not advertise unauthorized shares.

Do not reuse a cached Windows SMB session when testing another identity. Disconnect existing mappings first:

```powershell
net use * /delete
```

This removes active SMB mappings from the Windows session. It does not delete server data.

## 6. Review Samba logs

```bash
sudo journalctl -u smbd.service -n 80 --no-pager
sudo find /var/log/samba -maxdepth 1 -type f -name 'log.*' -printf '%f\n' | sort
```

Review only the minimum required log window. Raw logs remain protected and are not committed to Git.

## 7. Apply a controlled configuration change

1. Preserve the current file and snapshot.
2. Edit `/etc/samba/smb.conf`.
3. Run `sudo testparm -s`.
4. Reload Samba only after validation:

```bash
sudo systemctl reload smbd
```

5. Recheck UFW, listening sockets, allowed access, denied access, health monitoring, and failed units.
6. Add any new non-secret configuration file to `/etc/leanops-backup-files` and reverify configuration recovery.

## Troubleshooting order

1. Confirm the Windows VPN is disconnected if host-only traffic is unavailable.
2. Confirm `enp0s8` and the host-only route.
3. Confirm UFW permits the approved Windows source.
4. Confirm `smbd` is active and listening on TCP 445.
5. Validate `smb.conf` with `testparm`.
6. Confirm the fictional user exists in Linux and Samba.
7. Confirm group membership.
8. Confirm directory ownership, setgid bit, and mode.
9. Remove cached Windows SMB mappings and retest.
10. Review the smallest relevant journal and Samba log window.

## Rollback

- Preserve current share data and relevant logs.
- Restore the previous `smb.conf` and validate it with `testparm`.
- Reload or restart Samba.
- Remove only the Cycle 13 UFW rule if rolling back the service.
- Stop and disable `smbd` only when the intended rollback removes file sharing.
- Verify SSH remains available and no unexpected failed units exist.
- Restore snapshot `24-PDCA13-PreFileService` only when file-level rollback is insufficient and required share data has already been preserved.
