# PDCA 02: Stabilize the Host-Only Administration Address

## Summary

The Ubuntu server originally received `192.168.244.100/24` from VirtualBox DHCP. The lab documentation and administration commands depended on that address, but the lease could change. A persistent static address outside the DHCP pool was configured for the host-only interface and verified without disrupting NAT, DNS, SSH, or the service baseline from Cycle 01.

## Plan

### Current condition

- `enp0s3` received `10.0.2.15/24` through VirtualBox NAT DHCP.
- `enp0s8` received `192.168.244.100/24` through VirtualBox host-only DHCP.
- The default route used `10.0.2.2` through `enp0s3`.
- Runbooks and tests referenced a DHCP-assigned administration address.
- `networkctl status enp0s8` showed that a generated dracut fallback file managed the interface.

### Expected result

- `enp0s8` uses persistent address `192.168.244.10/24`.
- The address remains outside the DHCP pool of `.100` through `.200`.
- No gateway is added to `enp0s8`.
- The default route remains on `enp0s3`.
- Windows ping and SSH tests succeed at `.10`.
- Only required TCP port 22 remains externally open.
- NAT internet access and DNS resolution continue to work.
- The address survives reboot.

### Test method

1. Inspect interfaces and routes with `ip -br address` and `ip route`.
2. Confirm the selected network file with `networkctl status enp0s8 --no-pager`.
3. From Windows, run ping, `Test-NetConnection`, Nmap, and an SSH login against `.10`.
4. From Ubuntu, ping `1.1.1.1` and resolve `archive.ubuntu.com`.
5. Reboot and repeat address, route, Nmap, and SSH checks.

### Risks and rollback

- An incorrect match rule could leave the DHCP configuration active.
- An incorrect address could interrupt host-only SSH access.
- Adding a gateway to the host-only interface could disrupt outbound routing.
- The VM console remained available during the change.
- Snapshot `04-PDCA02-PreStaticAddress` preserved the verified DHCP baseline.
- File removal followed by reboot would return the interface to the generated fallback configuration.

## Do

A persistent networkd file was created:

```ini
[Match]
Name=enp0s8

[Network]
Address=192.168.244.10/24
DHCP=no
LinkLocalAddressing=ipv6
```

The configuration was loaded with:

```bash
sudo networkctl reload
sudo networkctl reconfigure enp0s8
```

### Unexpected result and correction

The first activation left `.100` in place. `networkctl status` proved that the generated `/run/systemd/network/zzzz-dracut-default.network` file was still selected. Inspection found that the match key had been entered as `me=enp0s8` instead of `Name=enp0s8`.

The key was corrected and the file was verified with line numbers before reloading it. Networkd then selected `/etc/systemd/network/20-leanops-enp0s8.network`, released the DHCP lease, and assigned `.10`.

## Check

### Sanitized evidence summary

This compact summary is derived from the observed test results. Unique identifiers and unrelated terminal output are omitted.

```text
BEFORE
enp0s8: 192.168.244.100/24 via DHCP

AFTER REBOOT
enp0s8: 192.168.244.10/24 static
default route: 10.0.2.2 via enp0s3
22/tcp open  ssh
999 commonly scanned TCP ports closed
ping: 4 replies, 0% loss
DNS resolution: successful
SSH login: successful
```

| Test | Before | After | Result |
|---|---|---|---|
| `enp0s8` address | DHCP `192.168.244.100/24` | Static `192.168.244.10/24` | Passed |
| Default route | `10.0.2.2` through `enp0s3` | Unchanged | Passed |
| Windows ping | Worked at `.100` | Four replies at `.10`, zero loss | Passed |
| TCP 22 test | Reachable at `.100` | `TcpTestSucceeded : True` at `.10` | Passed |
| Nmap | TCP 22 open | TCP 22 open; 999 common ports closed | Passed |
| Direct internet test | Not part of address baseline | Four replies from `1.1.1.1`, zero loss | Passed |
| DNS test | Not part of address baseline | `archive.ubuntu.com` resolved | Passed |
| SSH login | Worked at `.100` | Worked at `.10` after reboot | Passed |
| Reboot persistence | DHCP lease | `.10` retained | Passed |

Apache remained disabled, and TCP port 80 did not reappear.

## Act

The new standard host-only administration address is `192.168.244.10/24`. Configuration is stored in:

```text
/etc/systemd/network/20-leanops-enp0s8.network
```

The host-only interface must not contain a default gateway. VirtualBox DHCP remains enabled for future guests, but its `.100` through `.200` pool does not include the server's `.10` address.

Standard verification and recovery steps are documented in:

- [`../runbooks/verify-host-only-connectivity.md`](../runbooks/verify-host-only-connectivity.md)
- [`../runbooks/configure-static-host-only-address.md`](../runbooks/configure-static-host-only-address.md)

The completed state is preserved in snapshot `05-PDCA02-StaticAddressVerified`.

## Lessons learned

- A valid filename does not prove that networkd selected the file.
- `networkctl status` provides stronger evidence by identifying the active configuration source.
- Verifying the saved configuration before activation limits avoidable troubleshooting.
- A network change is incomplete until routing, required services, internet access, DNS, and reboot persistence have all been retested.
