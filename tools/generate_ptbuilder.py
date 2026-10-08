#!/usr/bin/env python3
"""Generate build/ptbuilder-build.js from the topology below and configs/*.txt.

The output is pasted into the PTBuilder extension inside Cisco Packet Tracer
(Extensions > Builder Code Editor). PTBuilder then places every device,
cables it, sets end-host IP settings and pushes the CLI configs. You save the
result from Packet Tracer as a genuine .pkt file.

configs/*.txt stay the single source of truth: edit a config, re-run this
script, and the build script picks the change up.

Usage:  python3 tools/generate_ptbuilder.py
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONFIGS = ROOT / "configs"
OUT = ROOT / "build" / "ptbuilder-build.js"

# (name, PTBuilder model string, x, y)
DEVICES = [
    ("INET-SRV",    "Server-PT",      900,  60),
    ("ISP-R1",      "2911",           600,  60),
    ("EDGE-R1",     "2911",           600, 180),
    ("FW-01",       "5506-X",         600, 300),
    ("CORE-SW1",    "3560-24PS",      600, 420),
    ("SRV-DC01",    "Server-PT",      900, 330),
    ("SRV-WEB",     "Server-PT",      900, 400),
    ("SRV-FILE",    "Server-PT",      900, 470),
    ("SRV-FINAPP",  "Server-PT",      900, 540),
    ("ACCESS-SW1",  "2960-24TT",      300, 560),
    ("ACCESS-SW2",  "2960-24TT",      700, 560),
    ("PC-MGMT-01",  "PC-PT",           50, 720),
    ("PC-IT-01",    "PC-PT",          130, 720),
    ("PC-IT-02",    "PC-PT",          210, 720),
    ("PC-HR-01",    "PC-PT",          290, 720),
    ("PC-HR-02",    "PC-PT",          370, 720),
    ("PC-EXEC-01",  "PC-PT",          450, 720),
    ("PC-FIN-01",   "PC-PT",          550, 720),
    ("PC-FIN-02",   "PC-PT",          630, 720),
    ("PC-USR-01",   "PC-PT",          710, 720),
    ("PC-USR-02",   "PC-PT",          790, 720),
    ("PRN-01",      "Printer-PT",     870, 720),
    ("AP-GUEST-01", "AccessPoint-PT", 970, 640),
    ("TAB-GST-01",  "TabletPC-PT",    950, 780),
    ("PHONE-GST-01", "SMARTPHONE-PT", 1050, 780),
]

# (dev1, if1, dev2, if2, cable)  -- classic MDI/MDI-X rules:
# like devices (router-router, switch-switch, router-host) = cross, else straight
LINKS = [
    ("ISP-R1",   "GigabitEthernet0/0", "EDGE-R1",    "GigabitEthernet0/0", "cross"),
    ("ISP-R1",   "GigabitEthernet0/1", "INET-SRV",   "FastEthernet0",      "cross"),
    ("EDGE-R1",  "GigabitEthernet0/1", "FW-01",      "GigabitEthernet1/1", "cross"),
    ("FW-01",    "GigabitEthernet1/2", "CORE-SW1",   "FastEthernet0/24",   "straight"),
    ("CORE-SW1", "GigabitEthernet0/1", "ACCESS-SW1", "GigabitEthernet0/1", "cross"),
    ("CORE-SW1", "GigabitEthernet0/2", "ACCESS-SW2", "GigabitEthernet0/1", "cross"),
    ("CORE-SW1", "FastEthernet0/1",    "SRV-DC01",   "FastEthernet0",      "straight"),
    ("CORE-SW1", "FastEthernet0/2",    "SRV-WEB",    "FastEthernet0",      "straight"),
    ("CORE-SW1", "FastEthernet0/3",    "SRV-FILE",   "FastEthernet0",      "straight"),
    ("CORE-SW1", "FastEthernet0/4",    "SRV-FINAPP", "FastEthernet0",      "straight"),
    ("ACCESS-SW1", "FastEthernet0/1",  "PC-MGMT-01", "FastEthernet0",      "straight"),
    ("ACCESS-SW1", "FastEthernet0/2",  "PC-IT-01",   "FastEthernet0",      "straight"),
    ("ACCESS-SW1", "FastEthernet0/3",  "PC-IT-02",   "FastEthernet0",      "straight"),
    ("ACCESS-SW1", "FastEthernet0/4",  "PC-HR-01",   "FastEthernet0",      "straight"),
    ("ACCESS-SW1", "FastEthernet0/5",  "PC-HR-02",   "FastEthernet0",      "straight"),
    ("ACCESS-SW1", "FastEthernet0/6",  "PC-EXEC-01", "FastEthernet0",      "straight"),
    ("ACCESS-SW2", "FastEthernet0/1",  "PC-FIN-01",  "FastEthernet0",      "straight"),
    ("ACCESS-SW2", "FastEthernet0/2",  "PC-FIN-02",  "FastEthernet0",      "straight"),
    ("ACCESS-SW2", "FastEthernet0/3",  "PC-USR-01",  "FastEthernet0",      "straight"),
    ("ACCESS-SW2", "FastEthernet0/4",  "PC-USR-02",  "FastEthernet0",      "straight"),
    ("ACCESS-SW2", "FastEthernet0/5",  "PRN-01",     "FastEthernet0",      "straight"),
    ("ACCESS-SW2", "FastEthernet0/6",  "AP-GUEST-01", "Port 0",            "straight"),
]

# End hosts with a FastEthernet0 port: (name, dhcp, ip, mask, gw, dns)
HOSTS = [
    ("INET-SRV",   False, "203.0.113.10", "255.255.255.0", "203.0.113.1", "203.0.113.10"),
    ("SRV-DC01",   False, "192.168.60.10", "255.255.255.0", "192.168.60.1", "192.168.60.10"),
    ("SRV-WEB",    False, "192.168.60.20", "255.255.255.0", "192.168.60.1", "192.168.60.10"),
    ("SRV-FILE",   False, "192.168.60.30", "255.255.255.0", "192.168.60.1", "192.168.60.10"),
    ("SRV-FINAPP", False, "192.168.60.40", "255.255.255.0", "192.168.60.1", "192.168.60.10"),
    ("PC-MGMT-01", False, "192.168.10.10", "255.255.255.0", "192.168.10.1", "192.168.60.10"),
    ("PRN-01",     False, "192.168.50.10", "255.255.255.0", "192.168.50.1", "192.168.60.10"),
] + [(pc, True, None, None, None, None) for pc in (
    "PC-IT-01", "PC-IT-02", "PC-HR-01", "PC-HR-02", "PC-EXEC-01",
    "PC-FIN-01", "PC-FIN-02", "PC-USR-01", "PC-USR-02")]

# Configured in this order: provider first, then edge, core, access.
IOS_DEVICES = ["ISP-R1", "EDGE-R1", "CORE-SW1", "ACCESS-SW1", "ACCESS-SW2"]
# The ASA CLI is not IOS; PTBuilder pushes it best-effort (see docs/04).
ASA_DEVICES = ["FW-01"]

# Lines that PTBuilder handles itself (it starts in global config mode and
# runs "write memory" at the end).
SKIP = {"enable", "configure terminal", "end", "write memory"}


def config_commands(name):
    lines = []
    for raw in (CONFIGS / f"{name}.txt").read_text().splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("!"):
            continue
        if line.strip() in SKIP:
            continue
        lines.append(line)
    return "\n".join(lines)


def js(value):
    return json.dumps(value)


def main():
    out = [
        "// =====================================================================",
        "// CORP enterprise network - PTBuilder build script",
        "// GENERATED by tools/generate_ptbuilder.py from configs/*.txt - do not edit.",
        "// Use: Packet Tracer 8.2+ > Extensions > Builder Code Editor > paste > Run.",
        "// Start from an EMPTY workspace (File > New). Then File > Save As .pkt.",
        "// Server services, wireless and ASA verification are manual: docs/04-build-guide.md",
        "// =====================================================================",
        "",
        "// ---- 1. Devices ----",
    ]
    for name, model, x, y in DEVICES:
        out.append(f"addDevice({js(name)}, {js(model)}, {x}, {y});")
    out += ["", "// ---- 2. Cabling ----"]
    for d1, i1, d2, i2, cable in LINKS:
        out.append(f"addLink({js(d1)}, {js(i1)}, {js(d2)}, {js(i2)}, {js(cable)});")
    out += ["", "// ---- 3. End-host IP settings (static servers, DHCP clients) ----"]
    for name, dhcp, ip, mask, gw, dns in HOSTS:
        if dhcp:
            out.append(f"configurePcIp({js(name)}, true);")
        else:
            out.append(f"configurePcIp({js(name)}, false, {js(ip)}, {js(mask)}, {js(gw)}, {js(dns)});")
    out += ["", "// ---- 4. Cisco IOS configurations ----"]
    for name in IOS_DEVICES:
        out.append(f"configureIosDevice({js(name)}, {js(config_commands(name))});")
    out += ["", "// ---- 5. ASA configuration (best effort - verify per docs/04) ----"]
    for name in ASA_DEVICES:
        out.append(f"configureIosDevice({js(name)}, {js(config_commands(name))});")
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(out) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
