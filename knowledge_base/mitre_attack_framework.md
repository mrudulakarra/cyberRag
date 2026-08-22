# MITRE ATT&CK Framework - Student Study Guide

## Introduction to MITRE ATT&CK
MITRE ATT&CK® (Adversary Tactics, Techniques, and Knowledge Base) is a globally-accessible knowledge base of adversary tactics and techniques based on real-world observations. The ATT&CK knowledge base is used as a foundation for the development of specific threat models and methodologies in the private sector, in government, and in the cybersecurity product and service community.

---

## Enterprise Tactics Overview
Tactics represent the "why" of an ATT&CK technique or sub-technique. It is the adversary's tactical goal: the reason for performing an action.

1. **Reconnaissance (TA0043)**: Gathering information to plan future adversary operations (e.g., active scanning, gathering victim org information).
2. **Resource Development (TA0042)**: Establishing resources to support operations (e.g., acquiring infrastructure, compromise accounts).
3. **Initial Access (TA0011)**: Techniques adversaries use to gain an initial foothold within a network (e.g., Spearphishing Attachment, Exploit Public-Facing Application, Drive-by Compromise).
4. **Execution (TA0002)**: Running adversary-controlled code on a local or remote system (e.g., Command and Scripting Interpreter like PowerShell, Bash, Python, Scheduled Task).
5. **Persistence (TA0003)**: Maintaining access across restarts, changed credentials, or other interruptions (e.g., Registry Run Keys, Startup Folder, DLL Search Order Hijacking).
6. **Privilege Escalation (TA0004)**: Gaining higher-level permissions on a system or network (e.g., Sudo, Exploitation for Privilege Escalation, Access Token Manipulation).
7. **Defense Evasion (TA0005)**: Avoiding detection by security controls (e.g., Obfuscated Files, Process Injection, Deleting Logs, Disabling Security Tools).
8. **Credential Access (TA0006)**: Stealing credentials such as account names and passwords (e.g., OS Credential Dumping like LSASS memory extraction, Brute Force, Kerberoasting).
9. **Discovery (TA0007)**: Gaining knowledge about the system and internal network (e.g., Account Discovery, Network Service Discovery, System Information Discovery).
10. **Lateral Movement (TA0008)**: Entering and controlling remote systems on a network (e.g., Remote Services, Pass the Hash, SSH Hijacking, RDP compromise).
11. **Collection (TA0009)**: Gathering data of interest to the adversary's goal (e.g., Screen Capture, Audio Capture, Clipboard Data, Email Collection).
12. **Command and Control (TA0011)**: Communicating with compromised systems within a target network (e.g., Encrypted Channel over HTTPS, DNS Tunneling, Web Protocols).
13. **Exfiltration (TA0010)**: Stealing data from your network (e.g., Exfiltration Over C2 Channel, Exfiltration to Cloud Storage).
14. **Impact (TA0040)**: Disrupting availability or compromising integrity of business/operational processes (e.g., Data Encrypted for Impact / Ransomware, Service Stop).

---

## Deep-Dive into Key Techniques & Sub-Techniques

### T1059.001 - Command and Scripting Interpreter: PowerShell
- **Description**: Adversaries may use PowerShell to perform commands and execute scripts. PowerShell is a powerful interactive command-line interface and scripting environment integrated into Windows.
- **Adversary Usage**: Execution of in-memory payloads, downloading secondary malware via `Invoke-WebRequest` or `Net.WebClient`, running administrative commands without dropping binary files onto disk (Living off the Land).
- **Mitigation & Detection**: Enable Script Block Logging (Event ID 4104), PowerShell Module Logging, and constrained language mode. Utilize Antimalware Scan Interface (AMSI).

### T1003.001 - OS Credential Dumping: LSASS Memory
- **Description**: Adversaries may attempt to access credential material stored in the Local Security Authority Subsystem Service (LSASS) process memory.
- **Adversary Usage**: Tools like Mimikatz or `procdump.exe` read LSASS memory to extract plain-text passwords, NTLM hashes, Kerberos tickets, and digest credentials.
- **Mitigation & Detection**: Enable Windows Defender Credential Guard (virtualization-based security), restrict Local Administrator access, monitor process access rights to `lsass.exe` (Event ID 4656 / Sysmon Event ID 10).

### T1566.001 - Phishing: Spearphishing Attachment
- **Description**: Adversaries send targeted emails containing malicious attachments to gain execution on target systems.
- **Adversary Usage**: Email with weaponized Office documents (containing VBA Macros), ISO/VHD files, or executable archives (ZIP/RAR) bypassing email gateway filters.
- **Mitigation**: Email filtering controls, disabling office macros by default, security awareness training for staff.

### T1021.002 - Remote Services: SMB/Windows Admin Shares
- **Description**: Adversaries may use SMB to interact with Windows Admin Shares (`C$`, `ADMIN$`) to execute code remotely.
- **Adversary Usage**: Tools such as PsExec or Impacket's `psexec.py` upload a service executable to `ADMIN$` and start it remotely to gain SYSTEM privileges on another domain host.
- **Mitigation**: Disable SMBv1, enforce SMB signing, restrict local administrator password reuse using LAPS (Local Administrator Password Solution), block inbound port 445 at internal firewalls between workstations.

---

## Cyber Kill Chain vs MITRE ATT&CK
While Lockheed Martin's Cyber Kill Chain describes high-level phases of a cyber attack (Recon -> Weaponization -> Delivery -> Exploitation -> Installation -> C2 -> Actions on Objectives), MITRE ATT&CK provides a granular matrix of specific adversary behaviors, techniques, and practical detection mechanisms mapped to real threat groups (e.g., APT28, APT29, FIN7).
