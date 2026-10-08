# 1. Design and Decisions

## 1.1 Architecture

The network is a **collapsed-core** design, which suits a single-site organisation of this size (about 10 wired hosts and 4 servers, with room to grow to several hundred).

| Layer | Device | Model | Role |
|---|---|---|---|
| Internet | INET-SRV | Server-PT | Public web site `www.example.com` and public DNS resolver |
| Provider | ISP-R1 | Cisco 2911 | Simulated ISP. Knows only public prefixes. |
| Edge | EDGE-R1 | Cisco 2911 | WAN termination, NAT/PAT, stateless WAN filter, TACACS+ client |
| Perimeter | FW-01 | Cisco ASA 5506-X | Stateful security boundary between the edge and the internal network |
| Core / distribution | CORE-SW1 | Cisco 3560-24PS | Inter-VLAN routing (SVIs), inter-VLAN ACLs, DHCP relay, STP root, server access ports |
| Access | ACCESS-SW1, ACCESS-SW2 | Cisco 2960-24TT | End-host ports, port security, BPDU Guard |
| Wireless | AP-GUEST-01 | AccessPoint-PT | Guest SSID `CORP-GUEST` bridged into VLAN 70 |
| Servers | SRV-DC01, SRV-WEB, SRV-FILE, SRV-FINAPP | Server-PT | Identity/DNS/DHCP/AAA/NTP/Syslog, intranet, file (FTP), finance application |

**Why these models?**
- The **2911** supports NAT, extended ACLs, AAA/TACACS+, SSH and `login block-for` in Packet Tracer without a license change.
- The **3560-24PS** is Packet Tracer's most dependable multilayer switch. It supports `ip routing`, SVIs, routed ports, ACLs on SVIs, `ip helper-address` and port security. The 3650 was avoided because it boots with no power supply in Packet Tracer, a common trap for learners.
- The **2960-24TT** is the standard access switch, with port security, BPDU Guard, PortFast, rapid-PVST and SSH.
- The **ASA 5506-X** is the firewall model Packet Tracer supports. It provides nameif and security levels, interface ACLs, MPF inspection and SSH.

## 1.2 Routing decision: static, not OSPF

The project brief asks for OSPF *only if it is justified*. Here it is not, for three reasons:

1. **There is a single path.** Every packet leaving the site takes exactly one route: CORE-SW1 → FW-01 → EDGE-R1 → ISP. There is no redundant link or second router for a dynamic protocol to choose between or fail over to. OSPF would only advertise what three static routes already express.
2. **The firewall sits in the path.** OSPF between CORE-SW1 and EDGE-R1 would have to cross the ASA. The ASA 5506-X in Packet Tracer has limited and version-dependent dynamic routing support, so OSPF adjacencies through or with it are not dependable. A lab that only works on some Packet Tracer builds is a poor deliverable.
3. **The ISP side is never OSPF.** Enterprise-to-ISP routing uses static defaults or eBGP, never the customer's IGP.

The complete routing table is small and fully deterministic:

| Device | Route | Next hop | Purpose |
|---|---|---|---|
| CORE-SW1 | 0.0.0.0/0 | 10.0.0.5 (FW-01 inside) | Everything non-local goes to the firewall |
| FW-01 | 0.0.0.0/0 | 10.0.0.1 (EDGE-R1) | Internet |
| FW-01 | 192.168.0.0/16 | 10.0.0.6 (CORE-SW1) | Summary of all internal VLANs |
| EDGE-R1 | 0.0.0.0/0 | 198.51.100.1 (ISP-R1) | Internet |
| EDGE-R1 | 192.168.0.0/16 | 10.0.0.2 (FW-01 outside) | Internal VLANs (return traffic after un-NAT) |
| EDGE-R1 | 10.0.0.4/30 | 10.0.0.2 | Reach the FW-01 ↔ CORE-SW1 transit link |
| ISP-R1 | *(none)* | — | Knows only its connected public networks, so NAT is mandatory |

**When to move to OSPF:** add a second core switch or a second edge router, or a branch site over a WAN. At that point run OSPF area 0 between CORE-SW1(s) and the edge, set the router ID to the loopback, make all SVIs passive, and have the edge router originate the default (`default-information originate`). Move the firewall to a design that supports it, such as a firewall on a stick or an ASA with OSPF on a supported platform.

## 1.3 VLAN design

The address plan follows a simple rule: VLAN *N* uses 192.168.*N*.0/24 and its gateway is .1. Within every client subnet:

| Range | Use |
|---|---|
| .1 | Default gateway (CORE-SW1 SVI) |
| .2 – .99 | Reserved for infrastructure and statically addressed devices (never handed out by DHCP) |
| .100 – .199 | DHCP pool |
| .200 – .254 | Reserved for growth |

Changes from the brief's example plan:
- **"Management" is split into two things.** VLAN 10 MANAGEMENT is the *network-management* VLAN: the admin workstation and the switch management SVIs. The *Management department* (executives) has its own VLAN 80 EXECUTIVE, so executives never share a broadcast domain with infrastructure management.
- **VLAN 99 is the native VLAN only.** No hosts and no SVI. A native VLAN that carries management traffic is the classic VLAN-hopping target, so the 192.168.99.0/24 block is reserved but deliberately unused.
- **VLAN 999 PARKING** holds every unused port. Those ports are also shut down.
- **Trunks are pruned.** ACCESS-SW1 carries only 10, 20, 30, 80 and 99. ACCESS-SW2 carries only 10, 40, 50, 70 and 99.
- **VTP is transparent** on all switches, so a rogue switch with a higher revision number cannot wipe the VLAN database.

## 1.4 Services design

| Service | Where | Notes |
|---|---|---|
| DHCP | SRV-DC01, with `ip helper-address` on each client SVI | Centralised, like a Windows DHCP role in an AD domain. One pool per VLAN, matched by the relay's gateway address. |
| Internal DNS (`corp.local`) | SRV-DC01 | Also hosts an A record for `www.example.com`, because Packet Tracer DNS has no forwarders. |
| Public DNS | INET-SRV 203.0.113.10 | Used by guests, who must not touch internal DNS. |
| AAA (TACACS+) | SRV-DC01 | EDGE-R1 logins are checked centrally, with local `netadmin` as fallback. |
| NTP / Syslog | SRV-DC01 | All IOS devices sync time and send logs centrally. |
| Intranet | SRV-WEB | HTTP and HTTPS |
| Files | SRV-FILE | FTP (Packet Tracer's file-transfer service) |
| Finance application | SRV-FINAPP | HTTPS only, restricted by ACL |

## 1.5 Security in depth

| Layer | Control |
|---|---|
| Internet edge | Anti-spoofing plus a stateless "return traffic only" ACL (`WAN_IN`) on EDGE-R1. PAT hides all internal addressing. CDP is disabled toward the ISP. |
| Perimeter | ASA: inside (100) → outside (0) is stateful. Outside → inside is denied except three management flows from EDGE-R1 to SRV-DC01 and ICMP errors. |
| Internal segmentation | One inbound extended ACL per client SVI on CORE-SW1 (least privilege per department) |
| Layer 2 | Sticky port security, BPDU Guard, PortFast, parked and shut unused ports, dedicated unused native VLAN, DTP disabled on trunks, VTP transparent, VLAN 1 SVI shut |
| Device management | SSH v2 only, `access-class` restricted to VLAN 10, local users with `secret` hashes, `service password-encryption`, exec timeouts, login banners, `login block-for` (routers), TACACS+ (EDGE-R1) |
| Visibility | Central syslog and NTP-synchronised timestamps |

Features **deliberately not enabled** in the base build, because they break or behave inconsistently in Packet Tracer (see `docs/05-security-acl-policy.md` §5.6 for optional add-ons):
- **DHCP snooping.** With option 82 inserted by the access switch and relayed by the core, Packet Tracer often drops the leases. It is provided as an optional module with the PT-specific fix.
- **802.1X.** Packet Tracer end hosts have only partial supplicant support.
