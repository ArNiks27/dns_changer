import subprocess
import json
import os
import sys
def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))
def load_or_create_config():
    base_path = get_base_path()
    config_dir = os.path.join(base_path, "config")
    config_path = os.path.join(config_dir, "config.json")

    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
        print(f"new dir: {config_dir}")

    if os.path.exists(config_path):
        print("file detected, remake this file if you want to change the dns config/config.json")
        f = open("config/config.json")
        return json.load(f)
    else:
        print("file dont delect")
        
        config_data = {
            "primary_dns": "8.8.8.8",    
            "secondary_dns": "8.8.4.4"  
        }
        f = open(config_path, 'w')
        json.dump(config_data, f)
        return config_data
def change_dns(interface, primary, secondary):
    cmd_primary = f'netsh interface ip set dnsservers name="{interface}" static {primary} primary'
    cmd_secondary = f'netsh interface ip add dnsservers name="{interface}" {secondary} index=2'

    subprocess.run(cmd_primary, shell=True, check=True)
    print(f"primary dns {primary}")
        
    subprocess.run(cmd_secondary, shell=True, check=True)
    print(f"secondary dns  {secondary}")
        
    subprocess.run("ipconfig /flushdns", shell=True, check=True)
    print("clean cash")

INTERFACE_NETWORK_CONNECTION = ""
PRIMARY_DNS = ""
SECONDARY_DNS = ""

print("pls select network connection Ethernet(lan) or WI-FI\n1 - Ethernet\n2 - WI-FI")
network_connection = int(input())

if network_connection == 1:
    INTERFACE_NETWORK_CONNECTION = "Ethernet"
else: 
    INTERFACE_NETWORK_CONNECTION = "WI-FI"

data = load_or_create_config()

try:
    change_dns(INTERFACE_NETWORK_CONNECTION, data["primary_dns"], data["secondary_dns"])
    
    input("\npress Enter to display and flush DNS...")

finally:
    print("\nautomatic DHCP...")
    cmd_reset = f'netsh interface ip set dnsservers name="{INTERFACE_NETWORK_CONNECTION}" source=dhcp'
    subprocess.run(cmd_reset, shell=True, check=True)
    subprocess.run("ipconfig /flushdns", shell=True, check=True)
    print("goodbye world")
