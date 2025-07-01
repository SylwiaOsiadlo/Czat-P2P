import socket
import threading
from .protocol import decode_message

class PeerServer:
    def __init__(self, peer):
        self.peer = peer
        self.message_cache = set()

    def listen(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.peer.host, self.peer.port))
        s.listen()
        print(f"[SERVER] Listening on {self.peer.host}:{self.peer.port}")

        while True:
            conn, addr = s.accept()
            peer_addr = f"{addr[0]}:{addr[1]}"
            self.peer.peers[conn] = peer_addr
            threading.Thread(target=self.handle_client, args=(conn,), daemon=True).start()

    def handle_client(self, conn):
        with conn:
            while True:
                try:
                    data = conn.recv(1024)
                    if not data:
                        break

                    msg_str = data.decode()
                    msg = decode_message(msg_str)

                    if msg['content'] not in self.message_cache:
                        self.message_cache.add(msg['content'])

                        if hasattr(self.peer, 'gui_handler'):
                            self.peer.gui_handler.message_received.emit(msg['sender'], msg['content'])

                        self.forward_message(msg_str, exclude=conn)

                except Exception:
                    break

        self._cleanup_connection(conn)

    def forward_message(self, raw_message: str, exclude):
        msg = decode_message(raw_message)
        for sock in list(self.peer.peers.keys()):
            if sock != exclude and self.peer.peers[sock] != msg['sender']:
                try:
                    sock.sendall(raw_message.encode())
                except:
                    self._cleanup_connection(sock)

    def _cleanup_connection(self, conn):
        if conn in self.peer.peers:
            del self.peer.peers[conn]
            conn.close()