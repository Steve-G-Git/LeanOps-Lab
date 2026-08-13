# Runbook: Verify Host-Only Connectivity and SSH

## Purpose

Confirm that the Windows host and Ubuntu VM can communicate through the isolated VirtualBox host-only network without relying on the NAT interface.

## Expected standard

- Windows host-only address: `192.168.244.1/24`
- Ubuntu host-only address: within `192.168.244.100-200/24`
- Ubuntu interface: `enp0s8`
- SSH: reachable on TCP port 22
- Proton VPN: disconnected for the current verified configuration

## Procedure

### 1. Confirm Ubuntu interfaces

On Ubuntu:

```bash
ip -br address
```

Expected relevant lines:

```text
enp0s3  UP  10.0.2.15/24
enp0s8  UP  192.168.244.x/24
```

### 2. Confirm Ubuntu routing

```bash
ip route
```

Verify:

- The default route uses `enp0s3` through `10.0.2.2`.
- `192.168.244.0/24` is directly connected through `enp0s8`.
- There is no default route through `enp0s8`.

### 3. Test Ubuntu to Windows

```bash
ping -c 4 192.168.244.1
```

Expected: four replies with zero percent packet loss.

### 4. Test Windows to Ubuntu

In PowerShell, substitute Ubuntu's observed host-only address if it is not `.100`:

```powershell
ping 192.168.244.100
Test-NetConnection 192.168.244.100 -Port 22
```

Expected: ping replies and `TcpTestSucceeded : True`.

### 5. Test SSH login

```powershell
ssh leanopsadmin@192.168.244.100
```

Expected prompt:

```text
leanopsadmin@leanops-server:~$
```

Never record the password or publish the SSH host fingerprint unnecessarily.

## Troubleshooting

### Ubuntu receives a `192.168.56.x` address

1. Power off the VM.
2. In VirtualBox Network Manager, confirm the host-only adapter is `192.168.244.1/24`.
3. Confirm its DHCP server uses:
   - Server: `192.168.244.2`
   - Mask: `255.255.255.0`
   - Pool: `192.168.244.100-200`
4. Close and restart VirtualBox to clear stale DHCP state.
5. Start Ubuntu and repeat `ip -br address`.

### Ubuntu can ping Windows but Windows reports `General failure`

1. Confirm the VirtualBox adapter is up with `Get-NetAdapter -Name "Ethernet 3"`.
2. Disconnect Proton VPN.
3. Repeat ping and `Test-NetConnection`.
4. Do not disable Windows Firewall without evidence that it is the cause.

### SSH service appears inactive

Ubuntu may use socket activation. Check:

```bash
systemctl is-active ssh.socket
sudo ss -lntp
```

An active `ssh.socket` and a listener on TCP 22 indicate SSH is available even when `ssh.service` is temporarily inactive.

## Recovery

If network settings become uncertain, restore VirtualBox snapshot `02-HostOnlyNetworkVerified` or a later verified snapshot and repeat this runbook.
