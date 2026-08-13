# PDCA 04: Establish a UFW Host Firewall

## Summary

The Ubuntu server had no active host firewall. Its limited exposure depended on unnecessary services remaining stopped or disabled. UFW was configured with a default-deny inbound policy, default-allow outbound policy, and one TCP 22 rule restricted to the Windows host-only address `192.168.244.1`. Approved SSH, outbound internet access, DNS resolution, firewall state, and the rule survived reboot.

No raw screenshot is published because the observed terminal output included personal usernames, MAC addresses, or generated IPv6 details. The evidence below is a sanitized transcription of verified results.

## Plan

### Current condition and problem

- `ufw status verbose` reported `Status: inactive`.
- The UFW systemd service was enabled, but no firewall policy was being enforced.
- `ufw show added` reported no saved user rules.
- SSH listened on TCP port 22 over IPv4 and IPv6.
- Local DNS-related listeners were bound to loopback only.
- Apache was not listening on TCP port 80.
- From Windows at `192.168.244.1`, TCP 22 was reachable and Nmap reported 999 other commonly scanned TCP ports closed.

The server needed an explicit host-level policy so unsolicited inbound traffic would be denied even if another service began listening unexpectedly.

### Expected result

- UFW is active and enabled at startup.
- Incoming traffic is denied by default.
- Outgoing traffic is allowed by default.
- Routed traffic remains disabled.
- TCP 22 is allowed only from `192.168.244.1`.
- Existing and fresh key-authenticated SSH sessions continue working from the approved Windows endpoint.
- Outbound internet traffic and DNS resolution continue working.
- The firewall policy and SSH access survive reboot.
- No additional commonly scanned TCP ports become reachable.

### Test method

1. Inspect UFW status, service enablement, saved rules, and listening TCP sockets.
2. Record external TCP 22 reachability and the baseline Nmap result.
3. Create snapshot `08-PDCA04-PreUFW`.
4. Set the default policies and save one source-restricted SSH rule while UFW remains inactive.
5. Inspect the stored rule before enforcement.
6. Enable UFW while retaining the current SSH session and VirtualBox console access.
7. Inspect the active policy.
8. Open a second key-authenticated SSH session from Windows.
9. Test direct outbound connectivity and DNS resolution.
10. Repeat the Nmap scan.
11. Reboot and repeat SSH, UFW status, Nmap, and DNS checks.

### Risks and rollback

- Enabling UFW without an approved SSH rule could cause remote lockout.
- An overly broad rule would not achieve the intended least-privilege policy.
- An incorrect source address would block fresh SSH connections.
- Snapshot `08-PDCA04-PreUFW` preserved the verified Cycle 03 state before firewall rules were added.
- The original SSH session and VirtualBox console remained available during activation.
- Immediate rollback command: `sudo ufw disable`.

## Do

### Prepared policy

The default policies were saved while UFW remained inactive:

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
```

The single inbound rule was restricted to the Windows host-only endpoint:

```bash
sudo ufw allow from 192.168.244.1 to any port 22 proto tcp comment 'LeanOps SSH admin'
```

`ufw show added` confirmed the exact stored rule before enforcement. No general `OpenSSH` or unrestricted `22/tcp` rule was added.

### Activated firewall

UFW was enabled only after the rule was inspected:

```bash
sudo ufw enable
```

The active policy reported:

```text
Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), disabled (routed)
22/tcp ALLOW IN from 192.168.244.1
```

### Unexpected results and corrections

- Proton VPN initially caused Windows-to-VM failures even though the host-only adapter retained `192.168.244.1/24`. Fully exiting Proton restored SSH. No UFW change was made during that diagnosis.
- Several mistyped PowerShell connectivity commands produced only command errors. The shorter `tnc` alias confirmed TCP 22 reachability.
- Immediately after first enabling UFW, the rollback command `sudo ufw disable` was entered even though SSH had not disconnected. UFW stopped safely, its saved rule remained intact, and it was enabled again. The active policy was then verified before testing continued.
- A mistyped `getents` command changed nothing. The correct `getent` command verified DNS resolution.

## Check

### Sanitized evidence summary

```text
BEFORE
UFW: inactive
saved user rules: none
22/tcp open  ssh
999 commonly scanned TCP ports closed (reset)

AFTER REBOOT
UFW: active
default incoming: deny
default outgoing: allow
routed traffic: disabled
22/tcp allowed from 192.168.244.1 only
key-authenticated SSH: successful
22/tcp open  ssh
999 commonly scanned TCP ports filtered (no response)
DNS resolution: successful
```

| Verification | Result |
|---|---|
| Existing SSH session after activation | Remained connected |
| Fresh key-authenticated SSH session | Successful |
| Direct outbound ping | Four replies, zero packet loss |
| DNS resolution | Successful |
| Nmap after activation | TCP 22 open; 999 commonly scanned TCP ports filtered |
| Key-authenticated SSH after reboot | Successful |
| UFW after reboot | Active with intended defaults and restricted rule |
| Nmap after reboot | TCP 22 open; 999 commonly scanned TCP ports filtered |
| DNS after reboot | Successful |

The change produced measurable filtering without interrupting approved administration or required outbound functions.

## Act

### Final standard

- UFW remains active and enabled at startup.
- Incoming traffic is denied by default.
- Outgoing traffic is allowed by default.
- Routed traffic remains disabled.
- TCP 22 is allowed only from `192.168.244.1`.
- No unrestricted SSH rule is permitted without a documented requirement and controlled test.
- Any firewall change must keep an existing SSH session and the VirtualBox console available until a fresh connection succeeds.
- The final state is preserved in snapshot `09-PDCA04-UFWVerified`.

### Standard work and recovery

Repeatable configuration, verification, and recovery steps are documented in [`../runbooks/configure-ufw-host-firewall.md`](../runbooks/configure-ufw-host-firewall.md).

### Remaining risks

- The approved SSH rule depends on the Windows host-only address remaining `192.168.244.1`.
- Only the approved Windows endpoint was used for remote verification. Rejection from a separate unapproved host has not been tested.
- UFW logging remains at the low level and has not yet been evaluated as an operational monitoring source.
