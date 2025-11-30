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
    output = ser.read(2048).decode(errors="ignore")

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

# -------------------- Main Config Function --------------------
def configure_switch(port):
    ser = serial.Serial(port, baudrate=9600, timeout=1)
    time.sleep(1.5)
    print("\n[*] Starting FIU Capstone VLAN + Voice configuration...\n")

    commands = [
        # Basic setup
        "enable",
        "configure terminal",
        "hostname SW1",
        "no ip domain-lookup",
        "service password-encryption",
        "enable secret 123456789",
        "username admin privilege 15 secret 123456789",

        # Console / VTY protection
        "line console 0",
        "password 123456789",
        "login local",
        "exec-timeout 10 0",
        "logging synchronous",
        "exit",

        "line vty 0 15",
        "password 123456789",
        "login local",
        "transport input ssh telnet",
        "exec-timeout 10 0",
        "exit",

        # Default gateway
        "ip default-gateway 192.168.1.1",

        # Management VLAN
        "interface vlan1",
        "ip address 192.168.1.5 255.255.255.0",
        "no shutdown",
        "exit",

        # VLANs
        "vlan 10", "name VOICE", "exit",
        "vlan 20", "name USERS", "exit",
        "vlan 30", "name SERVERS", "exit",
        "vlan 40", "name DEV_TEST", "exit",

        # Enable QoS
        "mls qos",

        # VLAN 10 - VOICE
        "interface range fa0/1 - 16",
        "switchport mode access",
        "switchport access vlan 10",
        "switchport voice vlan 10",
        "mls qos trust cos",
        "description VOICE_PORTS",
        "no shutdown",
        "exit",

        # VLAN 20 - USERS
        "interface range fa0/17 - 30",
        "switchport mode access",
        "switchport access vlan 20",
        "description USERS_PORTS",
        "no shutdown",
        "exit",

        # VLAN 30 - SERVERS
        "interface range fa0/31 - 38",
        "switchport mode access",
        "switchport access vlan 30",
        "description SERVERS_PORTS",
        "no shutdown",
        "exit",

        # VLAN 40 - DEV/TEST
        "interface range fa0/39 - 46",
        "switchport mode access",
        "switchport access vlan 40",
        "description DEV_TEST_PORTS",
        "no shutdown",
        "exit",

        # Trunk uplink to UniFi router
        "interface fa0/47",
        "switchport mode trunk",
        "switchport trunk allowed vlan 1,10,20,30,40",
        "description UPLINK_TO_UNIFI",
        "no shutdown",
        "exit",

        # Disable unused port
        "interface fa0/48",
        "shutdown",
        "description UNUSED_PORT",
        "exit",

        # Banner
        (
            "banner motd #\n"
            "************************************************************\n"
            "*   FLORIDA INTERNATIONAL UNIVERSITY - CAPSTONE SHOWCASE    *\n"
            "*        Swtich VLAN + VOIP NETWORK CONFIGURATION SCRIPT           *\n"
            "************************************************************#"
        ),

        # Save configuration
        "end",
        "copy running-config startup-config"
    ]

    for cmd in commands:
        send_and_confirm(ser, cmd)

    ser.close()

    print("\n[✓] Configuration completed successfully.\n")
    print("Network Summary:")
    print(" • VLAN 10 - Voice (Fa0/1–16)")
    print(" • VLAN 20 - Users (Fa0/17–30)")
    print(" • VLAN 30 - Servers (Fa0/31–38)")
    print(" • VLAN 40 - Dev/Test (Fa0/39–46)")
    print(" • Trunk Port Fa0/47 → UniFi Router")
    print(" • Admin Username: admin / Password: 123456789")
    print(" • Management IP: 192.168.1.5 / Gateway: 192.168.1.1")

# -------------------- Main --------------------
def main():
    port = detect_com_port()
    configure_switch(port)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] {e}")
    input("\nPress Enter to exit...")