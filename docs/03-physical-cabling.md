# 3. Physical Topology & Cabling

## 3.1 Cable table

| # | From (device / port) | To (device / port) | Cable | Link role | VLANs / subnet |
|---|---|---|---|---|---|
| 1 | ISP-R1 Gi0/0 | EDGE-R1 Gi0/0 | Copper cross-over | **WAN** (routed) | 198.51.100.0/30 |
| 2 | ISP-R1 Gi0/1 | INET-SRV Fa0 | Copper cross-over | Routed (ISP LAN) | 203.0.113.0/24 |
| 3 | EDGE-R1 Gi0/1 | FW-01 Gi1/1 | Copper cross-over | **Routed** (FW outside) | 10.0.0.0/30 |
| 4 | FW-01 Gi1/2 | CORE-SW1 Fa0/24 | Copper straight-through | **Routed** (`no switchport`) | 10.0.0.4/30 |
| 5 | CORE-SW1 Gi0/1 | ACCESS-SW1 Gi0/1 | Copper cross-over | **Trunk** 802.1Q, native 99 | 10,20,30,80 |
| 6 | CORE-SW1 Gi0/2 | ACCESS-SW2 Gi0/1 | Copper cross-over | **Trunk** 802.1Q, native 99 | 10,40,50,70 |
| 7 | CORE-SW1 Fa0/1 | SRV-DC01 Fa0 | Copper straight-through | **Access** | 60 |
| 8 | CORE-SW1 Fa0/2 | SRV-WEB Fa0 | Copper straight-through | Access | 60 |
| 9 | CORE-SW1 Fa0/3 | SRV-FILE Fa0 | Copper straight-through | Access | 60 |
| 10 | CORE-SW1 Fa0/4 | SRV-FINAPP Fa0 | Copper straight-through | Access | 60 |
| 11 | ACCESS-SW1 Fa0/1 | PC-MGMT-01 Fa0 | Copper straight-through | Access | 10 |
| 12 | ACCESS-SW1 Fa0/2 | PC-IT-01 Fa0 | Copper straight-through | Access | 20 |
| 13 | ACCESS-SW1 Fa0/3 | PC-IT-02 Fa0 | Copper straight-through | Access | 20 |
| 14 | ACCESS-SW1 Fa0/4 | PC-HR-01 Fa0 | Copper straight-through | Access | 30 |
| 15 | ACCESS-SW1 Fa0/5 | PC-HR-02 Fa0 | Copper straight-through | Access | 30 |
| 16 | ACCESS-SW1 Fa0/6 | PC-EXEC-01 Fa0 | Copper straight-through | Access | 80 |
| 17 | ACCESS-SW2 Fa0/1 | PC-FIN-01 Fa0 | Copper straight-through | Access | 40 |
| 18 | ACCESS-SW2 Fa0/2 | PC-FIN-02 Fa0 | Copper straight-through | Access | 40 |
| 19 | ACCESS-SW2 Fa0/3 | PC-USR-01 Fa0 | Copper straight-through | Access | 50 |
| 20 | ACCESS-SW2 Fa0/4 | PC-USR-02 Fa0 | Copper straight-through | Access | 50 |
| 21 | ACCESS-SW2 Fa0/5 | PRN-01 Fa0 | Copper straight-through | Access | 50 |
| 22 | ACCESS-SW2 Fa0/6 | AP-GUEST-01 Port 0 | Copper straight-through | Access (AP uplink) | 70 |
| — | AP-GUEST-01 (radio) | TAB-GST-01, PHONE-GST-01 | Wireless (WPA2-PSK) | Wireless | 70 |

Cable rule used: like-to-like devices (router–router, switch–switch, router/firewall–host) use **cross-over**; unlike devices (switch–router/firewall/host/AP) use **straight-through**. (Packet Tracer Gigabit ports usually auto-MDIX, but correct cabling avoids surprises on FastEthernet.)

## 3.2 Unused ports (shut down, VLAN 999)

| Device | Ports |
|---|---|
| EDGE-R1 / ISP-R1 | Gi0/2 |
| CORE-SW1 | Fa0/5 – Fa0/23 |
| ACCESS-SW1 | Fa0/7 – Fa0/24, Gi0/2 |
| ACCESS-SW2 | Fa0/7 – Fa0/24, Gi0/2 |

## 3.3 Suggested workspace placement (logical view, x/y as used by the build script)

```
                         ISP-R1 (600,60) ──── INET-SRV (900,60)
                            │
                         EDGE-R1 (600,180)
                            │
                         FW-01 (600,300)                 SRV-DC01   (900,330)
                            │                            SRV-WEB    (900,400)
                         CORE-SW1 (600,420) ─────────────SRV-FILE   (900,470)
                         /            \                  SRV-FINAPP (900,540)
          ACCESS-SW1 (300,560)    ACCESS-SW2 (700,560)          AP-GUEST-01 (970,640)
          /  /  |  |  \  \          /  |  |  \  \                  )))  TAB-GST-01, PHONE-GST-01
   MGMT IT-01 IT-02 HR-01 HR-02 EXEC  FIN-01 FIN-02 USR-01 USR-02 PRN-01      (y = 720-780)
```
