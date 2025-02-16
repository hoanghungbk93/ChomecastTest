import socket
import struct

# Cấu hình địa chỉ multicast mDNS
MCAST_GRP = '224.0.0.251'
MCAST_PORT = 5353

# IP cứng của Chromecast (lấy từ TV)
CHROMECAST_IP = "10.5.20.85"

# Danh sách các thiết bị đã xác thực (Hardcode tạm thời)
ALLOWED_DEVICES = ["10.3.0.246"]  # Ví dụ: chỉ cho phép thiết bị này gửi lệnh cast

# Tạo socket UDP để nhận multicast từ VLAN 3
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((MCAST_GRP, MCAST_PORT))

# Tham gia nhóm multicast trên interface mạng
mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

print(f"🎧 Đang lắng nghe multicast mDNS trên {MCAST_GRP}:{MCAST_PORT}...")

# Tạo socket để gửi gói tin forward đến Chromecast
forward_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    data, addr = sock.recvfrom(1024)  # Nhận dữ liệu từ multicast
    client_ip = addr[0]  # IP nguồn gửi gói tin

    print(f"📡 Nhận gói tin từ {client_ip}: {data.hex()}")

    # Kiểm tra nếu IP nguồn đã được xác thực
    if client_ip in ALLOWED_DEVICES:
        print(f"✅ Thiết bị {client_ip} đã xác thực, forwarding đến {CHROMECAST_IP}...")
        
        # Forward gói tin multicast đến Chromecast
        forward_sock.sendto(data, (CHROMECAST_IP, MCAST_PORT))
    else:
        print(f"❌ Thiết bị {client_ip} chưa xác thực, bỏ qua.")


auto eth1.3
iface eth1.3 inet static
    address 10.3.0.2
    netmask 255.255.255.0
    vlan-raw-device eth1

# Cấu hình VLAN eth1.5
auto eth1.5
iface eth1.5 inet static
    address 10.5.0.2
    netmask 255.255.0.0
    vlan-raw-device eth1