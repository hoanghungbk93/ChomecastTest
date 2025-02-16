from flask import Flask, request, jsonify, send_file
import socket
import json
import os
from datetime import datetime

app = Flask(__name__)

# Path to the JSON file
VERIFIED_IPS_FILE = '/opt/verified_ips.json'

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

# Initialize verified IPs
verified_ips = load_verified_ips()

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

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
    
    if code == "1234":
        print(f"Handshake successful - Device IP: {device_ip}, Code: {code}")
        if device_ip not in verified_ips:
            verified_ips[device_ip] = {"pair_time": datetime.now().isoformat()}
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
    if device_ip in verified_ips:
        del verified_ips[device_ip]
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