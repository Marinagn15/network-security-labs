# Lab 02 — Perimeter Defense

## Overview
This lab focuses on protecting network perimeters against brute force attacks and setting up encrypted tunnels. It covers MikroTik firewall rules, port knocking, Netcat communication analysis, and OpenVPN configuration.

**Tools:** `Hydra` `Netcat` `OpenVPN` `MikroTik RouterOS` `Wireshark`

---

## Exercise 1 — Brute Force & Countermeasures

### 1.1 Brute Force + Blacklists
A brute force SSH attack is launched against MKT-R1 using Hydra, then MikroTik firewall blacklists are configured to progressively block the attacker.

**Preparing the router:**
```bash
/ip ssh set strong-crypto=yes
```

**Attack from KaliLinux-1 (Red A):**
```bash
cd /usr/share/set/src/fasttrack
hydra -l admin -P wordlist.txt -f <router_ip> ssh
```

**Blacklist escalation configured on MikroTik:**
```
Black-list-1 = 1 min  →  Black-list-2 = 3 min  →  Black-list-3 = 2 min  →  Black-list = 200 days
```

Firewall rules built using the jump-target and return technique. Attack effectiveness verified via:
```bash
# MikroTik
/ip firewall address-list print
```

Reference: [MikroTik Bruteforce Login Prevention](https://wiki.mikrotik.com/Bruteforce_login_prevention)

### 1.2 Port Knocking
An alternative to blacklists — the router only opens SSH after receiving a specific sequence of TCP port knocks.

**Secret knock sequence:**
```
TCP/831  →  TCP/841  →  TCP/851
```

**MikroTik firewall rules:**
```bash
# Allow established/related connections
add chain=input connection-state=established,related action=accept

# Knock 1: TCP/831 → add to "port:831" list (1 min TTL)
add chain=input protocol=tcp dst-port=831 action=add-src-to-address-list \
    address-list="port:831" address-list-timeout=1m

# Knock 2: if in port:831 and knocks TCP/841 → add to "port:841"
add chain=input protocol=tcp dst-port=841 src-address-list="port:831" \
    action=add-src-to-address-list address-list="port:841" address-list-timeout=1m

# Knock 3: if in port:841 and knocks TCP/851 → add to "secure"
add chain=input protocol=tcp dst-port=851 src-address-list="port:841" \
    action=add-src-to-address-list address-list="secure" address-list-timeout=5m

# Accept from "secure" hosts only
add chain=input src-address-list=secure action=accept

# Drop everything else
add chain=input action=drop
```

**Testing the knock sequence:**
```bash
knock <router_ip> 831 841 851
```

Reference: [MikroTik Port Knocking](https://wiki.mikrotik.com/Port_Knocking)

---

## Exercise 2 — Netcat + OpenVPN

### Step 1 — Unencrypted communication (Netcat)
Before configuring the VPN, a plaintext channel is established between KaliLinux-1 and KaliLinux-2 to demonstrate the risk of unencrypted traffic.

```bash
# Server (KaliLinux-2)
nc -l -p <port>

# Client (KaliLinux-1)
nc <server_ip> <port>
```

Wireshark capture on the link between client and its switch reveals message payloads in plaintext — even when the connection appears "encrypted" in the protocol label.

### Step 2 — OpenVPN Configuration

**Server-side installation:**
```bash
sudo apt install openvpn easy-rsa
gunzip -c /usr/share/doc/openvpn/examples/sample-config-files/server.conf.gz > /etc/openvpn/server.conf
```

**Key `server.conf` changes:**
```
dh /etc/openvpn/server/dh.pem
push "redirect-gateway def1 bypass-dhcp"
push "dhcp-options DNS 8.8.8.8"
user nobody
group nogroup
ca /etc/openvpn/server/ca.crt
cert /etc/openvpn/server/server.crt
key /etc/openvpn/server/server.key
```

**Enable IP forwarding:**
```bash
echo 1 > /proc/sys/net/ipv4/ip_forward
```

### Step 3 — Verify encryption
Netcat communication repeated over the VPN tunnel. Wireshark confirms the payload is now encrypted — plaintext messages are no longer visible.

**Result:** The VPN tunnel successfully protects traffic that was previously exposed in plaintext.
