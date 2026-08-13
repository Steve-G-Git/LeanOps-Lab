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
