# Security Considerations

## Isolation

- The lab VM uses a VirtualBox host-only adapter for administration and scanning.
- The NAT adapter supports outbound updates without router port forwarding.
- No service is intentionally exposed to the public internet.
- Scans target only the owned Ubuntu VM.

## Current access controls

- SSH is required for remote administration and listens on TCP port 22.
- SSH public-key authentication is enabled for the designated administrative account.
- SSH password and keyboard-interactive authentication are disabled.
- The private key remains on the Windows administrative workstation and is protected by a passphrase.
- UFW is active with incoming traffic denied and outgoing traffic allowed by default.
- TCP port 22 is allowed only from the approved Windows host-only administration address.
- Routed traffic is disabled in the current UFW policy.
- Apache remains installed but stopped and disabled.
- Ubuntu package updates were applied before the first service cycle.

## Configuration backup controls

- `/var/backups/leanops` is owned by `root:root` with mode `700`.
- The root-controlled allowlist has mode `600` and limits each archive to eleven approved regular files.
- The backup script has mode `700` and rejects absolute paths, parent-directory traversal, missing files, and symbolic-link sources.
- Archives, manifests, and checksum files have mode `600`.
- Backup scope excludes private SSH keys, `authorized_keys`, password databases, logs, and machine-specific identifiers.
- Each archive is listed after creation and receives a SHA-256 checksum.
- Restoration testing occurs in an isolated temporary directory before any live replacement is considered.
- A verified package is stored off the VM on the Windows administrative workstation.

## Health-check controls

- `/usr/local/sbin/leanops-health-check` is owned by `root:root` with mode `700`.
- The script must run with `sudo` because it reads firewall and protected-backup state.
- Output reports only operational status, percentages, counts, and fictional lab addresses. It does not display configuration contents or checksum values.
- Required-state failures return exit code `2`; warnings return `1`; an all-pass result returns `0`.
- A controlled Apache failure was protected by an EXIT trap that restored the required inactive state.
- The health-check script and both scheduled-monitoring unit files are included in the eleven-file configuration backup.

## Scheduled-monitoring controls

- `leanops-health-monitor.service` is a root-owned oneshot unit; `leanops-health-monitor.timer` is enabled and persistent.
- The timer runs approximately every 15 minutes and schedules its first post-boot run after five minutes.
- The service now launches `/usr/local/sbin/leanops-health-event-handler`, which runs the existing health check under an exclusive lock and passes its output to the Python processor.
- `SuccessExitStatus=1 2` accepts health warnings and processed health failures because both are recorded and escalated by the processor. Exit code `3` remains a failed monitoring service.
- Output and errors are recorded in the system journal.
- `NoNewPrivileges=true`, `PrivateTmp=true`, and `ProtectHome=true` reduce service exposure.
- `ProtectSystem=full` keeps `/usr`, `/boot`, and `/etc` read-only while allowing UFW's required runtime lock under `/run`.
- Controlled failure testing pauses the timer and uses an EXIT trap to stop Apache and restart scheduling.
- Both unit files are protected by the eleven-source configuration backup.
- Reboot verification confirms timer enablement, activation, and automatic execution.

## Health-event processing controls

- The handler and processor are owned by `root:root` with mode `700`.
- The handler waits up to 30 seconds for an exclusive lock and returns code `3` if the monitoring pipeline cannot proceed safely.
- Stable condition identifiers keep changing measurements, such as package counts or percentages, in one condition history.
- Unknown abnormal messages and mismatches between parsed results and health exit codes return code `3` instead of being silently discarded.
- `/var/lib/leanops-health-monitor` and `/var/log/leanops-health-events` are `700 root:root`; their state and event files are `600 root:root`.
- Every abnormal cycle is recorded. Generic healthy runs are not added to the event log, but recovery from a previously active condition is recorded.
- Warning evidence becomes due on the fourth consecutive occurrence. Failure evidence becomes due on the first occurrence. Recovery clears the active count and evidence latch.
- The four-occurrence count and recovery reset were verified. Final collector invocation and duplicate suppression after the integrated trigger remain to be observed.

## Incident-evidence controls

- `/var/log/leanops-incidents` is owned by `root:root` with mode `700`.
- `/usr/local/sbin/leanops-incident-collect` is owned by `root:root` with mode `700`.
- Each collection uses a unique temporary directory, a restrictive `umask`, and an EXIT cleanup trap limited to the expected `/tmp` prefix.
- Evidence is limited to 12 defined sources rather than unrestricted copies of `/var/log` or configuration directories.
- Authentication evidence includes only recent `sshd` entries; UFW evidence is limited to the last 100 lines.
- MAC addresses and UFW `SRC` and `DST` values are replaced before packaging.
- IPv4-only interface and route commands avoid collecting generated interface IPv6 addresses.
- Every evidence archive receives a manifest and SHA-256 checksum, and all artifacts have mode `600`.
- Raw incident evidence is subject to a 180-day `systemd-tmpfiles` policy.
- The collector records command exit codes, allowing unavailable or failed evidence sources to remain visible.
- The collector script is included in the eleven-file configuration backup.

## Incident-response controls

- Controlled network-failure testing is performed only in the isolated VM after a healthy baseline and recovery snapshot are verified.
- The host-only administration path is kept separate from the NAT route under test.
- Evidence is collected before recovery whenever access and safety permit.
- Diagnosis compares interface state, connected routes, the default route, service health, and firewall state before selecting a corrective action.
- Recovery actions are attempted one at a time in the order DHCP renewal, interface reconfiguration, reboot, then snapshot restoration.
- A failed recovery step is recorded rather than hidden by an unrelated configuration change.
- Recovery is not complete until the health check passes without failures, a fresh key-only SSH session succeeds, and the state persists after reboot.
- Required evidence is transferred off the VM and independently verified with SHA-256 before temporary export data is removed.

## Evidence sanitization

Before publication, screenshots and copied output must be checked for:

- Personal Windows usernames and paths
- Real home-network addresses
- Passwords, tokens, private keys, and authentication material
- SSH fingerprints when they add no documentation value
- Machine IDs, boot IDs, and unnecessary MAC addresses
- Browser tabs or notifications containing unrelated personal information

Public documentation uses role-based placeholders for host and subnet addresses unless a specific lab value is essential to understanding the test.

## Known constraints and remaining risks

- Proton VPN blocked the host-only connection during testing. Current standard work requires disconnecting it during lab access.
- The host-only VM uses a static address outside the VirtualBox DHCP pool. Configuration changes must preserve the lack of a default gateway on this interface.
- Loss of the Windows private key would require recovery through the VirtualBox console or a verified snapshot. A separate key-backup process has not yet been established.
- The SSH firewall rule depends on the approved Windows host-only administration address remaining stable.
- The NAT adapter should be disconnected before any future exercise that intentionally creates a higher-risk service condition.
- Installed but disabled Apache packages still require updates while retained for rollback.
- The package protects selected configuration files only. It is not a full-system backup and does not preserve installed packages, user data, SSH host keys, or the VM itself.
- SHA-256 detects corruption or unexpected changes but does not authenticate who created the archive.
- Because `authorized_keys` is intentionally excluded, administrative public-key access must be provisioned before restoring the key-only SSH configuration to a replacement server.
- The Windows backup currently represents one off-VM copy. A separate encrypted or versioned backup destination has not yet been established.
- Package-update results use the current local APT cache. They do not prove that package metadata was refreshed immediately before the check.
- The internet check depends on ICMP replies from `1.1.1.1`; an upstream ICMP policy could produce a failure even when other outbound traffic works.
- Incident archives can still contain operational details such as service names, package names, fictional lab addresses, timestamps, and authentication outcomes. They remain protected and are not published raw.
- Sanitization covers the observed MAC, UFW address-field, and generated local IPv6 risks. It is not a universal data-loss-prevention system.
- The collector packages local evidence on demand. It does not provide centralized logging or tamper-resistant remote storage.
- Health-event records rotate daily, retain up to 180 rotations, expire after 180 days, and compress older rotations.
- Scheduled monitoring remains local and does not send remote notifications.
- The new handler, processor, and retention policies have not yet been added to a newly verified configuration-backup package.
- Automatic collector invocation after the final handler integration has not yet been exercised at a real warning or failure threshold.
- Successful DNS resolution during a short route failure may reflect cached resolver state and does not prove full outbound connectivity.
- Reconfiguring a network interface can briefly interrupt traffic on that interface and requires an independent administrative path or console fallback.
