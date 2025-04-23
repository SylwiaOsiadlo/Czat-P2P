# === p2p_chat/chat/server.py ===
# Serwer nasłuchujący na nowe połączenia TCP (inne peery chcące się połączyć).

import socket
import threading
from .protocol import decode_message

class PeerServer:
    def __init__(self, peer):
        self.peer = peer

    def listen(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.peer.host, self.peer.port))
        s.listen()
        print(f"[SERVER] Listening on {self.peer.host}:{self.peer.port}")

        while True:
            conn, addr = s.accept()
            print(f"[SERVER] New connection from {addr}")
            threading.Thread(target=self.handle_client, args=(conn,), daemon=True).start()

    def handle_client(self, conn):
        with conn:
            while True:
                try:
                    data = conn.recv(1024)
                    if not data:
                        break
                    msg = decode_message(data.decode())
                    print(f"[RECEIVED] {msg}")
                except Exception as e:
                    print(f"[ERROR] {e}")
                    break