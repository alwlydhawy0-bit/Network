# 4. Build Guide — Producing the Real `.pkt`

Requirements: **Cisco Packet Tracer 8.2 or later** (free with a Cisco Networking Academy / Skills for All account).

There are two ways to build. Path A (automated) is recommended. Both end with the GUI-only steps in §4, which no script can do.

---

## 1. Path A — Automated build with PTBuilder (≈ 10 minutes)

PTBuilder is a free, open-source Packet Tracer script module that uses Packet Tracer's own internal API to add devices, links and configs.

1. Download `Builder.pts` from <https://github.com/kimmknight/PTBuilder> (file in the repo root).
2. Packet Tracer → **Extensions → Scripting → Configure PT Script Modules → Add…** → select `Builder.pts`.
3. **File → New** (empty workspace).
4. **Extensions → Builder Code Editor**.
5. Open `build/ptbuilder-build.js` from this repository, copy the **entire** contents, paste into the editor, click **Run**.
6. Wait until all devices appear and cables turn green/amber (switch ports take ~30 s for STP; with PortFast edge ports come up quickly). The script then pushes each config and runs `write memory`.
7. **Verify FW-01** (§3) — the ASA config is pushed best-effort because the ASA CLI is not IOS.
8. Do the GUI-only steps in **§4**.
9. **File → Save As → `CORP-Enterprise.pkt`**. This is your real Packet Tracer project.

What the script does / does not do:

| Done by script | Manual (GUI) |
|---|---|
| All 25 devices placed and named | Server services (DNS, DHCP, AAA, NTP, Syslog, HTTP, FTP) |
| All 22 cables | Wireless SSID / WPA2 on AP and guest devices |
| Static IPs on servers, PC-MGMT-01, printer; DHCP on staff PCs | Guest device DHCP (wireless NIC) |
| Full CLI config of ISP-R1, EDGE-R1, CORE-SW1, ACCESS-SW1/2 | ASA config verification (re-paste if needed) |

## 2. Path B — Fully manual build

1. Place devices exactly as in `docs/03-physical-cabling.md` §3.3 (models in `docs/01-design.md` §1.1). Rename each device (click device → **Config** tab → *Display Name*; the CLI hostname is set by the config).
2. Cable everything per `docs/03-physical-cabling.md` §3.1 using the listed cable type.
3. For each Cisco device open **CLI**, press Enter to skip the setup dialog (answer `no` to *initial configuration dialog*), then paste the matching `configs/<DEVICE>.txt`. Paste in this order: ISP-R1, EDGE-R1, FW-01 (see §3), CORE-SW1, ACCESS-SW1, ACCESS-SW2.
   *Tip:* paste in chunks of ~60 lines if your PT version drops characters on very long pastes, then check `show running-config`.
4. End hosts: **Desktop → IP Configuration** with values from `docs/02-ip-addressing.md` (servers, PC-MGMT-01 and PRN-01 static; all other PCs **DHCP**).
5. Continue with §3 and §4, then **File → Save As**.

## 3. FW-01 (ASA 5506-X) — apply / verify

1. Click FW-01 → **CLI**. Type `enable`, press Enter at `Password:` (blank on a new ASA).
2. `show running-config` — check that `nameif outside` / `nameif inside`, the two `route` lines and `access-group OUTSIDE_IN in interface outside` exist.
3. If anything is missing, paste `configs/FW-01.txt` from `configure terminal` downwards (it is idempotent).
4. `show interface ip brief` → Gi1/1 and Gi1/2 **up/up**.
5. If `crypto key generate rsa modulus 1024` asks *"Do you really want to replace them?"*, answer `yes`.

## 4. GUI-only configuration

### 4.1 SRV-DC01 — AD-style identity & infrastructure server (192.168.60.10)

**Services → DHCP** (interface FastEthernet0, Service **On**). Create each pool: type values → **Add**. Edit the built-in `serverPool` (it cannot be deleted) so it covers only the server VLAN's spare range.

| Pool Name | Default Gateway | DNS Server | Start IP Address | Subnet Mask | Maximum Users |
|---|---|---|---|---|---|
| serverPool (edit → **Save**) | 192.168.60.1 | 192.168.60.10 | 192.168.60.200 | 255.255.255.0 | 20 |
| VLAN20-IT | 192.168.20.1 | 192.168.60.10 | 192.168.20.100 | 255.255.255.0 | 100 |
| VLAN30-HR | 192.168.30.1 | 192.168.60.10 | 192.168.30.100 | 255.255.255.0 | 100 |
| VLAN40-FIN | 192.168.40.1 | 192.168.60.10 | 192.168.40.100 | 255.255.255.0 | 100 |
| VLAN50-USERS | 192.168.50.1 | 192.168.60.10 | 192.168.50.100 | 255.255.255.0 | 100 |
| VLAN70-GUEST | 192.168.70.1 | **203.0.113.10** | 192.168.70.100 | 255.255.255.0 | 100 |
| VLAN80-EXEC | 192.168.80.1 | 192.168.60.10 | 192.168.80.100 | 255.255.255.0 | 100 |

(Leave TFTP/WLC as 0.0.0.0.) The relay agent (CORE-SW1 SVI) sets the gateway address in the request; the server picks the pool whose *Default Gateway* subnet matches it.

**Services → DNS** — Service **On**, add **A Records**:

| Name | Address | Purpose |
|---|---|---|
| dc01.corp.local | 192.168.60.10 | Identity server |
| dns.corp.local | 192.168.60.10 | DNS |
| web.corp.local | 192.168.60.20 | Web server |
| intranet.corp.local | 192.168.60.20 | Intranet alias |
| files.corp.local | 192.168.60.30 | File server |
| finance.corp.local | 192.168.60.40 | Finance app |
| prn-01.corp.local | 192.168.50.10 | Printer |
| core-sw1.corp.local | 192.168.10.1 | Core switch |
| access-sw1.corp.local | 192.168.10.11 | Access switch 1 |
| access-sw2.corp.local | 192.168.10.12 | Access switch 2 |
| fw-01.corp.local | 10.0.0.5 | Firewall (inside) |
| edge-r1.corp.local | 10.0.0.1 | Edge router |
| www.example.com | 203.0.113.10 | External site (PT DNS has no forwarders) |

**Services → AAA** — Service **On**.
- *Network Configuration*: Client Name `EDGE-R1`, Client IP `10.0.0.1`, Secret `TacKey2026`, ServerType **Tacacs** → **Add**.
- *User Setup*: Username `it.admin`, Password `ItAdmin2026` → **Add**.

**Services → NTP** — Service **On**, Authentication Disable.
**Services → SYSLOG** — Service **On**.
**Services → HTTP, FTP, EMAIL, TFTP** — turn **Off** (hardening: this server only offers the services it is meant to).

### 4.2 SRV-WEB (192.168.60.20)
**Services → HTTP**: HTTP **On**, HTTPS **On**. Edit `index.html`, e.g.:
```html
<html><body><h1>CORP Intranet</h1><p>web.corp.local - served from VLAN 60</p></body></html>
```
Turn **Off** DHCP, DNS, FTP, EMAIL, AAA, TFTP.

### 4.3 SRV-FILE (192.168.60.30)
**Services → FTP**: Service **On**. Add user `employee` / `Files2026` with Write, Read, Delete, Rename, List → **Add**. Remove the default `cisco/cisco` account. Turn **Off** HTTP/HTTPS, DNS, DHCP, EMAIL, AAA.

### 4.4 SRV-FINAPP (192.168.60.40)
**Services → HTTP**: HTTP **Off**, HTTPS **On**. Edit `index.html`:
```html
<html><body><h1>CORP Finance ERP</h1><p>Restricted: FINANCE and EXECUTIVE only</p></body></html>
```
Turn **Off** FTP, DNS, DHCP, EMAIL, AAA.

### 4.5 INET-SRV (203.0.113.10)
**Services → HTTP**: On; `index.html`: `<h1>www.example.com - You reached the Internet</h1>`.
**Services → DNS**: On; A record `www.example.com` → `203.0.113.10`.

### 4.6 Guest Wi-Fi
**AP-GUEST-01 → Config → Port 1**: SSID `CORP-GUEST`, Authentication **WPA2-PSK**, PSK Pass Phrase `GuestWiFi2026`, Encryption **AES**.

**TAB-GST-01 and PHONE-GST-01 → Config → Wireless0**: SSID `CORP-GUEST`, **WPA2-PSK**, key `GuestWiFi2026`, AES; IP Configuration **DHCP**. A wireless link (dashed waves) to the AP appears; the device should get 192.168.70.10x.

### 4.7 Get DHCP leases
On every staff PC: **Desktop → IP Configuration → DHCP** (toggle Static → DHCP if already selected). Expect "DHCP request successful".

### 4.8 Populate sticky MACs
From each PC/server, ping its gateway once. Port security then learns and stores the MAC (`show port-security address`). Run `write memory` on the switches afterwards (`copy running-config startup-config`) so sticky MACs survive reload.

## 5. Save

**File → Save As** → `CORP-Enterprise.pkt`.

## 6. Packet Tracer version notes (lines that may be rejected)

Packet Tracer implements a subset of IOS that varies slightly by release. A rejected line prints `% Invalid input` and the rest of the paste continues. None of the lines below are required for connectivity:

| Line | Device | If rejected |
|---|---|---|
| `logging trap informational` | all IOS | Ignore — default severity still sent |
| `logging host 192.168.60.10` | 2960 | Use `logging 192.168.60.10` |
| `ip ssh time-out` / `authentication-retries` | 2960 | Ignore |
| `security passwords min-length 10` | EDGE-R1 | Ignore |
| `no dhcpd enable inside` | FW-01 | Ignore — means no factory DHCP config was present |
| `ssh timeout 10` | FW-01 | Ignore |
| `inspect http` / `inspect ftp` | FW-01 | Ignore — `inspect icmp` and `inspect dns` are the important ones |
| `description ...` under ASA interfaces | FW-01 | Not used in the config for that reason |

Lines that **are** required use long-standing Packet Tracer features on these models (they appear in Cisco's own Networking Academy PT activities): VLAN/trunk/access commands, SVIs, `ip routing`, `ip helper-address`, extended named ACLs and `ip access-group`, `ip nat` commands, static routes, `crypto key generate rsa`, `transport input ssh`, `access-class`, port-security, PortFast/BPDU Guard, ASA `nameif`/`security-level`/`route`/`access-group`/`policy-map`.
