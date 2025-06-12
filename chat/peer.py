import socket
import threading
import json
import time
from PyQt5.QtCore import QTimer, pyqtSignal, QObject


class PeerSignals(QObject):
    message_received = pyqtSignal(str, str)  # sender, message


class Peer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.peers = {}
        self.running = True
        self.signals = PeerSignals()
        self.message_history = set()

    def start(self):
        # Start server thread
        server_thread = threading.Thread(target=self._run_server, daemon=True)
        server_thread.start()

        # Start receiver thread
        receiver_thread = threading.Thread(target=self._receive_loop, daemon=True)
        receiver_thread.start()

    def _run_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen()
            print(f"[{self.port}] Server started")

            while self.running:
                conn, addr = s.accept()
                peer_addr = f"{addr[0]}:{addr[1]}"
                self.peers[conn] = peer_addr
                print(f"[{self.port}] New connection from {peer_addr}")

    def connect(self, peer_host, peer_port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((peer_host, peer_port))
            peer_addr = f"{peer_host}:{peer_port}"
            self.peers[sock] = peer_addr
            return True
        except:
            return False

    def broadcast(self, message):
        message_id = f"{time.time()}-{self.port}"
        self.message_history.add(message_id)

        msg = self._create_message(message, message_id)
        for sock in list(self.peers.keys()):
            try:
                sock.sendall(msg.encode())
            except:
                self._remove_peer(sock)

    def _receive_loop(self):
        while self.running:
            for sock in list(self.peers.keys()):
                try:
                    data = sock.recv(1024)
                    if data:
                        self._process_message(data.decode())
                except:
                    self._remove_peer(sock)
            time.sleep(0.1)

    def _process_message(self, raw_msg):
        try:
            msg = json.loads(raw_msg)
            message_id = msg['message_id']

            # Ignore if message already processed or from self
            if (message_id in self.message_history or
                    msg['sender'] == f"{self.host}:{self.port}"):
                return

            self.message_history.add(message_id)
            self.signals.message_received.emit(msg['sender'], msg['content'])

            # Forward to other peers (flooding prevention)
            for sock in list(self.peers.keys()):
                try:
                    sock.sendall(raw_msg.encode())
                except:
                    self._remove_peer(sock)

        except json.JSONDecodeError:
            pass

    def _create_message(self, content, message_id):
        return json.dumps({
            'sender': f"{self.host}:{self.port}",
            'content': content,
            'message_id': message_id
        })

    def _remove_peer(self, sock):
        if sock in self.peers:
            sock.close()
            del self.peers[sock]