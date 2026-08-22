# Web Security & Cryptography Essentials

## 1. Fundamental Cryptographic Concepts

### Hashing vs Encryption vs Encoding

| Feature | Encoding | Hashing | Encryption |
|---|---|---|---|
| **Purpose** | Data format transformation for compatibility | Data integrity verification & non-reversible transformation | Confidentiality & data protection |
| **Reversibility** | Fully reversible (no key needed) | One-way mathematical function (non-reversible) | Reversible with correct secret key |
| **Examples** | Base64, ASCII, Hexadecimal, URL Encoding | SHA-256, SHA-3, Argon2, bcrypt | AES-256, RSA, ECC, ChaCha20 |

---

## 2. Symmetric vs Asymmetric Encryption

### Symmetric Encryption
- **Mechanics**: Uses a **single shared secret key** for both encryption and decryption.
- **Algorithms**: Advanced Encryption Standard (AES-128/192/256), ChaCha20, 3DES (legacy).
- **Pros & Cons**: Extremely fast and computationally efficient; key distribution is difficult across open networks.

### Asymmetric Encryption (Public-Key Cryptography)
- **Mechanics**: Uses a mathematically linked **key pair**:
  - *Public Key*: Shared publicly; used by anyone to encrypt messages intended for the recipient or verify digital signatures.
  - *Private Key*: Kept secret by owner; used to decrypt messages or generate digital signatures.
- **Algorithms**: RSA (2048/4096-bit), Elliptic Curve Cryptography (ECC / Ed25519), Diffie-Hellman Key Exchange.
- **Use Cases**: TLS handshake, SSH authentication, digital signatures, PGP email encryption.

---

## 3. TLS/SSL & HTTPS Architecture

### Transport Layer Security (TLS 1.3)
HTTPS secures web traffic by wrapping HTTP inside TLS encryption.

### Handshake Sequence (TLS 1.3):
1. **Client Hello**: Sends supported cipher suites, TLS version, and key share.
2. **Server Hello**: Selects cipher suite, provides server public key share and X.509 Digital Certificate.
3. **Authentication**: Client verifies server certificate against trusted Root Certificate Authorities (CAs).
4. **Key Derivation**: Both client and server derive symmetric session key via Ephemeral Elliptic Curve Diffie-Hellman (ECDHE).
5. **Encrypted Communication**: Application data (HTTP) is encrypted using fast symmetric encryption (AES-GCM or ChaCha20-Poly1305).

---

## 4. Web Authentication & Session Management

### JSON Web Tokens (JWT)
- **Structure**: `Header.Payload.Signature` (Base64URL encoded strings separated by dots).
- **Header**: Specifies algorithm (e.g., `HS256` or `RS256`).
- **Payload**: Contains claims (user ID, permissions, expiration timestamp `exp`).
- **Signature**: Hash of Header + Payload signed with secret key. Prevents tampering.
- **Vulnerabilities**:
  - `None` algorithm attack: Forging token header with `"alg": "none"`.
  - Weak secret key brute-force (for HMAC-SHA256).
  - Storing sensitive tokens in unencrypted `localStorage` (susceptible to XSS).

### Session Cookies Security Flags
- `HttpOnly`: Prevents client-side JavaScript (`document.cookie`) from reading session cookie. Mitigates XSS cookie theft.
- `Secure`: Ensures cookie is transmitted only over encrypted HTTPS connections.
- `SameSite=Strict / Lax`: Restricts cross-site cookie transmission to mitigate Cross-Site Request Forgery (CSRF).
