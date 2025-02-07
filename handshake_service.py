from flask import Flask, request, jsonify, send_file
import socket
import time

app = Flask(__name__)

# Lưu trữ các phiên kết nối
connected_devices = {}  # device_id -> connection_time

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
    device_id = request.headers.get('X-Device-ID')
    
    if not code or not device_id:
        return jsonify({'success': False, 'message': 'Missing code or device ID'})
    
    # Hard code mã 1234 để test
    if code == "1234":
        print(f"Handshake successful - Device: {device_id}, Code: {code}")
        connected_devices[device_id] = time.time()
        return jsonify({
            'success': True,
            'message': 'Connected successfully'
        })
    else:
        print(f"Invalid code received from device: {device_id}")
        return jsonify({
            'success': False,
            'message': 'Invalid code'
        })

@app.route('/disconnect', methods=['POST'])
def disconnect():
    device_id = request.headers.get('X-Device-ID')
    if device_id and device_id in connected_devices:
        del connected_devices[device_id]
        print(f"Device disconnected: {device_id}")
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