# Security Considerations

## Isolation

- The lab VM uses a VirtualBox host-only adapter for administration and scanning.
- The NAT adapter supports outbound updates without router port forwarding.
- No service is intentionally exposed to the public internet.
- Scans target only the owned Ubuntu VM.

## Current access controls

- SSH is required for remote administration and listens on TCP port 22.
- SSH public-key authentication is enabled for `leanopsadmin`.
- SSH password and keyboard-interactive authentication are disabled.
- The private key remains on the Windows administrative workstation and is protected by a passphrase.
- UFW is active with incoming traffic denied and outgoing traffic allowed by default.
- TCP port 22 is allowed only from the Windows host-only address `192.168.244.1`.
- Routed traffic is disabled in the current UFW policy.
- Apache remains installed but stopped and disabled.
- Ubuntu package updates were applied before the first service cycle.

## Configuration backup controls

- `/var/backups/leanops` is owned by `root:root` with mode `700`.
- The root-controlled allowlist has mode `600` and limits each archive to nine approved regular files.
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
- The health-check script is included in the nine-file configuration backup.

## Incident-evidence controls

- `/var/log/leanops-incidents` is owned by `root:root` with mode `700`.
- `/usr/local/sbin/leanops-incident-collect` is owned by `root:root` with mode `700`.
- Each collection uses a unique temporary directory, a restrictive `umask`, and an EXIT cleanup trap limited to the expected `/tmp` prefix.
- Evidence is limited to 12 defined sources rather than unrestricted copies of `/var/log` or configuration directories.
- Authentication evidence includes only recent `sshd` entries; UFW evidence is limited to the last 100 lines.
- MAC addresses and UFW `SRC` and `DST` values are replaced before packaging.
- IPv4-only interface and route commands avoid collecting generated interface IPv6 addresses.
- Every evidence archive receives a manifest and SHA-256 checksum, and all artifacts have mode `600`.
- The collector records command exit codes, allowing unavailable or failed evidence sources to remain visible.
- The collector script is included in the nine-file configuration backup.

## Evidence sanitization

Before publication, screenshots and copied output must be checked for:

- Personal Windows usernames and paths
- Real home-network addresses
- Passwords, tokens, private keys, and authentication material
- SSH fingerprints when they add no documentation value
- Machine IDs, boot IDs, and unnecessary MAC addresses
- Browser tabs or notifications containing unrelated personal information

The fictional lab addresses `10.0.2.0/24` and `192.168.244.0/24` may be documented because they identify only the isolated virtual environment.

## Known constraints and remaining risks

- Proton VPN blocked the host-only connection during testing. Current standard work requires disconnecting it during lab access.
- The host-only VM uses static address `192.168.244.10/24`, outside the VirtualBox DHCP pool. Configuration changes must preserve the lack of a default gateway on this interface.
- Loss of the Windows private key would require recovery through the VirtualBox console or a verified snapshot. A separate key-backup process has not yet been established.
- The SSH firewall rule depends on the Windows host-only address remaining `192.168.244.1`.
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
- The collector packages local evidence on demand. It does not provide centralized logging, tamper-resistant remote storage, alerting, or continuous monitoring.
