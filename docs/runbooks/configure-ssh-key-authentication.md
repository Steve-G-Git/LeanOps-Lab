# Runbook: Configure and Verify SSH Key Authentication

## Purpose

Establish dedicated key-based SSH access from Windows to the Ubuntu lab server, verify it without password fallback, then disable SSH password authentication without causing an administrative lockout.

## Preconditions

- Ubuntu address: `192.168.244.10`
- Ubuntu account: `leanopsadmin`
- Local VirtualBox console access available
- Current-state snapshot created
- Proton VPN disconnected for the current verified host-only configuration
- Password login still available until key authentication passes all pre-hardening tests

Never publish or paste the private key, key passphrase, public-key content, or fingerprint.

## 1. Inspect the baseline

From an existing SSH session:

```bash
sudo sshd -T | grep -E '^(pubkeyauthentication|passwordauthentication|kbdinteractiveauthentication|usepam) '
if [ -f ~/.ssh/authorized_keys ]; then wc -l ~/.ssh/authorized_keys; else echo "No authorized_keys file"; fi
```

Do not display the contents of `authorized_keys` as public evidence.

## 2. Check for an existing default key

Exit to Windows PowerShell and run:

```powershell
Test-Path "$env:USERPROFILE\.ssh\id_ed25519"
Test-Path "$env:USERPROFILE\.ssh\id_ed25519.pub"
```

If either file exists, stop and decide whether to use it or create a dedicated lab key. Do not overwrite an existing key.

## 3. Create the dedicated key

If the dedicated lab key does not already exist:

```powershell
ssh-keygen -t ed25519 -f "$env:USERPROFILE\.ssh\leanops_lab_ed25519" -C "leanops-lab"
```

Use a private passphrase. Do not record it in project documentation.

## 4. Install only the public key

From Windows PowerShell:

```powershell
Get-Content "$env:USERPROFILE\.ssh\leanops_lab_ed25519.pub" | ssh leanopsadmin@192.168.244.10 "umask 077; mkdir -p ~/.ssh; cat >> ~/.ssh/authorized_keys; chmod 600 ~/.ssh/authorized_keys; wc -l ~/.ssh/authorized_keys"
```

Before repeating this command, inspect the line count so the same public key is not appended twice.

## 5. Verify permissions

On Ubuntu:

```bash
stat -c '%a %n' ~/.ssh ~/.ssh/authorized_keys
```

Required permissions:

```text
700 /home/leanopsadmin/.ssh
600 /home/leanopsadmin/.ssh/authorized_keys
```

## 6. Prove key authentication

From Windows PowerShell:

```powershell
ssh -i "$env:USERPROFILE\.ssh\leanops_lab_ed25519" -o IdentitiesOnly=yes -o PasswordAuthentication=no leanopsadmin@192.168.244.10
```

Run `whoami`, then repeat the connection from a second independent PowerShell session. Reboot and test again before changing password authentication.

## 7. Identify active SSH configuration sources

On Ubuntu:

```bash
sudo sshd -T | grep -E '^(pubkeyauthentication|passwordauthentication|kbdinteractiveauthentication|usepam) '
sudo grep -RniE '^[[:space:]]*(Include|PasswordAuthentication|PubkeyAuthentication|KbdInteractiveAuthentication|UsePAM)[[:space:]]' /etc/ssh/sshd_config /etc/ssh/sshd_config.d 2>/dev/null
```

## 8. Create the hardening drop-in

Create `/etc/ssh/sshd_config.d/00-leanops-auth.conf` with:

```text
# LeanOps Lab PDCA Cycle 03
PubkeyAuthentication yes
PasswordAuthentication no
KbdInteractiveAuthentication no
```

Verify the saved file, validate syntax, and inspect effective settings:

```bash
sudo cat -n /etc/ssh/sshd_config.d/00-leanops-auth.conf
sudo sshd -t && echo "SSH configuration syntax valid"
sudo sshd -T | grep -E '^(pubkeyauthentication|passwordauthentication|kbdinteractiveauthentication|usepam) '
```

Do not reload SSH unless syntax is valid and the effective settings match the intended state.

## 9. Reload and test without closing the working session

Keep the current SSH session open:

```bash
sudo systemctl reload ssh.service
systemctl is-active ssh.service
```

From a new Windows PowerShell tab, repeat the key-only connection. After it succeeds, test password-only access:

```powershell
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no -o KbdInteractiveAuthentication=no leanopsadmin@192.168.244.10
```

Required result:

```text
Permission denied (publickey).
```

The command must not prompt for the Ubuntu password.

## 10. Verify persistence

Reboot Ubuntu. Repeat the key-only login, password-only rejection test, and Nmap scan:

```powershell
nmap 192.168.244.10
```

Required results:

- Key-only login succeeds.
- Password-only login is rejected.
- TCP port 22 remains open.
- No additional commonly scanned TCP ports open.

## Recovery

If key authentication fails after the drop-in is applied, use the still-open SSH session or VirtualBox console:

```bash
sudo rm /etc/ssh/sshd_config.d/00-leanops-auth.conf
sudo sshd -t
sudo systemctl reload ssh.service
```

The cloud-init setting should restore password authentication. Confirm the effective settings before closing the recovery session. If recovery is unsuccessful, restore snapshot `06-PDCA03-KeyAuthVerified`.

If recovery must return to the state before any key installation, restore snapshot `05-PDCA02-StaticAddressVerified`.
