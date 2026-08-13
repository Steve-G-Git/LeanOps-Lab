# PDCA 03: Establish SSH Key Authentication

## Summary

The Ubuntu server allowed SSH password authentication on the isolated host-only network. A dedicated Ed25519 key pair was created on the Windows administrative workstation, and only its public key was installed for `leanopsadmin`. Key access was verified repeatedly before a separate SSH drop-in disabled password and keyboard-interactive authentication. Key access and the hardened settings persisted after reboot, while password-only access was rejected.

No private key, passphrase, public-key content, fingerprint, personal Windows username, or MAC address is included in this record.

## Plan

### Current condition and problem

- Effective SSH settings showed public-key and password authentication enabled.
- Keyboard-interactive authentication was already disabled.
- PAM remained enabled for account and session handling.
- `~/.ssh/authorized_keys` existed but contained zero entries.
- The Windows workstation did not have a default Ed25519 key pair.

Password authentication created an avoidable remote authentication method. Disabling it before key access was independently proven could have caused an administrative lockout.

### Expected result

- A dedicated passphrase-protected key remains on the Windows workstation.
- Only the public key is added to the Ubuntu account.
- Key-only SSH login works in separate sessions and after reboot.
- SSH password and keyboard-interactive authentication are disabled.
- Password-only login is rejected without prompting for a password.
- TCP port 22 remains reachable, and no additional common TCP ports open.

### Test method

1. Inspect effective SSH authentication settings and the authorized-key line count.
2. Check for an existing default Ed25519 key without displaying key content.
3. Create a dedicated key pair and install only the public key.
4. Verify the SSH directory and file permissions.
5. Test key-only authentication twice with password fallback disabled.
6. Reboot and repeat the key-only test.
7. Inspect the active SSH configuration sources.
8. Validate the new drop-in before reloading SSH.
9. Keep a working session open while testing a fresh key-only session.
10. Force a password-only attempt and confirm rejection.
11. Reboot and repeat the positive and negative authentication tests.
12. Run Nmap and confirm that the established port baseline remains unchanged.

### Risks and rollback

- Disabling passwords before proving key access could cause remote lockout.
- Incorrect permissions could cause OpenSSH to reject the authorized-key file.
- A malformed SSH drop-in could prevent a safe service reload.
- Snapshot `05-PDCA02-StaticAddressVerified` preserved the pre-key baseline.
- Snapshot `06-PDCA03-KeyAuthVerified` preserved working key access while passwords were still enabled.
- Existing SSH sessions and the VirtualBox console provided recovery access during hardening.

## Do

### Establish key authentication

A dedicated Ed25519 key pair named `leanops_lab_ed25519` was created on Windows with comment `leanops-lab` and a private passphrase. The private key remained on Windows. The public key was appended to:

```text
/home/leanopsadmin/.ssh/authorized_keys
```

The authorized-key count changed from zero to one. Permissions were verified as:

```text
700 /home/leanopsadmin/.ssh
600 /home/leanopsadmin/.ssh/authorized_keys
```

Key-only authentication was tested using the dedicated identity with unrelated identities and password fallback disabled. Two independent sessions succeeded, and another key-only login succeeded after reboot.

### Trace the active configuration

The effective pre-hardening settings were:

```text
usepam yes
pubkeyauthentication yes
passwordauthentication yes
kbdinteractiveauthentication no
```

Inspection traced `PasswordAuthentication yes` to the cloud-init drop-in:

```text
/etc/ssh/sshd_config.d/50-cloud-init.conf
```

### Apply the controlled hardening change

Rather than modify the cloud-init-managed file, the following persistent drop-in was created:

```text
/etc/ssh/sshd_config.d/00-leanops-auth.conf
```

Its contents were:

```text
# LeanOps Lab PDCA Cycle 03
PubkeyAuthentication yes
PasswordAuthentication no
KbdInteractiveAuthentication no
```

`sshd -t` confirmed valid syntax. `sshd -T` confirmed the intended effective values before SSH was reloaded. The current working session remained open during the reload and fresh-session test.

### Unexpected command-path result

The password-rejection command was briefly run from inside an Ubuntu SSH session instead of Windows PowerShell. That tested the server connecting to itself and produced a first-use host-authenticity prompt. The correct Windows-to-Ubuntu test was then repeated from a fresh PowerShell session. No SSH server setting changed as a result of the mistaken test location.

## Check

### Sanitized evidence summary

This compact summary is derived from the observed results. Key material, fingerprints, personal paths, usernames, MAC addresses, and unrelated output are omitted.

```text
BEFORE
public-key authentication: enabled
password authentication: enabled
keyboard-interactive authentication: disabled
authorized key entries: 0

AFTER REBOOT
public-key authentication: enabled
password authentication: disabled
keyboard-interactive authentication: disabled
key-only login: successful
password-only login: Permission denied (publickey)
22/tcp open  ssh
999 commonly scanned TCP ports closed
```

| Verification | Result |
|---|---|
| Dedicated public key installed | One authorized-key entry |
| SSH directory permissions | `700` |
| Authorized-key file permissions | `600` |
| Independent key-only sessions | Two successful |
| Key login after initial reboot | Successful |
| SSH configuration syntax | Valid |
| Effective password authentication | Disabled |
| Fresh key login after reload | Successful |
| Password-only login after reload | Rejected |
| Key login after final reboot | Successful |
| Password-only login after final reboot | Rejected |
| Nmap after final reboot | TCP 22 open; 999 commonly scanned TCP ports closed |

The expected result was achieved without losing remote administration or changing the established service-exposure baseline.

## Act

### Final standard

- Remote SSH access uses the dedicated Ed25519 key for `leanopsadmin`.
- SSH password and keyboard-interactive authentication remain disabled.
- The private key stays on the Windows administrative workstation and must never be copied into the repository.
- SSH configuration changes must pass `sshd -t` before reload.
- A working session remains open until a second independent session verifies any authentication change.
- The final verified state is preserved in snapshot `07-PDCA03-SSHKeyOnlyVerified`.

### Standard work and recovery

Repeatable setup, verification, and recovery steps are documented in [`../runbooks/configure-ssh-key-authentication.md`](../runbooks/configure-ssh-key-authentication.md).

If the client key becomes unavailable, use the VirtualBox console or restore snapshot `06-PDCA03-KeyAuthVerified`. Do not weaken authentication remotely without first establishing a controlled recovery path.

### Remaining risk

The dedicated private key currently depends on the Windows workstation. A separate, secure key-backup and recovery process has not yet been established or tested.
