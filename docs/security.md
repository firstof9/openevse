# Security Policy

Information regarding security, supported versions, and responsibly disclosing vulnerabilities in the OpenEVSE Home Assistant integration.

---

## Supported Versions

Security patches and updates are actively maintained for the latest release:

| Release Branch / Version | Supported          |
| :----------------------- | :----------------- |
| Latest Release           | :white_check_mark: |
| Older Versions           | :x:                |

We strongly advise keeping both your Home Assistant instance and the OpenEVSE integration up-to-date via [HACS](https://hacs.xyz/) or [GitHub Releases](https://github.com/firstof9/openevse/releases).

---

## Reporting a Security Vulnerability

If you discover or suspect a security vulnerability in this integration, please report it responsibly:

### Private Vulnerability Disclosure
Please report security advisories privately using GitHub's **Private Vulnerability Reporting**:

1. Navigate to the repository's [Security Advisories](https://github.com/firstof9/openevse/security/advisories) tab.
2. Click **[Report a vulnerability](https://github.com/firstof9/openevse/security/advisories/new)**.
3. Fill in the details of the advisory.

::: warning Do Not Open Public Issues
Please **do not** report suspected security vulnerabilities via public GitHub issues, forum discussions, or pull requests.
:::

---

## Information to Include

To help us investigate and resolve the issue quickly:
- Detailed explanation of the vulnerability and attack surface.
- Step-by-step reproduction instructions or Proof of Concept (PoC).
- Versions of OpenEVSE integration, Home Assistant core, and charger firmware used.
- Any suggested fix or remediation if known.

---

## Vulnerability Handling Timeline

- **Initial Response**: We strive to review and acknowledge all security disclosures within 48 to 72 hours.
- **Triage & Patching**: Confirmed vulnerabilities are investigated and patched in a dedicated release branch.
- **Coordinated Disclosure**: Once a patched release is published, a security advisory will be issued crediting the reporter (unless anonymity is requested).
