# OWASP Top 10 Web Application Security Risks - Comprehensive Guide

## Overview
The Open Web Application Security Project (OWASP) Top 10 is a standard awareness document for developers and web application security experts. It represents a broad consensus on the most critical security risks facing web applications today.

---

## 1. A01:2021 - Broken Access Control
Access control enforces policies such that users cannot act outside of their intended permissions. Failures typically lead to unauthorized information disclosure, modification, or destruction of all data or performing a business function outside the user's limits.

### Common Vulnerabilities
- Bypassing access control checks by modifying the URL (parameter tampering), internal application state, or HTML page.
- Permitting viewing or editing someone else's account by providing its primary key (Insecure Direct Object Reference - IDOR).
- Accessing API endpoints with missing access controls for POST, PUT, and DELETE methods.
- Elevation of privilege (acting as admin without logging in).

### Mitigation Strategies
- Enforce access control in trusted server-side code or serverless API where the attacker cannot modify the check.
- Implement access control mechanisms once and re-use them throughout the application (RBAC - Role-Based Access Control).
- Disable web server directory listing and ensure file metadata (e.g., .git) is not present within web roots.
- Log access control failures and alert admins when appropriate.

---

## 2. A02:2021 - Cryptographic Failures
Formerly known as Sensitive Data Exposure, Cryptographic Failures refer to issues related to cryptography (or lack thereof) which often lead to sensitive data exposure or compromise of system credentials.

### Key Threats & Weaknesses
- Transmission of data in clear text (HTTP, FTP, SMTP without TLS).
- Use of old or weak cryptographic algorithms (MD5, SHA1, RC4, DES).
- Hardcoded encryption keys or passwords within source code repositories.
- Improper certificate validation or accepting self-signed untrusted TLS certificates.

### Prevention
- Classify data processed, stored, or transmitted by an application. Identify which data is sensitive according to privacy laws.
- Don't store sensitive data unnecessarily. Discard it as soon as possible.
- Ensure encryption at rest using strong algorithms such as AES-256 or ChaCha20.
- Use strong password hashing functions with salt, such as Argon2id, bcrypt, or PBKDF2.

---

## 3. A03:2021 - Injection (Including SQL Injection & XSS)
Injection occurs when untrusted user input is passed to an interpreter as part of a command or query. The attacker's hostile data tricks the interpreter into executing unintended commands or accessing unauthorized data.

### SQL Injection (SQLi)
- **Mechanics**: An attacker inserts SQL syntax into input fields (e.g., `' OR '1'='1`). If concatenation is used to construct queries, the database executes the malicious query structure.
- **Impact**: Bypassing authentication, dumping entire database tables (data exfiltration), altering data, or executing administrative commands.
- **Prevention**: Use Parameterized Queries (Prepared Statements) or Object-Relational Mapping (ORM) frameworks. Never concatenate user input into raw SQL strings.

### Cross-Site Scripting (XSS)
- **Types**:
  1. *Stored XSS*: Malicious script is permanently stored on the target server (e.g., in a comment field) and served to other users.
  2. *Reflected XSS*: Malicious script is reflected off a web server in an error message or search result.
  3. *DOM-based XSS*: Vulnerability exists in client-side JavaScript processing user data.
- **Impact**: Session hijacking via cookie theft, defacement, redirecting users to phishing sites.
- **Prevention**: Context-aware output encoding, Content Security Policy (CSP), setting `HttpOnly` flags on session cookies.

---

## 4. A04:2021 - Insecure Design
Insecure design focuses on risks related to design and architectural flaws. It calls for more use of threat modeling, secure design patterns, and reference architectures.

### Security Principles
- **Least Privilege**: Users should operate with the minimum level of access necessary.
- **Defense in Depth**: Multiple layers of security controls throughout an IT system.
- **Fail-Safe Defaults**: Access decisions should be based on permission rather than exclusion (deny by default).

---

## 5. A05:2021 - Security Misconfiguration
Security misconfigurations occur when security controls are inaccurately defined or left default.

### Examples
- Default credentials left enabled (e.g., `admin:admin` or `root:root`).
- Debugging features turned on in production environments.
- Unnecessary ports, services, pages, or accounts enabled.
- Missing security headers (e.g., `X-Content-Type-Options`, `Strict-Transport-Security`).

---

## 6. A06:2021 - Vulnerable and Outdated Components
Applications using components (libraries, frameworks, software modules) with known vulnerabilities can undermine application defenses and enable diverse attacks.

### Prevention
- Remove unused dependencies, unnecessary features, components, and files.
- Continuously inventory client-side and server-side components (Software Bill of Materials - SBOM).
- Monitor sources like CVE, NVD, and OWASP Dependency-Check for updates and security patches.

---

## 7. A07:2021 - Identification and Authentication Failures
Confirmation of the user's identity, authentication, and session management are critical to protect against authentication-related attacks.

### Attack Vector Examples
- Credential stuffing (using lists of compromised username/password pairs).
- Brute-force attacks against login panels.
- Session fixation and exposed session tokens in URLs.

### Defenses
- Implement Multi-Factor Authentication (MFA).
- Enforce strong password complexity rules and check against known breached password lists (HaveIBeenPwned).
- Implement rate limiting and IP throttling on login endpoints.

---

## 8. A08:2021 - Software and Data Integrity Failures
Relates to code and infrastructure that does not protect against integrity violations, such as untrusted CI/CD pipelines or auto-update mechanisms without verification.

---

## 9. A09:2021 - Security Logging and Monitoring Failures
Insufficient logging and monitoring prevent organizations from detecting, reacting to, and containing active security breaches in a timely manner.

### Best Practices
- Ensure all login, access control, and server-side validation failures can be logged with sufficient context.
- Centralize log management (SIEM) and implement automated alerting for anomalous activities.

---

## 10. A10:2021 - Server-Side Request Forgery (SSRF)
SSRF vulnerabilities occur when a web application fetches a remote resource without validating the user-supplied URL.

### Impact
An attacker can force the application to send crafted requests to unexpected destinations, such as internal cloud metadata services (`http://169.254.169.254`), internal databases, or local loopback services (`http://127.0.0.1:8080`).

### Mitigation
- Segment remote resource fetching in separate networks.
- Enforce strict URL allowlists and sanitize incoming destination addresses.
