from netmiko import ConnectHandler

# Define device details
cisco_switch = {
    "device_type": "cisco_ios",
    "ip": "192.168.1.100",   # Replace with switch management IP
    "username": "admin",     # Replace with your username
    "password": "adminpass", # Replace with your password
    "secret": "StrongPassword123",  # Enable secret
}

# Configuration commands
config_commands = [
    "hostname Switch1",
    "enable secret StrongPassword123",
    "banner motd #Unauthorized access is prohibited!#",
    "interface vlan 1",
    " ip address 192.168.1.2 255.255.255.0",
    " no shutdown",
    "ip default-gateway 192.168.1.1",
    "line console 0",
    " password ciscocon",
    " login",
    " logging synchronous",
    "line vty 0 4",
    " password ciscovty",
    " login",
    " transport input telnet ssh",
    "interface range FastEthernet0/10 - 24",
    " shutdown",
    "end",
    "write memory",
]

def main():
    # Connect to device
    print("Connecting to switch...")
    connection = ConnectHandler(**cisco_switch)
    
    # Enter enable mode
    connection.enable()
    
    # Send configuration commands
    print("Sending configuration...")
    output = connection.send_config_set(config_commands)
    print(output)
    
    # Save configuration
    print("Saving configuration...")
    save_output = connection.save_config()
    print(save_output)
    
    # Disconnect
    connection.disconnect()
    print("Configuration complete and connection closed.")

if __name__ == "__main__":
    main()
