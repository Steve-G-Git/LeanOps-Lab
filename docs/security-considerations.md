# Security Considerations

## Isolation

- The lab VM uses a VirtualBox host-only adapter for administration and scanning.
- The NAT adapter supports outbound updates without router port forwarding.
- No service is intentionally exposed to the public internet.
- Scans target only the owned Ubuntu VM.

## Current access controls

- SSH is required for remote administration and listens on TCP port 22.
- SSH password authentication is currently enabled for the isolated learning lab.
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
- The host-only VM address is assigned by DHCP and may change within the configured pool.
- SSH password authentication could be replaced with key authentication in a future controlled cycle.
- The NAT adapter should be disconnected before any future exercise that intentionally creates a higher-risk service condition.
- Installed but disabled Apache packages still require updates while retained for rollback.
