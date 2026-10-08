# 5. Security & ACL Policy

## 5.1 Access policy matrix (who may start a connection to what)

| From \ To | MGMT 10 | IT 20 | HR 30 | FIN 40 | USERS 50 | DC01 (DNS) | WEB | FILE | FINAPP | Network devices (SSH) | Internet |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **MGMT 10** | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |
| **IT 20** | ✖ | ✔ | ✔ | ✔ | ✔ | ✔ all | ✔ | ✔ | ping only | ✖ | ✔ |
| **HR 30** | ✖ | ✖ | ✔ (L2) | ✖ | ✖ | DNS | 80/443 | FTP | ✖ | ✖ | ✔ |
| **FIN 40** | ✖ | ✖ | ✖ | ✔ (L2) | ✖ | DNS | 80/443 | FTP | **443** | ✖ | ✔ |
| **USERS 50** | ✖ | ✖ | ✖ | ✖ | ✔ (L2, printer) | DNS | 80/443 | FTP | ✖ | ✖ | ✔ |
| **EXEC 80** | ✖ | ✖ | ✖ | ✖ | ✖ | DNS | 80/443 | FTP | **443** | ✖ | ✔ |
| **GUEST 70** | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ✖ | ✔ |

Ping to the servers (VLAN 60) is allowed from all staff VLANs for troubleshooting. Every VLAN may ping its own gateway. DHCP is always allowed.

## 5.2 Design principles

- **Where:** One extended ACL per client VLAN, applied **inbound on the SVI** of CORE-SW1. That is as close to the source as an L3 decision can be made, so denied traffic never crosses the core.
- **Statelessness:** The 3560 ACLs are stateless. When MANAGEMENT or IT start a session into a department VLAN, the reply has to be permitted on the way back. Each department ACL therefore permits only `echo-reply` and TCP `established` (ACK or RST set) toward VLANs 10 and 20. This lets the replies through without allowing new connections in that direction.
- **Internet access without `permit ip any any`:** Each ACL first denies *every* private destination (192.168.0.0/16, 10.0.0.0/8, 172.16.0.0/12). The final permit is `permit ip <own-subnet> any`. It can now only match public destinations, and it anti-spoofs the source. Anything else hits the explicit `deny ip any any` (visible in counters).
- **Device administration:** The only path is SSH from VLAN 10. This is enforced twice. The SVI ACLs block other VLANs from reaching device addresses, and every device has `access-class 10 in` on its VTY lines.

## 5.3 CORE-SW1 ACLs — rule by rule

### VLAN10_MGMT_IN (on Vlan10)
| Rule | Why |
|---|---|
| `permit ip 192.168.10.0 0.0.0.255 any` | Administrators and the switch management SVIs need full reach. The source is restricted to anti-spoof. |
| `deny ip any any` | Spoofed sources |

### VLAN20_IT_IN (on Vlan20)
| Rule | Why |
|---|---|
| `permit udp any eq bootpc any eq bootps` | DHCP Discover/Request (src 0.0.0.0 → 255.255.255.255) and unicast renewals |
| `permit icmp … 192.168.10.0 … echo-reply` | Lets MANAGEMENT ping IT PCs |
| `permit tcp … 192.168.10.0 … established` | Replies to TCP sessions started by MANAGEMENT |
| `deny ip any 192.168.10.0 0.0.0.255` | IT cannot start anything toward the MANAGEMENT VLAN |
| `deny tcp any 192.168.0.0 0.0.255.255 eq 22` / `eq telnet` | No device administration from IT. Only VLAN 10 is the admin plane. |
| `deny ip any 10.0.0.0 0.255.255.255` | Transit links (firewall and edge) are not reachable |
| `deny tcp any host 192.168.60.40` | Finance application is restricted. IT can still ping it for troubleshooting. |
| `permit ip 192.168.20.0 0.0.0.255 any` | IT support reaches the other client VLANs, the servers and the Internet |
| `deny ip any any` | Spoofed sources |

### VLAN30_HR_IN / VLAN40_FIN_IN / VLAN50_USERS_IN / VLAN80_EXEC_IN
These share one template. The only difference is the finance-app line.

| Rule | Why |
|---|---|
| `permit udp any eq bootpc any eq bootps` | DHCP |
| `permit icmp <net> host <gw> echo` | Ping own gateway (Test 2) |
| `permit icmp <net> 192.168.10.0/24 echo-reply` and `… 192.168.20.0/24 echo-reply` | Replies to admin and IT pings |
| `permit tcp <net> 192.168.10.0/24 established` and `… 192.168.20.0/24 established` | Replies to admin and IT TCP sessions |
| `permit udp/tcp <net> host 192.168.60.10 eq domain` | DNS |
| `permit tcp <net> host 192.168.60.20 eq www` / `eq 443` | Intranet |
| `permit tcp <net> host 192.168.60.30 eq ftp` | File server |
| `permit icmp <net> 192.168.60.0/24 echo` | Ping servers |
| **FIN and EXEC only:** `permit tcp <net> host 192.168.60.40 eq 443` | Finance application |
| `deny ip any 192.168.0.0/16`, `10.0.0.0/8`, `172.16.0.0/12` | Blocks all other internal traffic: inter-department, MANAGEMENT, device SSH, other servers and ports |
| `permit ip <net> any` | Internet. Only public destinations remain at this point. |
| `deny ip any any` | Spoofed sources |

### VLAN70_GUEST_IN (on Vlan70)
| Rule | Why |
|---|---|
| `permit udp any eq bootpc any eq bootps` | Guests get addresses from SRV-DC01 through the relay. The DHCP payload is the only thing they can send to it. |
| `permit icmp 192.168.70.0/24 host 192.168.70.1 echo` | Ping own gateway |
| `deny ip any 192.168.0.0/16`, `10.0.0.0/8`, `172.16.0.0/12` | No access to servers, MANAGEMENT, HR, FINANCE, IT, USERS, EXEC, internal DNS or infrastructure |
| `permit ip 192.168.70.0/24 any` | Internet only. Guest DNS is the public resolver 203.0.113.10. |
| `deny ip any any` | Spoofed sources |

VLAN 60 (servers) has no inbound ACL. Servers only answer requests, and their replies to clients must flow. Restricting *server-initiated* traffic is a listed hardening extension (§5.6).

## 5.4 Edge and perimeter ACLs

**EDGE-R1 `access-list 1` (NAT):** permits the eight internal /24s (10, 20, 30, 40, 50, 60, 70, 80). VLAN 99 and the transit /30s are not translated.

**EDGE-R1 `WAN_IN` (inbound Gi0/0):**
| Rule | Why |
|---|---|
| deny sources 10/8, 172.16/12, 192.168/16, 127/8 | RFC 1918 and loopback anti-spoofing (BCP 38 style) |
| `permit tcp any any established` | Return traffic for web and FTP sessions started from inside |
| `permit udp any eq domain any` | DNS replies (guests use the public resolver) |
| `permit icmp any any echo-reply` / `time-exceeded` / `unreachable` | Ping, traceroute and PMTU from inside |
| `deny ip any any` | Nothing from the Internet can start a connection inward |

**EDGE-R1 `access-list 10` (VTY):** SSH only from 192.168.10.0/24.

**FW-01 `OUTSIDE_IN` (inbound outside):**
| Rule | Why |
|---|---|
| `permit icmp any any echo-reply` / `time-exceeded` / `unreachable` | Ping and traceroute results for inside hosts (as a backup to `inspect icmp`) |
| `permit tcp host 10.0.0.1 host 192.168.60.10 eq 49` | EDGE-R1 TACACS+ authentication |
| `permit udp host 10.0.0.1 host 192.168.60.10 eq 514` | EDGE-R1 syslog |
| `permit udp host 10.0.0.1 host 192.168.60.10 eq 123` | EDGE-R1 NTP |
| `deny ip any any` | Everything else |

Inside → outside needs no ACL. Security level 100 → 0 is permitted and tracked statefully, and `inspect icmp/dns/http/ftp` handles the replies.

## 5.5 Device hardening checklist

| Control | ISP-R1 | EDGE-R1 | FW-01 | CORE-SW1 | ACCESS-SW1/2 |
|---|---|---|---|---|---|
| `enable secret` / local user with `secret` | ✔ | ✔ | ✔ (ASA `password`, hashed) | ✔ | ✔ |
| `service password-encryption` | ✔ | ✔ | n/a | ✔ | ✔ |
| SSH v2, RSA 1024, Telnet disabled | ✔ | ✔ | ✔ | ✔ | ✔ |
| VTY limited to VLAN 10 | — (ISP) | ✔ `access-class 10` | ✔ `ssh … inside` | ✔ | ✔ |
| TACACS+ with local fallback | — | ✔ | — | — | — |
| Login brute-force protection | — | ✔ `login block-for` | — | — | — |
| Exec timeout and banner | ✔ | ✔ | — | ✔ | ✔ |
| NTP and syslog to SRV-DC01 | — | ✔ | — | ✔ | ✔ |
| CDP off toward the ISP | n/a | ✔ | n/a | — | — |
| Unused ports shut (switches: parked in VLAN 999) | ✔ | ✔ | n/a | ✔ | ✔ |
| Port security (sticky, max 1) and BPDU Guard and PortFast | n/a | n/a | n/a | ✔ servers | ✔ hosts (AP port: max 5, restrict) |
| Native VLAN 99, DTP off, trunks pruned | n/a | n/a | n/a | ✔ | ✔ |
| VTP transparent, VLAN 1 SVI shut | n/a | n/a | n/a | ✔ | ✔ |
| Core is STP root for all VLANs | n/a | n/a | n/a | ✔ | — |

## 5.6 Optional hardening modules (not in base build)

**DHCP snooping (ACCESS-SW1/2).** Test it after the base build works.
```
ip dhcp snooping
ip dhcp snooping vlan 20,30,40,50,70,80
no ip dhcp snooping information option
interface GigabitEthernet0/1
 ip dhcp snooping trust
```
`no ip dhcp snooping information option` is needed. Without it, the access switch inserts option 82 with a zero giaddr, and the relay on CORE-SW1 or the PT DHCP server drops it, so clients lose DHCP.

**Server-initiated traffic restriction** (outbound on Vlan60 is awkward with stateless ACLs). On real hardware, use the ASA or a ZBF for an east-west server zone instead.

**ASA syslog:** `logging enable`, `logging trap informational`, `logging host inside 192.168.60.10`.
