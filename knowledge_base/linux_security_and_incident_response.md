# Linux Security & Incident Response Lifecycle

## 1. Linux Permissions & Access Control

### File Permission Bits
Linux file permissions are represented by 9 bits divided into three sets: Owner (`u`), Group (`g`), and Others (`o`).

- Read (`r` = 4)
- Write (`w` = 2)
- Execute (`x` = 1)

**Example**: `chmod 755 script.sh`
- Owner: `rwx` (4+2+1 = 7)
- Group: `r-x` (4+0+1 = 5)
- Others: `r-x` (4+0+1 = 5)

### Special Permissions
- **SUID (Set User ID)**: `chmod u+s /path/binary` (Octal 4000). Executable runs with the file owner's privileges (often `root`).
- **SGID (Set Group ID)**: `chmod g+s /path/directory` (Octal 2000). Files created inside inherit group ownership.
- **Sticky Bit**: `chmod +t /tmp` (Octal 1000). Users can only delete or rename their own files within the directory.

---

## 2. Hardening Linux Systems

### SSH Hardening (`/etc/ssh/sshd_config`)
- Disable root login: `PermitRootLogin no`
- Disable password authentication (enforce public key auth): `PasswordAuthentication no`
- Change default SSH port: `Port 2222`
- Limit authentication attempts: `MaxAuthTries 3`
- Use Fail2ban to automatically block IP addresses exhibiting malicious brute-force attempts.

### Log Inspection & Auditing
- System authentication log: `/var/log/auth.log` (Debian/Ubuntu) or `/var/log/secure` (RHEL/CentOS).
- System log daemon: `/var/log/syslog` or `journalctl -u ssh.service`.
- Web server logs: `/var/log/nginx/access.log` and `/var/log/nginx/error.log`.
- Command history inspection: `~/.bash_history` (Check for suspicious `curl`, `wget`, `nc`, or `base64` invocations).

---

## 3. Incident Response Framework (NIST SP 800-61)

### Phase 1: Preparation
- Develop incident response plans, policies, and communication channels.
- Deploy monitoring tools (EDR, SIEM, IDS/IPS).
- Ensure backups are taken regularly and tested for restoration integrity.

### Phase 2: Detection and Analysis
- Identify indicators of compromise (IOCs) such as unexpected network outbound connections, modified file hashes, or unknown listening ports (`netstat -tulpn` or `ss -tulpn`).
- Determine attack vector, scope, and affected systems.

### Phase 3: Containment, Eradication, and Recovery
- **Short-Term Containment**: Isolate affected system from the network (disable network interface or VLAN segment).
- **Long-Term Containment**: Apply temporary patches or security rules.
- **Eradication**: Remove malware components, terminate malicious processes (`kill -9 <PID>`), update credentials.
- **Recovery**: Restore systems from clean known-good backups, monitor for re-infection, bring systems back to production.

### Phase 4: Post-Incident Activity (Lessons Learned)
- Document full timeline of event.
- Hold post-mortem meeting within 2 weeks.
- Update security controls and incident response plan based on findings.
