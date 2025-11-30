import serial
import serial.tools.list_ports
import time
import re

# -------------------- Detect COM Port --------------------
def detect_com_port():
    ports = serial.tools.list_ports.comports()
    if not ports:
        raise Exception("No serial ports detected.")
    for p in ports:
        if "USB" in p.description.upper() or "SERIAL" in p.description.upper():
            print(f"[✓] Using detected port: {p.device}")
            return p.device
    return ports[0].device

# -------------------- Send Command --------------------
def send_and_confirm(ser, cmd, delay=0.4):
    ser.write((cmd + "\r").encode())
    time.sleep(delay)
    output = ser.read(4096).decode(errors="ignore")

    if re.search(r"\[confirm\]", output, re.I):
        ser.write(b"\r")
        print(f"   ↳ Confirmed [confirm] for: {cmd}")
    elif "Destination filename" in output:
        ser.write(b"\r")
        print("   ↳ Confirmed copy destination filename")
    elif "Building configuration" in output:
        print("   ↳ Saving configuration...")
    else:
        print(f"→ {cmd}")

# -------------------- Send Banner (interactive MOTD) --------------------
def send_banner(ser):
    ser.write(b"banner motd #\r")
    time.sleep(0.3)

    lines = [
        "************************************************************",
        "*   FLORIDA INTERNATIONAL UNIVERSITY - CAPSTONE SHOWCASE    *",
        "*   CISCO 2600 AUTOMATED ROUTER CONFIGURATION DEPLOYMENT    *",
        "************************************************************"
    ]

    for line in lines:
        ser.write((line + "\r").encode())
        time.sleep(0.2)

    ser.write(b"#\r")
    time.sleep(0.3)
    print("→ Banner MOTD configured")

# -------------------- Main Config Function --------------------
def configure_router(port):
    ser = serial.Serial(port, baudrate=9600, timeout=1)
    time.sleep(1.5)
    print("\n[*] Starting FIU Capstone Cisco 2600 Router configuration...\n")

    commands = [
        # ---------- BASIC SYSTEM ----------
        "enable",
        "configure terminal",
        "hostname FIU_SHOWCASE_FIREWALL",
        "no ip domain-lookup",
        "service password-encryption",

        # Passwords / users
        "enable secret 123456789",
        "username admin privilege 15 secret 123456789",

        # ---------- CONSOLE / VTY SECURITY ----------
        "line console 0",
        "password 123456789",
        "login local",
        "exec-timeout 10 0",
        "logging synchronous",
        "exit",

        "line vty 0 4",
        "password 123456789",
        "login local",
        "transport input ssh telnet",
        "exec-timeout 10 0",
        "exit",

        # ---------- NETWORK BASICS ----------
        "ip domain-name fiu.lab",
        "ip cef",

        # ---------- DHCP ----------
        "ip dhcp excluded-address 192.168.1.1 192.168.1.10",
        "ip dhcp pool LAN01",
        "network 192.168.1.0 255.255.255.0",
        "default-router 192.168.1.1",
        "dns-server 8.8.8.8",
        "lease 7",
        "exit",

        # ---------- ACLs ----------
        "access-list 1 permit 192.168.1.0 0.0.0.255",
        "access-list 10 permit 192.168.1.50",
        "access-list 10 deny any",
        "access-list 100 permit tcp 192.168.1.0 0.0.0.255 any eq 80",
        "access-list 100 permit tcp 192.168.1.0 0.0.0.255 any eq 443",
        "access-list 100 permit udp 192.168.1.0 0.0.0.255 any eq 53",
        "access-list 100 deny ip any any log",
        "access-list 110 permit ip 192.168.1.0 0.0.0.255 10.10.10.0 0.0.0.255",
        "access-list 120 permit ip 192.168.1.0 0.0.0.255 10.10.10.0 0.0.0.255",

        # ---------- VPN / CRYPTO ----------
        "crypto isakmp policy 10",
        "encr aes 128",
        "hash sha",
        "authentication pre-share",
        "group 2",
        "lifetime 86400",
        "exit",

        "crypto isakmp key MySharedKey123 address 60.60.60.1",
        "crypto ipsec transform-set VPN-SET esp-aes esp-sha-hmac",
        "exit",
        "crypto map VPN-MAP 10 ipsec-isakmp",
        "set peer 60.60.60.1",
        "set transform-set VPN-SET",
        "match address 110",
        "exit",

        # ---------- NAT ----------
        "route-map NONAT permit 10",
        "match ip address 120",
        "exit",
        "ip nat inside source route-map NONAT interface Serial0/0 overload",

        # ---------- INTERFACES ----------
        "interface FastEthernet0/0",
        "description LAN Interface",
        "ip address 192.168.1.1 255.255.255.0",
        "ip nat inside",
        "ip access-group 100 in",
        "no shutdown",
        "exit",

        "interface Serial0/0",
        "description WAN to ISP / VPN Endpoint",
        "ip address 50.50.50.1 255.255.255.252",
        "ip nat outside",
        "crypto map VPN-MAP",
        "clock rate 64000",
        "no shutdown",
        "exit",

        "interface Loopback0",
        "ip address 172.16.0.1 255.255.255.255",
        "exit",

        # ---------- ROUTING ----------
        "ip route 0.0.0.0 0.0.0.0 50.50.50.2",
        "ip route 10.10.10.0 255.255.255.0 50.50.50.2",

        # ---------- SERVICES ----------
        "ip http server",
        "ip http secure-server",
        "ip http access-class 10",
        "ip http authentication local",
        "crypto key generate rsa modulus 1024",
        "ip ssh time-out 60",
        "ip ssh authentication-retries 3",
        "logging buffered 4096 debugging",
    ]

    for cmd in commands:
        send_and_confirm(ser, cmd)

    send_banner(ser)

    send_and_confirm(ser, "end")
    send_and_confirm(ser, "copy running-config startup-config")

    ser.close()

    print("\n[✓] Cisco 2600 configuration completed successfully.\n")
    print("Router Name: FIU_SHOWCASE_FIREWALL")

# -------------------- Main --------------------
def main():
    port = detect_com_port()
    configure_router(port)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] {e}")
    input("\nPress Enter to exit...")
