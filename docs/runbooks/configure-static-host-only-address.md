# Runbook: Configure the Static Host-Only Address

## Purpose

Configure the Ubuntu server's `enp0s8` interface with the persistent host-only address `192.168.244.10/24` while preserving NAT as the only default route.

## Preconditions

- VirtualBox host-only network: `192.168.244.0/24`
- Windows host-only adapter: `192.168.244.1/24`
- VirtualBox DHCP server: `192.168.244.2/24`
- DHCP pool: `192.168.244.100` through `192.168.244.200`
- Local VirtualBox console access available
- Current-state snapshot created

The selected `.10` address is outside the DHCP pool.

## Configuration

Create `/etc/systemd/network/20-leanops-enp0s8.network` with:

```ini
[Match]
Name=enp0s8

[Network]
Address=192.168.244.10/24
DHCP=no
LinkLocalAddressing=ipv6
```

Verify the exact saved contents before activation:

```bash
sudo cat -n /etc/systemd/network/20-leanops-enp0s8.network
```

Apply the configuration from the local console:

```bash
sudo networkctl reload
sudo networkctl reconfigure enp0s8
```

## Verification

Confirm that networkd selected the intended file:

```bash
networkctl status enp0s8 --no-pager
```

Expected network file:

```text
/etc/systemd/network/20-leanops-enp0s8.network
```

Confirm addresses and routing:

```bash
ip -br address
ip route
```

Required results:

- `enp0s8` has `192.168.244.10/24`.
- `192.168.244.100/24` is absent.
- The default route remains through `10.0.2.2` on `enp0s3`.
- `enp0s8` has no default gateway.

Run the full [`verify-host-only-connectivity.md`](verify-host-only-connectivity.md) procedure. Also verify outbound routing and DNS:

```bash
ping -c 4 1.1.1.1
getent hosts archive.ubuntu.com
```

Reboot and repeat the address, route, Nmap, and SSH checks before declaring the change persistent.

## Troubleshooting

If `.100` remains active, inspect:

```bash
networkctl status enp0s8 --no-pager
```

If `Network File` still points to the generated dracut fallback, check the persistent file's `[Match]` section and confirm that it contains the exact key `Name=enp0s8`.

Do not add a gateway to the host-only interface.

## Recovery

From the local console, remove the persistent configuration file and reboot:

```bash
sudo rm /etc/systemd/network/20-leanops-enp0s8.network
sudo reboot
```

After reboot, the generated fallback configuration should return `enp0s8` to VirtualBox DHCP. If recovery is unsuccessful, restore snapshot `04-PDCA02-PreStaticAddress`.
