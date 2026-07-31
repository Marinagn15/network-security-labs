# Network Security Labs 

Hands-on network security labs developed as part of the **Internet Services and Protocol Security** course (2nd year, Cybersecurity & AI — Universidad de Málaga).

All labs were built using GNS3 with MikroTik routers and Kali Linux machines running in a simulated two-network environment.

---

## Environment

```
NAT1 (GNS3VM - Internet)
        |
   MKT-R1 (MikroTik Router)
   /              \
RED A              RED B
1.1.1.0/24       2.2.2.0/24
Switch1           Switch2
PC1, PC2, PC3    PC4, PC5, PC6
KaliLinux-1      KaliLinux-2
```

**Tools used across all labs:**
`GNS3` `GNS3 VM` `Kali Linux` `MikroTik RouterOS` `Wireshark` `VirtualBox / VMware`

---

## Labs

| Lab | Topic | Key Tools |
|-----|-------|-----------|
| [Lab 01](./lab-01-dos-attacks/) | DoS Attacks, Packet Injection & ARP Spoofing | hping3, Scapy, arpspoof, Wireshark |
| [Lab 02](./lab-02-perimeter-defense/) | Perimeter Defense: Brute Force, Port Knocking, VPN | Hydra, Netcat, OpenVPN, MikroTik Firewall |
| [Lab 03](./lab-03-os-security/) | OS Security: Access Control, IDS, Port Scanning | IPTables, Snort3, Nmap, OpenVAS |
| [Lab 04](./lab-04-secure-comms/) | Secure Client-Server Communication (TCP + TLS) | Python sockets, OpenSSL, Wireshark |

---

## Course
**Seguridad en Servicios y Protocolos de Internet** · Universidad de Málaga  
Grado en Ciberseguridad e Inteligencia Artificial
