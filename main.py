import subprocess
import json
import os
import sys

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def get_wifi_interface_name():
    """Автоматически находит системное имя беспроводного адаптера через PowerShell"""
    try:
        ps_get_name = 'Get-NetAdapter | Where-Object { $_.InterfacePhysicalMediaType -eq "Wireless80211" -or $_.MediaType -eq "Native 802.11" } | Select-Object -ExpandProperty Name'
        cmd = ["powershell", "-NoProfile", "-Command", ps_get_name]
        
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        name = result.stdout.strip()
        
        if name:
            return name.split('\n')[0].strip()
    except Exception:
        pass
    return "Беспроводная сеть" 

def load_or_create_config():
    base_path = get_base_path()
    config_dir = os.path.join(base_path, "config")
    config_path = os.path.join(config_dir, "config.json")

    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
        print(f"new dir: {config_dir}")

    if os.path.exists(config_path):
        print(f"file detected: {config_path}")
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        print("file dont delect, creating default...")
        config_data = {
            "primary_dns": "8.8.8.8",    
            "secondary_dns": "8.8.4.4"  
        }
        with open(config_path, 'w', encoding="utf-8") as f:
            json.dump(config_data, f, indent=4)
        return config_data

def change_dns(interface, primary, secondary):
    print(f"Setting DNS servers on '{interface}' via PowerShell...")
    
    dns_servers = f'"{primary}", "{secondary}"'

    ps_command = f'Set-DnsClientServerAddress -InterfaceAlias "{interface}" -ServerAddresses ({dns_servers})'
    
    cmd = ["powershell", "-NoProfile", "-Command", ps_command]
    
    subprocess.run(cmd, check=True)
    print(f"primary dns {primary}")
    print(f"secondary dns {secondary}")
        
    subprocess.run(["ipconfig", "/flushdns"], check=True)
    print("clean cash")

INTERFACE_NETWORK_CONNECTION = ""

print("pls select network connection Ethernet(lan) or WI-FI\n1 - Ethernet\n2 - WI-FI")
try:
    network_connection = int(input().strip())
except ValueError:
    network_connection = 2

if network_connection == 1:
    INTERFACE_NETWORK_CONNECTION = "Ethernet"
else: 
    INTERFACE_NETWORK_CONNECTION = get_wifi_interface_name()
    print(f"Detected Wi-Fi interface name: '{INTERFACE_NETWORK_CONNECTION}'")

data = load_or_create_config()

try:
    change_dns(INTERFACE_NETWORK_CONNECTION, data["primary_dns"], data["secondary_dns"])
    input("\nDNS successfully changed! Press Enter to restore DHCP and exit...")

except subprocess.CalledProcessError as e:
    print(f"\n[ERROR] Failed to execute network command: {e}")
    input("\nPress Enter to exit...")

finally:
    print("\nautomatic DHCP...")
<<<<<<< HEAD
    ps_reset = f'Set-DnsClientServerAddress -InterfaceAlias "{INTERFACE_NETWORK_CONNECTION}" -ResetServerAddresses'
    cmd_reset = ["powershell", "-NoProfile", "-Command", ps_reset]
    
    try:
        subprocess.run(cmd_reset, check=True)
        subprocess.run(["ipconfig", "/flushdns"], check=True)
        print("goodbye world")
    except subprocess.CalledProcessError:
        print("[WARNING] Could not reset to DHCP automatically.")
=======
    cmd_reset = f'netsh interface ip set dnsservers name="{INTERFACE_NETWORK_CONNECTION}" source=dhcp'
    subprocess.run(cmd_reset, shell=True, check=True)
    subprocess.run("ipconfig /flushdns", shell=True, check=True)
    print("goodbye world")
>>>>>>> ea6e16f11f7954d8e0e8cd69f879a9c9d070b721
