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
            self.peer.peers[conn] = addr
            threading.Thread(target=self.handle_client, args=(conn,), daemon=True).start()

    def handle_client(self, conn):
        with conn:
            while True:
                try:
                    data = conn.recv(1024)
                    print(f'data: {data}')
                    if not data:
                        break
                    msg = decode_message(data.decode())
                    print(f"[RECEIVED] {msg}")

                    # Forward wiadomości do innych peerów
                    self.forward_message(data.decode(), exclude=conn)

                except Exception as e:
                    print(f"[ERROR] {e}")
                    break
        if conn in self.peer.peers:
            del self.peer.peers[conn]

    def forward_message(self, raw_message: str, exclude):
        for sock in self.peer.peers:
            if sock != exclude:
                try:
                    sock.sendall(raw_message.encode())
                except:
                    continue