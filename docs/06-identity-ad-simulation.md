# 6. Active Directory–Style Identity Simulation

> **This project does NOT contain a Microsoft Active Directory Domain Controller.**
> Packet Tracer cannot run Windows Server, Kerberos, LDAP, Group Policy or AD replication. SRV-DC01 is a **Packet Tracer Server-PT** set up to play the *network-facing roles* a domain controller usually holds. That keeps the enterprise architecture and traffic flows realistic. The name "DC01" describes the role. It is not a claim of AD functionality.

## 6.1 What is simulated, and how

| Real AD-domain function | Real-world component | Simulation in this lab |
|---|---|---|
| Domain name system for `corp.local` | AD-integrated DNS zone on the DC | SRV-DC01 DNS service: A records for every server and network device |
| Client addressing | Windows DHCP role (authorised in AD) | SRV-DC01 DHCP: one scope per VLAN through `ip helper-address` |
| Centralised admin authentication | AD users + NPS (RADIUS) or ISE (TACACS+) | SRV-DC01 AAA (TACACS+) with user `it.admin`. EDGE-R1 authenticates against it, falling back to local `netadmin`. |
| Time source (Kerberos needs < 5 min skew) | PDC Emulator is the authoritative NTP source | SRV-DC01 NTP. All IOS devices run `ntp server 192.168.60.10`. |
| Security event collection | DC event logs and SIEM | SRV-DC01 Syslog. IOS devices run `logging host 192.168.60.10`. |
| Resource access by group | AD security groups + share and NTFS ACLs | VLAN membership per department + CORE-SW1 ACLs (FINANCE/EXEC → finance app) |
| User sign-in to file shares | Kerberos/NTLM to SMB | FTP user accounts on SRV-FILE |

Conceptual flow demonstrated:

```
User (PC-FIN-01)
  └─ DHCP via relay ────────────────► SRV-DC01 (address, gateway, DNS = DC)
  └─ DNS query finance.corp.local ──► SRV-DC01 DNS
  └─ HTTPS to SRV-FINAPP ───────────► permitted by VLAN40_FIN_IN (group-based policy)
Administrator (PC-MGMT-01)
  └─ SSH to EDGE-R1 ────────────────► EDGE-R1 ──TACACS+──► SRV-DC01 AAA (identity check)
                                                 └─ syslog/NTP ──► SRV-DC01
```

## 6.2 Connecting a real Active Directory to this design

Packet Tracer cannot bridge to real virtual machines, so a real AD needs a real or emulated lab. Use GNS3, EVE-NG or CML with IOSv/IOSvL2 images, or physical Cisco gear. The configs in `configs/` carry over almost unchanged:

1. Deploy **Windows Server 2022** at `192.168.60.10/24`, gateway `192.168.60.1`. Install the **AD DS** role and promote it to a new forest `corp.local`. DNS installs with it.
2. Add the **DHCP** role. Authorise it in AD and create the six scopes from `docs/02-ip-addressing.md` §2.4 (lease 8 days for staff, 4 hours for guests). The existing `ip helper-address` lines work as-is.
3. Set the DNS **forwarder** to the ISP resolver. Then remove the `www.example.com` static record.
4. Add **NPS** (RADIUS) and register the network devices as RADIUS clients. On IOS, replace TACACS+ with:
   ```
   radius server DC01
    address ipv4 192.168.60.10 auth-port 1812 acct-port 1813
    key <shared-secret>
   aaa authentication login default group radius local
   ```
   Restrict admin logins to the AD group `GG-Network-Admins` in the NPS network policy. For TACACS+ with command authorisation, use **Cisco ISE** joined to AD.
5. Allow AD traffic in the CORE-SW1 ACLs for domain-joined client VLANs. Add these lines before the `deny ip any 192.168.0.0 …` line:
   ```
   permit tcp <net> host 192.168.60.10 eq 88          ! Kerberos
   permit udp <net> host 192.168.60.10 eq 88
   permit tcp <net> host 192.168.60.10 eq 389         ! LDAP
   permit udp <net> host 192.168.60.10 eq 389
   permit tcp <net> host 192.168.60.10 eq 445         ! SMB (SYSVOL / GPO)
   permit tcp <net> host 192.168.60.10 eq 135         ! RPC endpoint mapper
   permit tcp <net> host 192.168.60.10 range 49152 65535  ! RPC dynamic
   permit tcp <net> host 192.168.60.10 eq 3268        ! Global Catalog
   permit udp <net> host 192.168.60.10 eq 123         ! NTP (Windows time)
   ```
   The GUEST ACL stays unchanged. Guests never talk to the DC except for DHCP.
6. Optionally enable **802.1X** on the access ports against NPS/ISE for identity-based VLAN assignment, which replaces static access VLANs. Do this on real or emulated switches, not in Packet Tracer.
7. Add a second DC (`SRV-DC02`, 192.168.60.11) for redundancy. Add it as a second `ip helper-address`, secondary DNS in the scopes and a second RADIUS server.
