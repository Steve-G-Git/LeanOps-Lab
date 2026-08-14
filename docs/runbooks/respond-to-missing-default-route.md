# Runbook: Respond to a Missing Default Route

## Purpose

Detect, preserve, diagnose, recover, and verify a missing IPv4 default route on the LeanOps Ubuntu server without making unrelated changes.

## Preconditions

- Key-authenticated SSH or VirtualBox console access
- Root access through `sudo`
- Host-only administration available through `enp0s8`
- NAT normally provided through `enp0s3`
- Standard health check and evidence collector installed
- A current verified snapshot or configuration backup
- No unrelated maintenance in progress

## 1. Record the reported condition

Run the standard health check:

```bash
sudo /usr/local/sbin/leanops-health-check
health_rc=$?
echo "EXIT_CODE=$health_rc"
```

Record the UTC time, summary, failed lines, and exit code.

## 2. Preserve evidence before correction

If access and safety permit:

```bash
sudo /usr/local/sbin/leanops-incident-collect route-missing
collector_rc=$?
echo "EXIT_CODE=$collector_rc"
```

Record the generated incident identifier and verify its checksum before changing network state.

## 3. Confirm administrative access

Verify that the independent host-only interface remains available:

```bash
ip -4 -br address show enp0s8
```

Expected lab state:

```text
enp0s8 UP 192.168.244.10/24
```

Keep the working SSH session open. When practical, retain VirtualBox console access as a fallback.

## 4. Diagnose the smallest failed component

Check the NAT interface and default route:

```bash
ip -4 -br address show enp0s3
ip -4 route show default
ip -4 route
systemctl is-active systemd-networkd
```

Interpretation:

| Observation | Likely scope |
|---|---|
| `enp0s3` down or missing its address | Interface or DHCP problem |
| `enp0s3` up with an address but no default route | Route or DHCP configuration problem |
| Default route present but internet check fails | Upstream reachability or ICMP-specific problem |
| Host-only SSH unavailable | Administration-path problem requiring console access |
| UFW state changed | Firewall problem requiring separate investigation |

Do not treat successful DNS resolution by itself as proof that outbound routing is healthy. Cached resolver state may remain available briefly.

## 5. Recover one step at a time

### Step 1: Renew DHCP state

```bash
sudo networkctl renew enp0s3
ip -4 route show default
```

If the default route is still absent, continue to Step 2.

### Step 2: Reconfigure the NAT interface

```bash
sudo networkctl reconfigure enp0s3
```

Wait briefly, then verify:

```bash
ip -4 route show default
```

Expected lab route:

```text
default via 10.0.2.2 dev enp0s3 proto dhcp src 10.0.2.15 metric 100
```

If the route is still absent, inspect `networkctl status enp0s3 --no-pager` and the recent network journal before considering a reboot.

### Step 3: Reboot only if required

Use a reboot only after evidence is preserved and smaller recovery actions fail:

```bash
sudo reboot
```

Reconnect through the host-only address and recheck the route.

### Step 4: Restore the verified snapshot

If normal configuration cannot be recovered safely, power off the VM and restore the latest verified snapshot. For the completed Cycle 08 state, use `17-PDCA08-IncidentResponseVerified`. For the verified pre-drill state, use `16-PDCA08-PreIncidentDrill`.

## 6. Verify complete recovery

Rerun the standard health check:

```bash
sudo /usr/local/sbin/leanops-health-check
health_rc=$?
echo "EXIT_CODE=$health_rc"
```

Confirm:

- NAT default route present
- Internet target reachable
- DNS working
- SSH active
- UFW state and policy unchanged
- Static host-only address present
- No new failures

Establish a new key-only SSH session from Windows to prove that recovery supports new connections rather than only the existing session.

## 7. Preserve the recovered state

```bash
sudo /usr/local/sbin/leanops-incident-collect route-recovered
collector_rc=$?
echo "EXIT_CODE=$collector_rc"
```

Verify the package checksum and inspect its health and network evidence.

## 8. Verify reboot persistence

Reboot the VM, reconnect through the host-only address, and repeat the route and health checks. Collect a post-reboot evidence package when the response requires preserved proof.

## 9. Transfer and validate evidence

Copy only the required archive, manifest, and checksum files through a temporary mode-`700` export directory. After SCP transfer, independently compute SHA-256 on Windows and compare it with each checksum file.

Remove only the temporary Ubuntu export directory after every destination verification passes. Retain the protected originals under `/var/log/leanops-incidents`.

## Escalation and safety

- Stop if the host-only administration path becomes unavailable.
- Use the VirtualBox console rather than guessing at remote network changes.
- Do not alter UFW, SSH, DNS, or static host-only configuration unless evidence identifies them as part of the failure.
- Do not add a permanent manual route to hide an unresolved DHCP or interface-management problem.
- Preserve failed recovery attempts in the incident record.
- Never publish raw evidence packages or screenshots without a separate sanitization review.
