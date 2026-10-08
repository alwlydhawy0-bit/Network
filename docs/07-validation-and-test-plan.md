# 7. Validation and Functional Test Plan

Run the tests in order. Each section depends on the previous one. Record **Pass/Fail** in the last column, or copy the file and fill it in.

## 7.1 Device verification commands

### ISP-R1 / EDGE-R1 (Cisco 2911)
| Command | Expected |
|---|---|
| `show ip interface brief` | Gi0/0 and Gi0/1 up/up with the IPs from doc 02. Gi0/2 administratively down. |
| `show ip route` | EDGE-R1: `S* 0.0.0.0/0 [1/0] via 198.51.100.1`, `S 192.168.0.0/16 via 10.0.0.2`, `S 10.0.0.4/30 via 10.0.0.2`. ISP-R1: connected and local routes only. |
| `show ip nat translations` (EDGE-R1) | After clients browse or ping: `icmp/tcp 198.51.100.2:<port> 192.168.x.y:<port> …` (PAT) |
| `show ip nat statistics` (EDGE-R1) | Outside interface Gi0/0, inside Gi0/1, hit counter increasing, `access-list 1 … interface GigabitEthernet0/0 … overload` |
| `show access-lists` (EDGE-R1) | `WAN_IN` match counters increase on `established` and `echo-reply` lines |
| `show ip ssh` | `SSH Enabled - version 2.0` |
| `show running-config \| include aaa\|tacacs` (EDGE-R1) | `aaa new-model`, `tacacs-server host 192.168.60.10 …`, `aaa authentication login default group tacacs+ local` |
| `show ntp status` / `show ntp associations` | Associated with 192.168.60.10 (can take a few minutes in PT; use **Fast Forward Time**) |
| `show cdp neighbors` (EDGE-R1) | Does **not** list ISP-R1 (CDP disabled on WAN) |

### FW-01 (ASA 5506-X)
| Command | Expected |
|---|---|
| `show interface ip brief` | Gi1/1 10.0.0.2 up/up and Gi1/2 10.0.0.5 up/up |
| `show nameif` | Gi1/1 `outside` security 0, Gi1/2 `inside` security 100 |
| `show route` | `S* 0.0.0.0 0.0.0.0 via 10.0.0.1, outside` and `S 192.168.0.0 255.255.0.0 via 10.0.0.6, inside` |
| `show access-list` | `OUTSIDE_IN` with 7 ACEs and hit counts |
| `show running-config policy-map` | `inspect icmp`, `inspect dns`, … |
| `show conn` | Active connections while clients browse |
| `show ssh` | 192.168.10.0 255.255.255.0 inside |

### CORE-SW1 (3560-24PS)
| Command | Expected |
|---|---|
| `show vlan brief` | VLANs 10, 20, 30, 40, 50, 60, 70, 80, 99 and 999 with names. Fa0/1–4 in VLAN 60. Fa0/5–23 in VLAN 999. |
| `show interfaces trunk` | Gi0/1 and Gi0/2 trunking, 802.1q, native 99. Allowed and forwarding: Gi0/1 `10,20,30,80,99`, Gi0/2 `10,40,50,70,99`. |
| `show ip interface brief` | Vlan10–80 up/up (Vlan60 needs a server cable up). Fa0/24 10.0.0.6 up/up. Vlan1 administratively down. |
| `show ip route` | `C` for each 192.168.x.0/24 and 10.0.0.4/30, plus `S* 0.0.0.0/0 [1/0] via 10.0.0.5` |
| `show ip access-lists` | Seven VLAN ACLs. Counters increase during tests 15–24. |
| `show running-config interface vlan 30` | `ip helper-address 192.168.60.10` and `ip access-group VLAN30_HR_IN in` |
| `show spanning-tree vlan 20` | "This bridge is the root". Mode rapid-pvst (`rstp`). |
| `show port-security` | Fa0/1–4 MaxSecureAddr 1, Action Shutdown |
| `show mac address-table` | Server MACs on Fa0/1–4 (VLAN 60). Client MACs learned through Gi0/1 and Gi0/2. |

### ACCESS-SW1 / ACCESS-SW2 (2960-24TT)
| Command | Expected |
|---|---|
| `show vlan brief` | Ports in the VLANs shown in doc 03. Unused ports in VLAN 999. |
| `show interfaces trunk` | Gi0/1 trunking, native 99, pruned allowed list |
| `show interfaces status` | Unused ports `disabled`. Used ports `connected`. |
| `show port-security` / `show port-security address` | One sticky MAC per host port (after test 2). Fa0/6 on SW2: max 5, Restrict. |
| `show spanning-tree interface fa0/2 detail` | `portfast` and `bpdu guard is enabled` |
| `show ip interface brief` | Vlan10 192.168.10.11 (SW1) or .12 (SW2) up/up |
| `show mac address-table` | Host MACs on access ports. Core MAC on Gi0/1. |

> In Packet Tracer, use the **Fast Forward Time** button (bottom bar) to converge STP, DHCP and ARP quickly before testing. The first ping across the network often loses 1–2 packets to ARP. That is normal.

## 7.2 Functional test plan

### A. Addressing and basic reachability

| # | Test | From | Action | Expected result | ✔/✖ |
|---|---|---|---|---|---|
| 1 | Client receives DHCP | PC-HR-01 (repeat on every staff PC) | Desktop → IP Configuration → DHCP | "DHCP request successful". IP 192.168.30.10x, mask 255.255.255.0, GW 192.168.30.1, DNS 192.168.60.10. | |
| 2 | Ping default gateway | PC-HR-01 | `ping 192.168.30.1` | Replies | |
| 3 | Reach DNS server | PC-HR-01 | `ping 192.168.60.10` | Replies | |
| 4 | DNS resolution | PC-HR-01 | `nslookup web.corp.local` | `192.168.60.20` | |
| 5 | Guest Wi-Fi association and DHCP | TAB-GST-01 | Desktop → IP Configuration | 192.168.70.10x, GW 192.168.70.1, DNS **203.0.113.10** | |
| 6 | Infrastructure statics correct | PC-MGMT-01 | `ping 192.168.10.11`, `ping 192.168.10.12` | Both access switches reply | |
| 7 | Inter-VLAN routing | PC-FIN-01 | `ping 192.168.60.20` | Replies (VLAN 40 → 60 through the core SVIs) | |

### B. Services

| # | Test | From | Action | Expected | ✔/✖ |
|---|---|---|---|---|---|
| 8 | Intranet web by name | PC-USR-01 | Web Browser → `http://intranet.corp.local` | "CORP Intranet" page | |
| 9 | Intranet over HTTPS | PC-HR-02 | Browser → `https://web.corp.local` | Page loads | |
| 10 | File server | PC-USR-02 | Command Prompt: `ftp 192.168.60.30`, user `employee` / `Files2026`, then `dir` | Login OK, file list shown | |
| 11 | Finance app (authorised) | PC-FIN-02 | Browser → `https://finance.corp.local` | "CORP Finance ERP" page | |
| 12 | Finance app (executive) | PC-EXEC-01 | Browser → `https://finance.corp.local` | Page loads | |
| 13 | Printer reachable in its VLAN | PC-USR-01 | `ping 192.168.50.10` | Replies | |

### C. Internet, NAT/PAT and traceroute

| # | Test | From | Action | Expected | ✔/✖ |
|---|---|---|---|---|---|
| 14 | Internet ping | PC-IT-01 | `ping 203.0.113.10` | Replies | |
| 15 | Internet web by name | PC-USR-01 | Browser → `http://www.example.com` | "You reached the Internet" | |
| 16 | Guest Internet | TAB-GST-01 | Browser → `http://www.example.com` | Page loads (resolved by public DNS) | |
| 17 | Path verification | PC-IT-01 | `tracert 203.0.113.10` | Hops: 192.168.20.1 → 10.0.0.1 → 198.51.100.1 → 203.0.113.10. FW-01 does not appear, because an ASA does not decrement TTL by default (a transparent security hop). | |
| 18 | PAT translation | EDGE-R1 | `show ip nat translations` right after tests 14–16 | Inside local 192.168.x.x mapped to inside global **198.51.100.2** with different ports | |
| 19 | NAT is necessary | ISP-R1 | `show ip route` | No 192.168.0.0 routes, which proves only translated traffic can return | |
| 20 | Internet cannot initiate inward | ISP-R1 | `ping 192.168.60.20` and `ping 198.51.100.2` then `show access-lists` on EDGE-R1 | Both fail. The first has no route on ISP-R1. The second is unsolicited echo dropped by `WAN_IN`. `ssh -l netadmin 198.51.100.2` from ISP-R1 also fails. The `deny ip any any` counter of `WAN_IN` increases. | |

### D. Segmentation (ACL) — negative tests

| # | Test | From | Action | Expected | ✔/✖ |
|---|---|---|---|---|---|
| 21 | Guest cannot reach servers | TAB-GST-01 | `ping 192.168.60.10`, browser `http://192.168.60.20` | Ping: *Destination host unreachable*. Browser: request timeout. | |
| 22 | Guest cannot reach MGMT, HR, FIN or IT | TAB-GST-01 | `ping 192.168.10.10`, `ping 192.168.30.1`, `ping 192.168.40.1`, `ping 192.168.20.1` | All fail | |
| 23 | Department isolation | PC-HR-01 | `ping <PC-FIN-01 IP>` | Fails | |
| 24 | Finance app denied to non-finance | PC-USR-01 and PC-HR-01 | Browser → `https://finance.corp.local` | Request timeout | |
| 25 | IT denied finance app (ping allowed) | PC-IT-01 | `ping 192.168.60.40` and then browser `https://192.168.60.40` | Ping OK, browser times out | |
| 26 | IT support reach | PC-IT-01 | `ping <PC-HR-01 IP>` | Replies (IT may reach departments) | |
| 27 | Users cannot manage devices | PC-USR-01 | Command Prompt `ssh -l netadmin 192.168.50.1` | Connection fails | |

### E. Secure management and identity

| # | Test | From | Action | Expected | ✔/✖ |
|---|---|---|---|---|---|
| 28 | SSH to core from MGMT | PC-MGMT-01 | `ssh -l netadmin 192.168.10.1` | Password `NetAdmin2026` gives the `CORE-SW1#` prompt (privilege 15) | |
| 29 | SSH to access switches | PC-MGMT-01 | `ssh -l netadmin 192.168.10.11` and `… 192.168.10.12` | Login OK | |
| 30 | AAA (TACACS+) login | PC-MGMT-01 | `ssh -l it.admin 10.0.0.1`, password `ItAdmin2026` | Logs in to EDGE-R1 with the **AAA server account**, which does not exist locally. While the AAA server is reachable, the local `netadmin` is *rejected*: fallback is used only when TACACS+ is unreachable. | |
| 31 | AAA fallback | EDGE-R1 | Turn SRV-DC01 AAA **Off**, then SSH with `netadmin` | Login succeeds through local fallback once TACACS+ times out. Turn AAA back On. | |
| 32 | SSH to firewall | PC-MGMT-01 | `ssh -l netadmin 10.0.0.5` | Login OK at the FW-01 prompt | |
| 33 | Telnet disabled | PC-MGMT-01 | `telnet 192.168.10.1` | Refused (`transport input ssh`) | |
| 34 | Syslog | SRV-DC01 | Services → SYSLOG, after shutting and re-enabling an unused port on CORE-SW1 (`int fa0/5`, `no shut`, `shut`) | Log entries from 192.168.60.1 (CORE-SW1's egress SVI toward the server) appear | |

### F. Layer 2 security

| # | Test | From | Action | Expected | ✔/✖ |
|---|---|---|---|---|---|
| 35 | Port-security violation | ACCESS-SW1 | Disconnect PC-HR-02 from Fa0/5, connect a **new** PC to Fa0/5, then ping from it | Fa0/5 goes **err-disabled**. `show port-security interface fa0/5` shows `Secure-shutdown` and violation count 1. | |
| 36 | Recover the port | ACCESS-SW1 | Reconnect PC-HR-02, then `interface fa0/5`, `shutdown`, `no shutdown` | Port up. The original sticky MAC still matches. | |
| 37 | BPDU Guard | ACCESS-SW2 | Temporarily `no shutdown` Fa0/7 (assign VLAN 50, `spanning-tree bpduguard enable`). Cable a spare 2960 to it. | Port err-disabled on the received BPDU (`%SPANTREE-2-BLOCK_BPDUGUARD`) | |
| 38 | Unused ports disabled | ACCESS-SW1 | Connect a PC to Fa0/10 | Link stays red, because the port is administratively down | |
| 39 | Native VLAN consistent | CORE-SW1 | `show interfaces trunk` | Native 99 on both trunks, no native-VLAN-mismatch CDP messages | |

## 7.3 Troubleshooting quick reference

| Symptom | Likely cause | Check |
|---|---|---|
| PC gets 169.254.x.x | DHCP pool missing or wrong GW on SRV-DC01, helper missing, or trunk not carrying the VLAN | `show run int vlan X`, `show interfaces trunk`, SRV-DC01 DHCP pools |
| Ping gateway OK, other VLANs fail | Expected for blocked flows. Otherwise ACL order or a missing `ip routing`. | `show ip access-lists` counters, `show ip route` |
| Internal OK, Internet fails | ASA routes or `access-group`, EDGE NAT inside/outside reversed, or ACL 1 missing a subnet | FW `show route`, EDGE `show ip nat statistics`, `debug ip nat` |
| Ping to Internet fails, web works | ASA dropping echo-reply | `show run policy-map` (inspect icmp), `OUTSIDE_IN` counters |
| SSH refused from MGMT | RSA keys missing, `ip domain-name` missing, or access-class | `show ip ssh`, `show run \| sec line vty` |
| Host port err-disabled | Port security or BPDU Guard | `show interfaces status err-disabled`, then `shut`/`no shut` |
| Guest has no address | AP SSID/PSK mismatch, or the AP port is in the wrong VLAN | AP Config → Port 1. `show vlan brief` on ACCESS-SW2. |
