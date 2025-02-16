import socket
import struct

MULTICAST_IP = "224.0.0.251"
PORT = 5353

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((MULTICAST_IP, PORT))

mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_IP), socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

print("📡 Proxy Server đang chạy, chuyển tiếp mDNS...")

while True:
    data, addr = sock.recvfrom(1024)
    print(f"📩 Nhận gói tin mDNS từ {addr}")

    # Gửi truy vấn này sang VLAN Chromecast
    chromecast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    chromecast_sock.sendto(data, ("10.5.20.85", PORT))  # Địa chỉ IP Chromecast VLAN 200

    # Nhận phản hồi từ Chromecast và gửi lại VLAN khách
    response, _ = chromecast_sock.recvfrom(1024)
    sock.sendto(response, addr)
