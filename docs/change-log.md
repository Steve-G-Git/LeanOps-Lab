# Change Log

| Date | Change | Reason | Verification | Rollback |
|---|---|---|---|---|
| 2026-08-12 | Created Ubuntu Server VM with 2 vCPUs, 2048 MB RAM, and a 30 GB dynamic disk | Establish smallest viable server lab | Ubuntu booted; hostname and OS verified | Delete new VM or restore clean-install snapshot |
| 2026-08-12 | Updated Ubuntu packages | Establish patched baseline | Zero immediate updates after reboot; SSH socket available | `00-CleanInstall-PreUpdates` snapshot |
| 2026-08-12 | Added VirtualBox host-only Adapter 2 | Isolate Windows-to-Ubuntu test traffic | Ubuntu and Windows communicated on `192.168.244.0/24`; SSH login succeeded | `01-UpdatedBaseline` snapshot |
| 2026-08-12 | Corrected VirtualBox host-only DHCP subnet from `192.168.56.0/24` to `192.168.244.0/24` | Adapter and DHCP server were configured for different networks | Ubuntu received `192.168.244.100/24` after VirtualBox restart | Restore prior VM snapshot and VirtualBox network values if required |
| 2026-08-12 | Installed Apache HTTP Server | Simulate an undocumented legacy service for PDCA Cycle 01 | HTTP `200 OK`; Nmap reported TCP 80 open | Remove package or restore `02-HostOnlyNetworkVerified` |
| 2026-08-12 | Stopped and disabled Apache | Eliminate unnecessary HTTP exposure while preserving SSH | Apache inactive and disabled; TCP 80 closed; TCP 22 and SSH worked after reboot | `sudo systemctl enable --now apache2` |
| 2026-08-12 | Added persistent `systemd-networkd` configuration for `enp0s8` | Prevent the documented administration address from changing with a DHCP lease | Static `192.168.244.10/24` survived reboot; ping, SSH, NAT, DNS, and routing passed; only TCP 22 remained open | Remove `/etc/systemd/network/20-leanops-enp0s8.network` and reboot, or restore `04-PDCA02-PreStaticAddress` |
| 2026-08-13 | Added a dedicated Ed25519 public key for `leanopsadmin` | Establish a stronger SSH authentication method before changing password access | Key-only login succeeded in two independent sessions and after reboot; permissions verified as `700` and `600` | Clear the added `authorized_keys` entry from the local console, or restore `05-PDCA02-StaticAddressVerified` |
| 2026-08-13 | Added `00-leanops-auth.conf` to disable SSH password and keyboard-interactive authentication | Reduce remote authentication exposure after key access was proven reliable | Effective settings showed key authentication enabled and password authentication disabled; key login survived reboot; password-only login was rejected; only TCP 22 remained open | Remove the drop-in and reload SSH from an existing key session or local console, or restore `06-PDCA03-KeyAuthVerified` |

## Snapshot checkpoints

| Snapshot | Verified condition |
|---|---|
| `00-CleanInstall-PreUpdates` | Fresh Ubuntu installation before package updates |
| `01-UpdatedBaseline` | Updated Ubuntu with verified SSH before host-only network configuration |
| `02-HostOnlyNetworkVerified` | NAT and host-only adapters working; SSH verified from Windows |
| `03-PDCA01-ApacheDisabled` | Apache disabled; SSH retained; post-change and post-reboot tests passed |
| `04-PDCA02-PreStaticAddress` | Pre-change Cycle 02 baseline with `enp0s8` using DHCP address `192.168.244.100/24` |
| `05-PDCA02-StaticAddressVerified` | Static `192.168.244.10/24` persisted after reboot; SSH, NAT, DNS, routing, and service exposure verified |
| `06-PDCA03-KeyAuthVerified` | Dedicated key authentication verified independently and after reboot; SSH password authentication still enabled |
| `07-PDCA03-SSHKeyOnlyVerified` | Key authentication persisted after reboot; password-only SSH rejected; only TCP 22 open |
