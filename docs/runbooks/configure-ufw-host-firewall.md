# Runbook: Configure and Verify the UFW Host Firewall

## Purpose

Enable a default-deny host firewall on the Ubuntu lab server while preserving key-authenticated SSH from the approved Windows host-only endpoint.

## Preconditions

- Ubuntu address: `192.168.244.10`
- Approved Windows source: `192.168.244.1`
- Key-authenticated SSH verified
- Proton VPN fully exited for the current host-only configuration
- Local VirtualBox console available
- Current-state snapshot created
- Existing SSH session kept open throughout activation

## 1. Record the baseline

On Ubuntu:

```bash
sudo ufw status verbose
systemctl is-enabled ufw
sudo ufw show added
sudo ss -lntp
```

From Windows PowerShell:

```powershell
Test-NetConnection 192.168.244.10 -Port 22
nmap 192.168.244.10
```

Stop if UFW is already active or saved rules exist unexpectedly. Review them before continuing.

## 2. Prepare the policy while UFW is inactive

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow from 192.168.244.1 to any port 22 proto tcp comment 'LeanOps SSH admin'
```

Verify the stored rule:

```bash
sudo ufw show added
```

Required rule:

```text
ufw allow from 192.168.244.1 to any port 22 proto tcp comment 'LeanOps SSH admin'
```

Do not add a general `OpenSSH` or unrestricted `22/tcp` rule.

## 3. Enable UFW safely

Keep the current SSH session open and the VirtualBox console available:

```bash
sudo ufw enable
sudo ufw status verbose
```

Required policy:

- Status active
- Default incoming deny
- Default outgoing allow
- Routed traffic disabled
- TCP 22 allowed from `192.168.244.1`

## 4. Verify a fresh approved connection

From a separate Windows PowerShell tab:

```powershell
ssh -i "$env:USERPROFILE\.ssh\leanops_lab_ed25519" -o IdentitiesOnly=yes -o PasswordAuthentication=no leanopsadmin@192.168.244.10
```

Run `whoami`. Do not close the original session until this test succeeds.

## 5. Verify required outbound functions

On Ubuntu:

```bash
ping -c 4 1.1.1.1
getent hosts archive.ubuntu.com
```

Required results:

- Four ping replies with zero packet loss
- One or more resolved addresses for `archive.ubuntu.com`

## 6. Verify external filtering

From Windows PowerShell:

```powershell
nmap 192.168.244.10
```

Required result from the approved endpoint:

- TCP 22 open
- Other commonly scanned TCP ports filtered

## 7. Verify persistence

Reboot Ubuntu. Repeat:

- Key-authenticated SSH login
- `sudo ufw status verbose`
- Nmap scan from Windows
- DNS resolution with `getent hosts archive.ubuntu.com`

Do not declare the change complete until the policy and required functions survive reboot.

## Recovery

If SSH access fails after enabling UFW, use the existing SSH session or VirtualBox console:

```bash
sudo ufw disable
```

Inspect saved rules:

```bash
sudo ufw show added
```

To remove the restricted rule while UFW is inactive:

```bash
sudo ufw delete allow from 192.168.244.1 to any port 22 proto tcp
```

Establish and verify an approved replacement rule before enabling UFW again. If recovery is unsuccessful, restore snapshot `08-PDCA04-PreUFW`.
