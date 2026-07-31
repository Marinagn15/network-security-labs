# Lab 03 — OS Security: Access Control, IDS & Port Scanning

## Overview
This lab covers Linux and Windows access control hardening, kernel-level firewall protection using IPTables, intrusion detection with Snort3, and port/vulnerability scanning with Nmap and OpenVAS.

**Tools:** `IPTables` `Snort3` `Nmap` `OpenVAS` `Wireshark` `Metasploitable2`

---

## Exercise 1 — User Management & Access Control

### 1.1 Linux (Kali Linux)

**Groups created:**
```bash
sudo groupadd -g 878 "grupoA-2025"
sudo groupadd -g 789 "grupoB-2025"
```

**Users created and assigned:**
```bash
sudo adduser -ingroup "grupoA-2025" "user1_Marina_Garcia_Navas-2025"
sudo adduser -ingroup "grupoB-2025" "user2_Rosana_Fuentes_Duque-2025"
sudo adduser -ingroup "grupoB-2025" "user3_CIA-seguridadenredes-2025"
```

**Directory structure per user** (depth 2):
```
carpeta1/
└── subcarpeta2/
    ├── fichero1.txt
    └── fichero2.txt
```

**Permission changes:**
```bash
# Change file owner and group
sudo chown <user> /path/to/fichero2.txt
sudo chgrp <user> /path/to/fichero2.txt

# Set read-only permissions
chmod 444 /path/to/fichero.txt

# Add user3 to sudo
sudo usermod -aG sudo "user3_CIA-seguridadenredes-2025"
```

**Verification:**
```bash
grep "user1_Marina_Garcia_Navas-2025" /etc/passwd
sudo grep "user1_Marina_Garcia_Navas-2025" /etc/shadow
sudo tree -pug /home/user1_Marina_Garcia_Navas-2025/
```

### 1.2 Windows 10/11

Users created via Settings > Accounts or `netplwiz`. `user3_CIA-seguridad en redes` promoted to Administrator.

**Security features enabled:**
- **DEP** — Data Execution Prevention
- **ASLR** — Address Space Layout Randomization  
- **CFG** — Control Flow Guard

Verified via System Properties > Performance Settings > Data Execution Prevention and Task Manager.

---

## Exercise 2 — Kernel Firewall: IPTables + Event Logging

Protection rules defined for two attack types using IPTables with logging before each action rule.

**Flush existing rules first:**
```bash
iptables -P INPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -P OUTPUT ACCEPT
iptables -t nat -F
iptables -t mangle -F
iptables -F
iptables -X
```

**Protection against Smurf Attack (ICMP flood):**
```bash
iptables -A INPUT -p icmp --icmp-type echo-request -m limit --limit 1/s \
    -j LOG --log-prefix "smurf attack: "
iptables -A INPUT -p icmp --icmp-type echo-request -m limit --limit 1/s -j ACCEPT
iptables -A INPUT -p icmp --icmp-type echo-request -j DROP
```

**Protection against SYN Flood:**
```bash
iptables -A INPUT -p tcp --syn -m limit --limit 1/s \
    -j LOG --log-prefix "syn flood: "
iptables -A INPUT -p tcp --syn -m limit --limit 1/s -j ACCEPT
iptables -A INPUT -p tcp --syn -j DROP
```

**Real-time log monitoring:**
```bash
sudo tail -f /var/log/kern.log
```

---

## Exercise 3 — Port Scanning & Vulnerability Assessment

### 3.1 Nmap — Port Scanning

**Target 1: Metasploitable2 VM** (vulnerable machine)

```bash
# Aggressive scan
sudo nmap -sV -T4 <metasploitable_ip>

# Stealth SYN scan (less aggressive)
sudo nmap -sS -T1 <metasploitable_ip>
```

**Target 2: KaliLinux (Kali vs Kali)**

```bash
# TCP + UDP aggressive
sudo nmap -sTU -T4 <kali_ip>

# Passive ping scan
sudo nmap -sP <kali_ip>
```

**IPTables rules to block Nmap reconnaissance on the victim Kali:**
```bash
# Block SYN scans
iptables -A INPUT -p tcp --tcp-flags ALL SYN -m limit --limit 1/s -j ACCEPT
iptables -A INPUT -p tcp --tcp-flags ALL SYN -j DROP

# Block FIN scans
iptables -A INPUT -p tcp --tcp-flags ALL FIN -j DROP
```

**Nmap timing reference:**

| Flag | Mode | Description |
|------|------|-------------|
| `-T0` | Paranoid | Slowest, evades most IDS |
| `-T1` | Sneaky | Slow, evades IDS |
| `-T3` | Normal | Default |
| `-T4` | Aggressive | Fast, detectable |
| `-T5` | Insane | Extremely fast |

### 3.2 OpenVAS — Vulnerability Scanning

Metasploitable2 scanned with OpenVAS to identify:
- **High-risk service** (shown in red): e.g. exposed FTP or HTTP with known CVEs
- **Medium-risk service** (shown in orange/yellow): e.g. outdated SSH configuration

Results analyzed by service category: OS-level accounts, access control, network-facing services.

---

## Snort3 Rules (from Lab 01 IDS component)

```bash
# Install
sudo apt-get install snort3
sudo snort -c /etc/snort/snort.lua  # verify config
```

**Rule: MitM / ARP Spoofing detection**
```
alert arp any any -> any any (
    msg:"MITM - Posible ARP Spoofing"; arp_opcode: 2;
    detection_filter: track by_src, count 5, seconds 10;
    sid:1000001;
)
```

**Rule: Abnormal TCP flags / packet injection**
```
alert tcp any any -> any any (
    msg:"Packet injection - abnormal TCP flags"; flags: SF;
    sid:1000002;
)

alert tcp any any -> any any (
    msg:"Packet injection - stateless TCP"; flow: stateless;
    sid:1000003;
)
```

**Run Snort:**
```bash
sudo snort -c snort.lua -R /etc/snort/rules/local.rules -i eth0 -A alert_fast
```
