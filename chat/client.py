# === p2p_chat/chat/client.py ===
# Klient łączący się z innym peerem (inicjuje połączenie).

import socket

def connect_to_peer(host: str, port: int):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        print(f"[CLIENT] Connected to {host}:{port}")
        return sock
    except Exception as e:
        print(f"[CLIENT] Connection failed: {e}")
        return None