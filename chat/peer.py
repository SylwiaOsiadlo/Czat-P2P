# === p2p_chat/chat/peer.py ===
# Klasa reprezentująca peer-a. Odpowiada za zarządzanie połączeniami.

import socket
import threading
from .server import PeerServer
from .client import connect_to_peer
from .protocol import encode_message

class Peer:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.peers = []

    def start(self):
        server = PeerServer(self)
        threading.Thread(target=server.listen, daemon=True).start()

    def connect(self, peer_host: str, peer_port: int):
        sock = connect_to_peer(peer_host, peer_port)
        if sock:
            self.peers.append(sock)

    def broadcast(self, message: str):
        encoded = encode_message(f"{self.host}:{self.port}", message)
        disconnected = []
        for sock in self.peers:
            try:
                sock.sendall(encoded.encode())
            except:
                disconnected.append(sock)
        for sock in disconnected:
            self.peers.remove(sock)