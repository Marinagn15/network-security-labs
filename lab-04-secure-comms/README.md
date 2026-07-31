# Lab 04 — Secure Client-Server Communication (TCP + TLS)

## Overview
This lab implements a three-entity TCP communication protocol in Python, first without encryption (plaintext visible in Wireshark), then secured end-to-end with TLS using self-signed certificates signed by a custom CA.

**Tools:** `Python 3` `OpenSSL` `Wireshark` `GNS3` `Kali Linux`

---

## Protocol Design

Three entities run independently across two networks:

```
Entity          Machine         Network
-----------     -----------     -------
Student_1       KaliLinux-1     Red A (1.1.1.0/24)
Student_2       KaliLinux-1     Red A (1.1.1.0/24)
Third           KaliLinux-2     Red B (2.2.2.0/24)
```

**Communication flow:**
```
Student_1  ──► Student_2  :  "Student_2: wait for nonce_1 seconds"
Student_2  ──► Third      :  "Third: wait for nonce_1 + nonce_2 seconds"
Third      ──► Student_2  :  "Student_2: wait for nonce_1 + nonce_2 + nonce_3 seconds"
Student_2  ──► Student_1  :  "Student_1: my system shows date -> current_date"
                              Student_1 computes date after nonce_1 seconds
                              Student_1 computes date after nonce_1 + nonce_2 seconds
                              Student_1 computes date after nonce_1 + nonce_2 + nonce_3 seconds
```

Each nonce is a random integer in [1, 10] generated with Python's `random` module.

---

## Exercise 1 — TCP Communication Without TLS

**Files:**
- `script_1.py` — Student_1 (Red A)
- `script_2.py` — Student_2 / relay server (Red A)
- `script_3.py` — Third / upstream server (Red B)

**Architecture:**
- Student_2 acts as server for Student_1
- Third acts as server for Student_2

**Key libraries used:**
```python
import socket
import random
import time
from datetime import datetime
```

**Date formatting used:**
```python
meses = ("enero","febrero","marzo","abril","mayo","junio",
         "julio","agosto","septiembre","octubre","noviembre","diciembre")
hoy = datetime.now()
print(hoy.strftime("{} de {} del {}, Hora: %H, Minutos: %M, Segundos: %S"
      .format(hoy.day, meses[hoy.month-1], hoy.year)))
```

**Wireshark result:** Messages visible in plaintext in the TCP stream (`Analyze > Follow > TCP Stream`).

---

## Exercise 2 — TCP Communication With TLS

The same three scripts extended to use TLS, securing all communication end-to-end.

**Port assignment:**
- Student_2 server (for Student_1): port `4X5`
- Third server (for Student_2): port `24X`

*(where X is the value assigned at the start of the course)*

### Certificate Generation (OpenSSL)

**Step 1 — Generate CA key and self-signed certificate:**
```bash
openssl genrsa -out cakey.pem 2048
openssl req -new -x509 -key cakey.pem -out certCA.pem -days 365
```

**Step 2 — Generate server key and CSR:**
```bash
openssl genrsa -out key.pem 2048
openssl req -new -key key.pem -out cert.csr
```

**Step 3 — Sign the server certificate with the CA:**
```bash
openssl x509 -req -days 365 -in cert.csr -CA certCA.pem -CAkey cakey.pem \
    -CAcreateserial -out cert.pem
```

**Files required to run the scripts:**
```
cert.pem      # Server certificate (signed by CA)
key.pem       # Server private key
certCA.pem    # CA certificate (used by clients to verify the server)
```

### TLS Wrapper (Python)
```python
import ssl

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain('cert.pem', 'key.pem')

# Server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    with context.wrap_socket(s, server_side=True) as tls_socket:
        tls_socket.bind(('0.0.0.0', PORT))
        tls_socket.listen()
        conn, addr = tls_socket.accept()
```

**Wireshark result:** Payload is now encrypted — the TCP stream shows only TLS handshake and encrypted data. Plaintext messages are no longer visible.

---

## Testing Locally

Before deploying to GNS3 machines, all three scripts can be tested on localhost using three independent terminal windows:

```bash
# Terminal 1
python3 script_3.py   # Third (upstream server)

# Terminal 2
python3 script_2.py   # Student_2 (relay)

# Terminal 3
python3 script_1.py   # Student_1 (client)
```
