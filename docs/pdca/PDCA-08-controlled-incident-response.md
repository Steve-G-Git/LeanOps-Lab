# PDCA 08: Controlled Default-Route Incident Response

## Summary

Cycle 08 tested the completed LeanOps controls as one end-to-end incident-response process. A healthy baseline and pre-incident evidence package were preserved before the VirtualBox NAT default route was deliberately removed from the isolated Ubuntu server.

The standardized health check detected the missing route and loss of internet reachability while SSH administration over the separate host-only network remained available. An incident package preserved the failure before recovery. The first recovery attempt, a DHCP lease renewal, did not restore the route. Reconfiguring the NAT interface did. Health, new SSH access, evidence integrity, and reboot persistence were then verified.

Raw evidence archives and screenshots are not published because they contain protected operational details or personal Windows paths. The evidence below is a sanitized record using only fictional lab addresses.

## Plan

### Current condition and problem

Cycles 06 and 07 created repeatable detection and evidence-collection tools, but they had not yet been exercised through a network failure that required diagnosis, staged recovery, and post-reboot verification.

### Expected result

- Establish and preserve a healthy pre-incident baseline.
- Create one controlled network failure without losing administrative access.
- Detect the failure through the standard health check.
- Preserve incident evidence before correction.
- Distinguish a routing failure from an interface, firewall, or SSH failure.
- Attempt recovery in the documented order and record unsuccessful steps.
- Restore service without unrelated changes.
- Verify health, fresh SSH access, reboot persistence, and off-VM evidence integrity.
- Convert the tested response into standardized work.

### Test method

1. Verify the normal health state and NAT route.
2. Collect a pre-incident evidence package.
3. Create snapshot `16-PDCA08-PreIncidentDrill`.
4. Remove only the NAT default route on `enp0s3`.
5. Confirm the host-only address and existing SSH session remain available.
6. Run the health check and preserve the failure package.
7. Inspect health and network evidence to identify the failed layer.
8. Attempt DHCP renewal, then interface reconfiguration if necessary.
9. Rerun the health check and collect recovered-state evidence.
10. Establish a new key-only SSH session.
11. Reboot and verify the route, health state, and SSH access.
12. Collect post-reboot evidence and verify all four archives on Windows.

### Risks and rollback

- Removing the wrong route or changing the wrong interface could interrupt administration.
- Multiple simultaneous changes could obscure the cause or invalidate the evidence.
- Evidence could be lost if recovery began before collection.
- The host-only interface `enp0s8` provided an independent administrative path.
- The recovery order was DHCP renewal, interface reconfiguration, reboot, then snapshot restoration.
- Snapshot `16-PDCA08-PreIncidentDrill` preserved the verified pre-incident state.

## Do

### Established the baseline

The normal health check returned 12 PASS, 1 WARN, 0 FAIL with exit code `1`. The warning represented two package updates in the current APT cache. The NAT interface had `10.0.2.15/24`, and the default route used `10.0.2.2` through `enp0s3`.

A pre-incident evidence package was collected and verified before the fault was introduced.

### Introduced one controlled failure

Only the NAT default route was removed:

```bash
sudo ip -4 route del default via 10.0.2.2 dev enp0s3
```

The host-only interface remained up at `192.168.244.10/24`, and the SSH session from `192.168.244.1` remained available.

### Detected and preserved the incident

The health check reported:

- NAT default route missing
- Internet target unreachable
- DNS still resolving
- 10 PASS, 1 WARN, 2 FAIL
- exit code `2`

The evidence collector preserved the failure before any recovery action. Network evidence showed both interfaces and their connected routes still present, but no default route. This isolated the problem to routing rather than link state, addressing, SSH, or UFW.

### Recovered in stages

The first planned action did not fix the condition:

```bash
sudo networkctl renew enp0s3
```

The default route remained absent. The second action restored the DHCP route:

```bash
sudo networkctl reconfigure enp0s3
```

The recovered route was:

```text
default via 10.0.2.2 dev enp0s3 proto dhcp src 10.0.2.15 metric 100
```

No snapshot restoration, manual route addition, firewall change, or SSH change was required.

## Check

### Sanitized evidence summary

```text
PRE-INCIDENT
health: 12 PASS, 1 WARN, 0 FAIL
health exit code: 1
default route: present
archive checksum: OK

ROUTE-MISSING INCIDENT
health: 10 PASS, 1 WARN, 2 FAIL
health exit code: 2
NAT interface address: present
host-only administration: available
default route: missing
internet target: unreachable
archive checksum: OK

RECOVERED
health: 12 PASS, 1 WARN, 0 FAIL
health exit code: 1
default route: restored by interface reconfiguration
fresh key-only SSH session: passed
archive checksum: OK

POST-REBOOT
health: 12 PASS, 1 WARN, 0 FAIL
health exit code: 1
default route: persisted
archive checksum: OK
Windows verification: four archives passed SHA-256
```

| Verification | Result |
|---|---|
| Controlled fault affected only the intended route | Passed |
| Health check detected operational impact | Passed |
| Failure evidence captured before recovery | Passed |
| SSH administration remained available | Passed |
| Evidence supported route-level diagnosis | Passed |
| DHCP renewal recovery attempt | Did not restore the route |
| Interface reconfiguration | Restored the DHCP default route |
| Fresh key-only SSH after recovery | Passed |
| Post-reboot route and health | Passed |
| Four off-VM checksum checks | Passed |

The expected result was achieved. The drill demonstrated a complete detect, preserve, investigate, contain, recover, verify, and standardize sequence.

## Act

### Final standard

- Establish a healthy baseline before a controlled drill.
- Preserve evidence before corrective action whenever access and safety permit.
- Confirm the administrative path is independent before changing a route.
- Use health and network evidence to identify the smallest failed component.
- Apply recovery actions one at a time and verify after each attempt.
- Record unsuccessful recovery steps instead of hiding them.
- After recovery, rerun health checks, establish a fresh SSH session, reboot, and verify again.
- Transfer required evidence off the VM and verify SHA-256 at the destination.
- Do not publish raw archives or screenshots containing personal paths or operational identifiers.
- The completed state is preserved in snapshot `17-PDCA08-IncidentResponseVerified`.

### Standard work and recovery

The tested procedure is documented in [`../runbooks/respond-to-missing-default-route.md`](../runbooks/respond-to-missing-default-route.md).

### Remaining risks

- The exercise used a controlled VirtualBox NAT failure, not a production outage.
- DNS continued to resolve during the short incident and was not treated as proof of internet reachability.
- `networkctl reconfigure` may briefly disrupt the affected interface.
- The health check depends on one ICMP target and cached APT metadata.
- Evidence remains locally generated and is not tamper-resistant remote logging.
