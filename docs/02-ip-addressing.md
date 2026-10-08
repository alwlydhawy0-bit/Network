# 2. IP Addressing Plan

All masks /24 (255.255.255.0) unless shown. DNS for internal hosts = 192.168.60.10.

## 2.1 Infrastructure

| Device | Type | Interface | VLAN | IP address | Mask | Default gateway | Purpose |
|---|---|---|---|---|---|---|---|
| ISP-R1 | Router 2911 | Gi0/0 | — | 198.51.100.1 | 255.255.255.252 | — | ISP side of customer WAN link |
| ISP-R1 | Router 2911 | Gi0/1 | — | 203.0.113.1 | 255.255.255.0 | — | Gateway for Internet server segment |
| EDGE-R1 | Router 2911 | Gi0/0 | — | 198.51.100.2 | 255.255.255.252 | 198.51.100.1 (default route) | WAN, NAT outside, PAT address |
| EDGE-R1 | Router 2911 | Gi0/1 | — | 10.0.0.1 | 255.255.255.252 | — | Transit to FW-01, NAT inside |
| FW-01 | ASA 5506-X | Gi1/1 (outside, sec 0) | — | 10.0.0.2 | 255.255.255.252 | 10.0.0.1 (route outside) | Firewall outside |
| FW-01 | ASA 5506-X | Gi1/2 (inside, sec 100) | — | 10.0.0.5 | 255.255.255.252 | — | Firewall inside |
| CORE-SW1 | L3 switch 3560 | Fa0/24 (routed) | — | 10.0.0.6 | 255.255.255.252 | 10.0.0.5 (default route) | Uplink to firewall |
| CORE-SW1 | L3 switch 3560 | Vlan10 | 10 | 192.168.10.1 | 255.255.255.0 | — | Gateway MANAGEMENT |
| CORE-SW1 | L3 switch 3560 | Vlan20 | 20 | 192.168.20.1 | 255.255.255.0 | — | Gateway IT |
| CORE-SW1 | L3 switch 3560 | Vlan30 | 30 | 192.168.30.1 | 255.255.255.0 | — | Gateway HR |
| CORE-SW1 | L3 switch 3560 | Vlan40 | 40 | 192.168.40.1 | 255.255.255.0 | — | Gateway FINANCE |
| CORE-SW1 | L3 switch 3560 | Vlan50 | 50 | 192.168.50.1 | 255.255.255.0 | — | Gateway USERS |
| CORE-SW1 | L3 switch 3560 | Vlan60 | 60 | 192.168.60.1 | 255.255.255.0 | — | Gateway SERVERS |
| CORE-SW1 | L3 switch 3560 | Vlan70 | 70 | 192.168.70.1 | 255.255.255.0 | — | Gateway GUEST |
| CORE-SW1 | L3 switch 3560 | Vlan80 | 80 | 192.168.80.1 | 255.255.255.0 | — | Gateway EXECUTIVE |
| ACCESS-SW1 | Switch 2960 | Vlan10 | 10 | 192.168.10.11 | 255.255.255.0 | 192.168.10.1 | Switch management |
| ACCESS-SW2 | Switch 2960 | Vlan10 | 10 | 192.168.10.12 | 255.255.255.0 | 192.168.10.1 | Switch management |
| AP-GUEST-01 | AccessPoint-PT | Port 0 | 70 | — (L2 bridge) | — | — | Guest SSID CORP-GUEST |

## 2.2 Servers (static)

| Device | Type | Interface | VLAN | IP address | Mask | Gateway | DNS | Purpose |
|---|---|---|---|---|---|---|---|---|
| SRV-DC01 | Server-PT | Fa0 | 60 | 192.168.60.10 | 255.255.255.0 | 192.168.60.1 | 192.168.60.10 | AD-style identity sim: DNS, DHCP, AAA (TACACS+), NTP, Syslog |
| SRV-WEB | Server-PT | Fa0 | 60 | 192.168.60.20 | 255.255.255.0 | 192.168.60.1 | 192.168.60.10 | Intranet (HTTP/HTTPS) |
| SRV-FILE | Server-PT | Fa0 | 60 | 192.168.60.30 | 255.255.255.0 | 192.168.60.1 | 192.168.60.10 | File server (FTP) |
| SRV-FINAPP | Server-PT | Fa0 | 60 | 192.168.60.40 | 255.255.255.0 | 192.168.60.1 | 192.168.60.10 | Finance application (HTTPS) |
| INET-SRV | Server-PT | Fa0 | — | 203.0.113.10 | 255.255.255.0 | 203.0.113.1 | 203.0.113.10 | Public web + public DNS |

## 2.3 Clients

| Device | Type | Switch port | VLAN | IP address | Gateway | DNS | Purpose |
|---|---|---|---|---|---|---|---|
| PC-MGMT-01 | PC-PT | ACCESS-SW1 Fa0/1 | 10 | 192.168.10.10 (static) | 192.168.10.1 | 192.168.60.10 | Network management workstation |
| PC-IT-01 | PC-PT | ACCESS-SW1 Fa0/2 | 20 | DHCP 192.168.20.100–199 | 192.168.20.1 | 192.168.60.10 | IT department |
| PC-IT-02 | PC-PT | ACCESS-SW1 Fa0/3 | 20 | DHCP | 192.168.20.1 | 192.168.60.10 | IT department |
| PC-HR-01 | PC-PT | ACCESS-SW1 Fa0/4 | 30 | DHCP 192.168.30.100–199 | 192.168.30.1 | 192.168.60.10 | HR |
| PC-HR-02 | PC-PT | ACCESS-SW1 Fa0/5 | 30 | DHCP | 192.168.30.1 | 192.168.60.10 | HR |
| PC-EXEC-01 | PC-PT | ACCESS-SW1 Fa0/6 | 80 | DHCP 192.168.80.100–199 | 192.168.80.1 | 192.168.60.10 | Management department |
| PC-FIN-01 | PC-PT | ACCESS-SW2 Fa0/1 | 40 | DHCP 192.168.40.100–199 | 192.168.40.1 | 192.168.60.10 | Finance |
| PC-FIN-02 | PC-PT | ACCESS-SW2 Fa0/2 | 40 | DHCP | 192.168.40.1 | 192.168.60.10 | Finance |
| PC-USR-01 | PC-PT | ACCESS-SW2 Fa0/3 | 50 | DHCP 192.168.50.100–199 | 192.168.50.1 | 192.168.60.10 | General employees |
| PC-USR-02 | PC-PT | ACCESS-SW2 Fa0/4 | 50 | DHCP | 192.168.50.1 | 192.168.60.10 | General employees |
| PRN-01 | Printer-PT | ACCESS-SW2 Fa0/5 | 50 | 192.168.50.10 (static) | 192.168.50.1 | 192.168.60.10 | Network printer |
| TAB-GST-01 | TabletPC-PT | wireless via AP-GUEST-01 | 70 | DHCP 192.168.70.100–199 | 192.168.70.1 | 203.0.113.10 | Guest |
| PHONE-GST-01 | SMARTPHONE-PT | wireless via AP-GUEST-01 | 70 | DHCP | 192.168.70.1 | 203.0.113.10 | Guest |

## 2.4 DHCP scopes (SRV-DC01)

| Pool name | VLAN | Network | Default gateway | DNS | Start | Max users | Range handed out | Excluded (static/infrastructure) |
|---|---|---|---|---|---|---|---|---|
| VLAN20-IT | 20 | 192.168.20.0/24 | 192.168.20.1 | 192.168.60.10 | 192.168.20.100 | 100 | .100–.199 | .1–.99, .200–.254 |
| VLAN30-HR | 30 | 192.168.30.0/24 | 192.168.30.1 | 192.168.60.10 | 192.168.30.100 | 100 | .100–.199 | .1–.99, .200–.254 |
| VLAN40-FIN | 40 | 192.168.40.0/24 | 192.168.40.1 | 192.168.60.10 | 192.168.40.100 | 100 | .100–.199 | .1–.99, .200–.254 |
| VLAN50-USERS | 50 | 192.168.50.0/24 | 192.168.50.1 | 192.168.60.10 | 192.168.50.100 | 100 | .100–.199 | .1–.99 (printer .10), .200–.254 |
| VLAN70-GUEST | 70 | 192.168.70.0/24 | 192.168.70.1 | **203.0.113.10** | 192.168.70.100 | 100 | .100–.199 | .1–.99, .200–.254 |
| VLAN80-EXEC | 80 | 192.168.80.0/24 | 192.168.80.1 | 192.168.60.10 | 192.168.80.100 | 100 | .100–.199 | .1–.99, .200–.254 |

VLAN 10 and VLAN 60 have **no** DHCP scope (all static). VLAN 99/999 carry no hosts.

**Lease time:** Packet Tracer's server DHCP service has no lease-duration setting. In production (Windows Server DHCP) the intended policy is **8 days** for staff VLANs and **4 hours** for VLAN 70 GUEST (high churn, small pool exhaustion risk). Exclusions are enforced by the pool start address + max users instead of an exclusion list.

## 2.5 Public / transit addressing

| Network | Use |
|---|---|
| 198.51.100.0/30 (RFC 5737 TEST-NET-2) | EDGE-R1 ↔ ISP-R1; .2 is the PAT address for the whole company |
| 203.0.113.0/24 (RFC 5737 TEST-NET-3) | "Internet" server segment |
| 10.0.0.0/30 | EDGE-R1 ↔ FW-01 outside |
| 10.0.0.4/30 | FW-01 inside ↔ CORE-SW1 |
