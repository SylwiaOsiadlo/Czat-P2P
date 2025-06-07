import os
import PyQt5
from PyQt5.QtCore import QTimer

# Konfiguracja ścieżki do pluginów Qt
plugin_path = os.path.join(os.path.dirname(PyQt5.__file__), "Qt", "plugins")
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = plugin_path

import threading
from .server import PeerServer
from .client import connect_to_peer
from .protocol import encode_message, decode_message

class Peer:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.peers = {}  # sock -> peer_address
        self.running = True
        self.gui = None
        self.tab_widget = None

    def start(self):
        # Start server listener
        server = PeerServer(self)
        threading.Thread(target=server.listen, daemon=True).start()

        # Start receive loop
        threading.Thread(target=self._receive_loop, daemon=True).start()

    def connect(self, peer_host: str, peer_port: int):
        sock = connect_to_peer(peer_host, peer_port)
        if sock:
            peer_addr = f"{peer_host}:{peer_port}"
            self.peers[sock] = peer_addr

            if self.gui:
                QTimer.singleShot(0, lambda: self.gui.add_peer_tab(peer_addr))

    def broadcast(self, message: str):
        encoded = encode_message(f"{self.host}:{self.port}", message)
        disconnected = []

        for sock, peer_addr in list(self.peers.items()):
            try:
                sock.sendall(encoded.encode())
                print(f'sendall {encoded}')
            except Exception:
                disconnected.append(sock)

        for sock in disconnected:
            peer_addr = self.peers.pop(sock, None)
            sock.close()

    def set_tab(self, tab_widget):
        self.tab_widget = tab_widget

    def _receive_loop(self):
        while self.running:
            for sock in list(self.peers.keys()):
                try:
                    data = sock.recv(1024)
                    if not data:
                        del self.peers[sock]
                        sock.close()
                        continue

                    message = decode_message(data.decode())
                    sender = message["sender"]
                    content = message["content"]

                    if self.gui:
                        QTimer.singleShot(0, lambda s=sender, c=content: self.gui.display_message(f"{s}: {c}"))

                except Exception as e:
                    print(f"[Receive error] {e}")
                    if sock in self.peers:
                        del self.peers[sock]
                    sock.close()

    def _disconnect_peer(self, sock):
        if sock in self.peers:
            print(f"[Peer disconnected] {self.peers[sock]}")
            self.peers.pop(sock, None)
            sock.close()
