# PDCA 01: Remove an Unnecessary HTTP Service

## Summary

An Apache HTTP service was introduced to simulate an undocumented legacy service on a small-business server. The service was confirmed internally and externally, evaluated as unnecessary for the fictional business, stopped, disabled, and retested. SSH remained available throughout the final verified state.

## Plan

### Current condition and problem

The clean server exposed only required SSH on TCP port 22. To create a controlled first exercise, Apache was installed as a simulated inherited web service. The fictional business has no requirement for this server to host a website, so TCP port 80 represented unnecessary exposure and maintenance work.

### Evidence

- Before Apache installation, Nmap reported only TCP 22 open.
- `apt-cache policy apache2` reported `Installed: (none)`.
- After installation, `systemctl is-active apache2` returned `active`.
- `ss -lntp` showed Apache listening on TCP port 80.
- `curl.exe -I` returned HTTP `200 OK`.
- Nmap reported TCP 22 and TCP 80 open.

### Expected result

- Apache is inactive.
- Apache does not start automatically after reboot.
- TCP port 80 is closed.
- TCP port 22 remains open.
- SSH login from Windows still works.

### Test method

1. Check Apache's runtime and startup states.
2. Attempt an HTTP header request from Windows.
3. Repeat the same Nmap scan used for the baseline.
4. Test TCP port 22 from PowerShell.
5. Reboot Ubuntu and repeat the Nmap and SSH tests.

### Risks

- Disabling the wrong service could interrupt remote administration.
- A command-entry mistake could enable rather than disable Apache.
- Proton VPN could block host-only traffic and produce a false failure.

### Rollback plan

Immediate service rollback:

```bash
sudo systemctl enable --now apache2
```

Full VM rollback: restore VirtualBox snapshot `02-HostOnlyNetworkVerified`.

## Do

### Controlled change

The intended command was:

```bash
sudo systemctl disable --now apache2
```

This stops Apache immediately and removes its automatic-start configuration.

### What actually happened

The rollback command was accidentally entered first:

```bash
sudo systemctl enable --now apache2
```

Verification correctly showed Apache as `active` and `enabled`. The mistake was recognized before proceeding. The intended disable command was then run, after which verification showed `inactive` and `disabled`.

### Other unexpected results during the milestone

- VirtualBox's host-only adapter used `192.168.244.0/24`, but its DHCP server initially issued addresses from `192.168.56.0/24`. The DHCP configuration was corrected and VirtualBox restarted to clear the stale state.
- A separate Netplan file was created during an attempted static-address configuration but was not included in Netplan's merged output. The attempt was abandoned and the verified snapshot was restored instead of applying uncertain network state.
- Proton VPN allowed no Windows-to-VM host-only communication in the observed configuration. Tests succeeded with Proton disconnected.
- Several command-entry errors produced no system changes and were corrected through output verification.

## Check

| Verification | Temporary legacy condition | Improved result |
|---|---|---|
| Apache runtime state | Active | Inactive |
| Apache startup state | Enabled | Disabled |
| HTTP request | `200 OK` | Connection failed on port 80 |
| Nmap TCP 80 | Open | Closed |
| Nmap TCP 22 | Open | Open |
| PowerShell TCP 22 test | Successful | Successful |
| SSH login | Successful | Successful after reboot |
| Persistence | Not applicable | Port 80 remained closed after reboot |

The expected result was achieved without breaking the required SSH function.

## Act

### Final standard

- SSH on TCP port 22 is the only externally reachable service in the default 1,000-port TCP scan.
- Apache remains installed but must stay stopped and disabled until a documented business requirement justifies enabling it.
- Proton VPN remains disconnected during current host-only lab testing unless its LAN behavior is deliberately evaluated in a future cycle.

### Standard verification

On Ubuntu:

```bash
systemctl is-active apache2
systemctl is-enabled apache2
sudo ss -lntp
```

From Windows:

```powershell
nmap 192.168.244.100
Test-NetConnection 192.168.244.100 -Port 22
ssh leanopsadmin@192.168.244.100
```

These commands record the DHCP address used when Cycle 01 was completed. Cycle 02 replaced it with the current static address `192.168.244.10`.

### Recovery procedure

If HTTP service becomes required and the change is approved:

```bash
sudo systemctl enable --now apache2
```

Then repeat internal socket inspection, HTTP testing, Nmap scanning, and SSH testing. Record the reason and results in the change log.

### Remaining risks

- SSH currently permits password authentication in the isolated lab.
- At the close of Cycle 01, the host-only address was assigned by DHCP. Cycle 02 resolved this risk with a controlled static address.
- NAT remains enabled for updates and should be reviewed before deliberately testing riskier services.
- Raw screenshots still require sanitization before publication.

### Possible next improvement

Cycle 02 selected controlled static addressing from this list and completed it. Remaining candidates include SSH authentication hardening, configuration backup verification, or firewall rule evaluation.
