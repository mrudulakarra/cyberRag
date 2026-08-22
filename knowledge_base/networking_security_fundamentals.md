# Networking & Security Fundamentals - Student Guide

## 1. OSI Model vs TCP/IP Protocol Suite

### OSI 7-Layer Reference Model
1. **Application (Layer 7)**: HTTP, HTTPS, FTP, SSH, DNS, SMTP. Interfaces directly with user applications.
2. **Presentation (Layer 6)**: Data encryption, compression, formatting (SSL/TLS, ASCII, JPEG, JSON).
3. **Session (Layer 5)**: Manages sessions between applications (NetBIOS, RPC).
4. **Transport (Layer 4)**: End-to-end communication, segmentation, flow control, error checking (TCP, UDP).
5. **Network (Layer 3)**: Logical addressing, routing across subnets (IP, ICMP, IPsec, ARP).
6. **Data Link (Layer 2)**: Physical addressing (MAC address), frame switching (Ethernet, Wi-Fi 802.11, Switches).
7. **Physical (Layer 1)**: Transmission of raw bits over physical medium (Cables, Fiber optics, RF signals).

### TCP/IP 4-Layer Model
- **Application Layer**: Combines OSI Layers 5, 6, and 7.
- **Transport Layer**: OSI Layer 4.
- **Internet Layer**: OSI Layer 3.
- **Network Access / Link Layer**: Combines OSI Layers 1 and 2.

---

## 2. TCP vs UDP Protocols

### TCP (Transmission Control Protocol)
- **Characteristics**: Connection-oriented, reliable, ordered delivery, flow control, error checking.
- **Three-Way Handshake**:
  1. `SYN`: Client sends a Synchronize packet with Initial Sequence Number (ISN) to Server.
  2. `SYN-ACK`: Server responds with Synchronize-Acknowledge.
  3. `ACK`: Client responds with Acknowledge. Connection established (`ESTABLISHED` state).
- **Four-Way Teardown**: `FIN` -> `ACK` -> `FIN` -> `ACK`.
- **Use Cases**: Web browsing (HTTP/HTTPS), file transfer (FTP), email (SMTP/IMAP), remote administration (SSH).

### UDP (User Datagram Protocol)
- **Characteristics**: Connectionless, lightweight, unreliable (no guarantee of delivery or order), no handshake, lower overhead.
- **Use Cases**: Real-time streaming, online gaming, VoIP, DNS queries, DHCP, SNMP.

---

## 3. Core Network Infrastructure & Attacks

### DNS (Domain Name System)
- **Function**: Translates human-readable domain names (e.g., `example.com`) into numerical IP addresses (e.g., `93.184.216.34`).
- **DNS Security Threats**:
  - *DNS Cache Poisoning / Spoofing*: Injecting false IP mappings into a DNS resolver cache to redirect users to malicious servers.
  - *DNS Tunneling*: Encoding data inside DNS queries/responses to bypass firewalls for C2 exfiltration.
  - *DNS Amplification DDoS*: Exploiting open DNS resolvers to flood a target with inflated UDP responses.

### ARP (Address Resolution Protocol) & ARP Spoofing
- **Function**: Resolves Layer 3 IP addresses to Layer 2 MAC addresses on local Ethernet networks.
- **ARP Spoofing / Poisoning Attack**:
  - An attacker sends forged ARP responses onto a local area network (LAN).
  - Associates the attacker's MAC address with the IP address of an authorized gateway or target server.
  - Enables Man-in-the-Middle (MITM) traffic interception, eavesdropping, and packet manipulation.
- **Defense**: Static ARP entries, Dynamic ARP Inspection (DAI) on managed switches, 802.1X network access control.

---

## 4. Firewalls, IDS, and IPS

### Firewalls
- **Packet Filtering Firewall**: Examines headers (source/dest IP, port, protocol) against access control lists (ACLs). Stateless.
- **Stateful Inspection Firewall**: Tracks state of active connections. Remembers SYN-ACK handshake states and allows return traffic automatically.
- **Next-Generation Firewall (NGFW)**: Deep Packet Inspection (DPI), application-level awareness, integrated intrusion prevention, and TLS decryption.

### IDS vs IPS
- **IDS (Intrusion Detection System)**: Passive monitor. Analyzes copy of network traffic (via TAP or SPAN port) and generates alerts upon detecting suspicious signatures or anomalies.
- **IPS (Intrusion Prevention System)**: Inline placement. Actively inspects live traffic flow and can block, drop, or reset connections in real time when threats are detected.

---

## 5. Packet Analysis & Wireshark Basics
- **Wireshark Display Filters**:
  - `ip.addr == 192.168.1.100`: Show traffic to/from IP.
  - `tcp.port == 443`: Show HTTPS traffic.
  - `http.request.method == "POST"`: Show HTTP POST submissions.
  - `dns.flags.response == 0`: Show DNS query requests.
  - `arp.duplicate-address-detected`: Identify potential ARP conflicts or spoofing.
