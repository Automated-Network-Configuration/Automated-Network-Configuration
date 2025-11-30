How to Use the FIU Capstone Switch Configuration Script

This Python script automates the configuration of a Cisco switch via the serial console using the pyserial library. The script performs the following tasks:

* Detects the correct COM/USB serial port
* Logs into the switch console
* Implements VLAN, voice, Quality of Service (QoS), and port configurations
* Configures the hostname, management IP address, and message of the day (MOTD) banner
* Saves the running configuration

---

1. Prerequisites and Requirements

1. Hardware
  * Cisco switch (e.g., Catalyst 2950)
  * USB-to-serial adapter (or native serial port)
  * Console cable connected from your PC to the switch’s console port
  * Ensure that the switch is powered on and displays a command-line interface (CLI) prompt, such as Switch> or Switch#.
2. Software
  * Python 3.x installed
  * pyserial library installed
3. To install the pyserial library, enter the following command in your terminal or command prompt:

pip install pyserial


---

2. Overview of the Script

The script uses these key modules:

import serial
import serial.tools.list_ports
import time
import re


* serial and serial.tools.list_ports: Communicate with the switch over the COM port and automatically detect the appropriate port.
* time: Introduces brief delays to allow the switch sufficient time to respond.
* re: Detects prompts such as [confirm] or copy confirmation messages within the switch output.

Core functions:

* detect_com_port()
Identifies the first serial port corresponding to a USB or serial adapter and displays the following message:

[✓] Using detected port: COM3


* send_and_confirm(ser, cmd, delay=0.4)
Sends a command, waits for a response, and then performs the following actions:
  * Automatically answers [confirm] prompts
  * Confirms Destination filename for copy run start
  * Prints which command is being sent
* configure_switch(port)
Establishes a connection to the switch on the specified port and executes all configuration commands in sequence:
  * Basic security (passwords, user)
  * Console and VTY protection
  * Default gateway and management VLAN SVI
  * VLANs 10/20/30/40 and port assignments
  * Configures the voice VLAN and disables the unused port Fa0/48, which is connected to the UniFi router
  * Shuts down unused port Fa0/48
  * Configures a message of the day (MOTD) banner
  * Saves the configuration
* main()
  * Detects the COM port
  * Calls configure_switch(port)
  * Handles errors and waits for Enter before closing

---

3. Network Design Configured by the Script

* Hostname: SW1
* Management
  * VLAN: VLAN 1
  * IP: 192.168.1.5
  * Mask: 255.255.255.0
  * Default gateway: 192.168.1.1
* VLANs
  * VLAN 10 – VOICE
  * VLAN 20 – USERS
  * VLAN 30 – SERVERS
  * VLAN 40 – DEV_TEST
* Port Assignments
  * Fa0/1–16 → VLAN 10 (VOICE) + voice VLAN + QoS trust
  * Fa0/17–30 → VLAN 20 (USERS)
  * Fa0/31–38 → VLAN 30 (SERVERS)
  * Fa0/39–46 → VLAN 40 (DEV_TEST)
  * Fa0/47 → Trunk to UniFi router (VLANs 1,10,20,30,40)
  * Fa0/48 → Disabled (UNUSED_PORT)
* Credentials (demonstration values; modify for production environments)
  * enable secret: 123456789
  * Local admin user: username admin privilege 15 secret 123456789
  * Console password: 123456789
  * VTY password: 123456789

---

4. Script Execution Instructions

1. Establish All Required Connections
  * Plug in the switch and turn it on.
  * Connect USB-to-serial adapter to your PC.
  * Connect console cable from adapter to the switch console port.
2. Verify Python and pyserial Installation

python --version
pip show pyserial


1. Save the Script File
  * Save the code to a file, for example:

configure_switch.py


1. Run from Terminal / Command Prompt
  * On Windows:

python configure_switch.py


  * On macOS / Linux (if python is Python 2, use python3):

python3 configure_switch.py


1. Monitor Script Output
  * You should see something like:

[✓] Using detected port: COM3

[*] Starting FIU Capstone VLAN + Voice configuration...

→ enable
→ configure terminal
...
   ↳ Confirmed [confirm] for: delete flash:vlan.dat
   ↳ Confirmed copy destination filename
...
[✓] Configuration completed successfully.

Network Summary:
 • VLAN 10 - Voice (Fa0/1–16)
 • VLAN 20 - Users (Fa0/17–30)
 • VLAN 30 - Servers (Fa0/31–38)
 • VLAN 40 - Dev/Test (Fa0/39–46)
 • Trunk Port Fa0/47 → UniFi Router
 • Admin Username: admin / Password: 123456789
 • Management IP: 192.168.1.5 / Gateway: 192.168.1.1


1. Optional: Verify Configuration on the Switch
After it finishes, connect with a normal terminal (e.g., PuTTY, Tera Term) and run:

show vlan brief
show ip interface brief
show running-config


---

5. Script CustomizatYou may modify the list of commands within configure_switch() to align with your specific network environment:ment:

* Change hostname

"hostname SW1",


* Change management IP / gateway

"ip default-gateway 192.168.1.1",
"interface vlan1",
"ip address 192.168.1.5 255.255.255.0",


* Change VLAN IDs, names, or port ranges
Edit lines like:

"vlan 20", "name USERS", "exit",
"interface range fa0/17 - 30",
"switchport access vlan 20",


* Change trunk port or allowed VLANs

"interface fa0/47",
"switchport trunk allowed vlan 1,10,20,30,40",


After making modifications, re-run the script to apply the updated configuration to the switch.

---

6. Error Handling Procedures

The main block:

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] {e}")
    input("\nPress Enter to exit...")


* Handles exceptions such as missing serial ports, permission errors, or lack of response from the switch
* Displays an [ERROR] message to inform the user, rather than terminating without notification
* Waits for user input before closing the window, ensuring that error messages are visible



TO view html code you may need to open the code in Visual Studio or simply right click on the html file to view code in text editor


