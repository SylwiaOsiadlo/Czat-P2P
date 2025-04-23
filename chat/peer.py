# === p2p_chat/chat/peer.py ===
# Klasa reprezentująca peer-a. Odpowiada za zarządzanie połączeniami.

import socket
import threading
from .server import PeerServer
from .client import connect_to_peer

class Peer:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.peers = []  # lista aktywnych połączeń (sockety)

    def start(self):
        # Start serwera nasłuchującego na połączenia
        server = PeerServer(self)
        threading.Thread(target=server.listen, daemon=True).start()

    def connect(self, peer_host: str, peer_port: int):
        sock = connect_to_peer(peer_host, peer_port)
        if sock:
            self.peers.append(sock)