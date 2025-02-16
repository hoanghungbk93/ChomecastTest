from flask import Flask, request, jsonify, send_file
import socket
import json
import os
import subprocess
from datetime import datetime

app = Flask(__name__)

# Paths to the JSON files
VERIFIED_IPS_FILE = '/opt/verified_ips.json'
CHROMECAST_FILE = '/opt/chromecast.json'

# Load existing verified IPs from the file
def load_verified_ips():
    if os.path.exists(VERIFIED_IPS_FILE):
        with open(VERIFIED_IPS_FILE, 'r') as file:
            return json.load(file)
    return {}

# Save verified IPs to the file
def save_verified_ips(ips):
    with open(VERIFIED_IPS_FILE, 'w') as file:
        json.dump(ips, file, indent=4)

# Load Chromecast codes and IPs
def load_chromecast_codes():
    if os.path.exists(CHROMECAST_FILE):
        with open(CHROMECAST_FILE, 'r') as file:
            return json.load(file)
    return {}

# Initialize verified IPs and Chromecast codes
verified_ips = load_verified_ips()
chromecast_codes = load_chromecast_codes()

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def get_mac_address(ip):
    try:
        # Run the arp command to get the MAC address
        result = subprocess.run(['arp', '-n', ip], capture_output=True, text=True)
        # Parse the output to find the MAC address
        for line in result.stdout.splitlines():
            if ip in line:
                return line.split()[2]  # MAC address is usually the third element
    except Exception as e:
        print(f"Error retrieving MAC address for {ip}: {e}")
    return "00:00:00:00:00:00"

@app.route('/')
def index():
    return send_file('sender.html')

@app.route('/verify_code', methods=['POST'])
def verify_code():
    data = request.json
    code = data.get('code')
    device_ip = request.remote_addr  # Get the client's IP address
    
    if not code:
        return jsonify({'success': False, 'message': 'No code provided'})
    
    # Check if the code exists in the Chromecast codes
    if code in chromecast_codes:
        chromecast_ip = chromecast_codes[code]
        print(f"Handshake successful - Device IP: {device_ip}, Code: {code}, Chromecast IP: {chromecast_ip}")
        
        # Ensure the chromecast_ip entry exists in verified_ips
        if chromecast_ip not in verified_ips:
            verified_ips[chromecast_ip] = []
        
        # Check if the device is already verified
        if not any(device['ip'] == device_ip for device in verified_ips[chromecast_ip]):
            mac_address = get_mac_address(device_ip)
            verified_ips[chromecast_ip].append({
                "ip": device_ip,
                "pair_time": datetime.now().isoformat(),
                "mac_address": mac_address
            })
            save_verified_ips(verified_ips)
        
        return jsonify({
            'success': True,
            'message': 'Connected successfully'
        })
    else:
        print(f"Invalid code received from IP: {device_ip}")
        return jsonify({
            'success': False,
            'message': 'Invalid code'
        })

@app.route('/disconnect', methods=['POST'])
def disconnect():
    device_ip = request.remote_addr  # Get the client's IP address
    for chromecast_ip, devices in verified_ips.items():
        for device in devices:
            if device['ip'] == device_ip:
                devices.remove(device)
                save_verified_ips(verified_ips)
                print(f"Device disconnected: {device_ip}")
                return jsonify({
                    'success': True,
                    'message': 'Disconnected successfully'
                })
    return jsonify({
        'success': False,
        'message': 'Device not found'
    })

def main():
    local_ip = get_local_ip()
    print(f"\nHandshake server running at:")
    print(f"http://{local_ip}:8000")
    print("\nTest code: 1234")
    
    app.run(host='0.0.0.0', port=8000)

if __name__ == "__main__":
    main() 