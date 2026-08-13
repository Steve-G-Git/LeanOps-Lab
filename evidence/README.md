# Evidence Handling

Only reviewed and sanitized evidence belongs in this directory.

## Suggested structure

- `sanitized/`: screenshots or text output approved for public use
- `raw/`: local working evidence excluded by `.gitignore`

## Review checklist

Before adding evidence, remove or crop:

- Personal usernames and local profile paths
- Real home-network details
- Passwords, keys, tokens, and authentication material
- Machine IDs, boot IDs, and unnecessary MAC addresses
- SSH fingerprints unless they are essential to the documented test
- Unrelated browser tabs, notifications, and personal content

Give sanitized files descriptive names such as:

```text
pdca-01-before-nmap-ssh-only.png
pdca-01-temporary-apache-http-open.png
pdca-01-after-nmap-http-closed.png
```
