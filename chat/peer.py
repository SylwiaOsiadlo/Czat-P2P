import socket
import threading
import json
import time
from PyQt5.QtCore import QTimer, pyqtSignal, QObject


class PeerSignals(QObject):
    message_received = pyqtSignal(str, str)  # sender, message


class Peer:
    def __init__(self, host, port):
        self.tab_widget = None
        self.host = host
        self.port = port
        self.peers = {}  # Format: {socket: peer_addr}
        self.running = True
        self.signals = PeerSignals()
        self.message_history = set()  # Stores message IDs to prevent duplicates
        self.lock = threading.Lock()  # For thread-safe operations

    def start(self):
        server_thread = threading.Thread(target=self._run_server, daemon=True)
        server_thread.start()

        receiver_thread = threading.Thread(target=self._receive_loop, daemon=True)
        receiver_thread.start()

    def _run_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen()
            print(f"[{self.port}] Server started")

            while self.running:
                try:
                    conn, addr = s.accept()
                    peer_addr = f"{addr[0]}:{addr[1]}"
                    with self.lock:
                        self.peers[conn] = peer_addr
                    print(f"[{self.port}] New connection from {peer_addr}")
                except:
                    if self.running:
                        print(f"[{self.port}] Error accepting connection")

    def connect(self, peer_host, peer_port, nickname, peer_pass):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)  # Set timeout for connection
            sock.connect((peer_host, peer_port))
            peer_addr = f"{peer_host}:{peer_port}"
            with self.lock:
                self.peers[sock] = peer_addr
            sock.settimeout(None)  # Reset timeout after connection

            msg = self._create_hello_message(nickname, peer_pass)

            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def broadcast(self, message):
        message_id = f"{time.time()}-{self.port}"
        self.message_history.add(message_id)
        msg = self._create_message(message, message_id)

        with self.lock:
            peers_to_remove = []
            for sock in self.peers.keys():
                try:
                    sock.sendall(msg.encode())
                except:
                    peers_to_remove.append(sock)

            for sock in peers_to_remove:
                self._remove_peer(sock)

    def _receive_loop(self):
        while self.running:
            with self.lock:
                sockets = list(self.peers.keys())

            for sock in sockets:
                try:
                    sock.settimeout(0.5)  # Non-blocking with timeout
                    data = sock.recv(1024)
                    if data:
                        msg = json.loads(data.decode())
                        message_type = msg['message_type']

                        if message_type == 'hello':
                            nickname = msg['nickname']
                            password = msg['password']

                            con_valid = self.tab_widget.validate_login(nickname, password)

                            if not con_valid:
                                self._remove_peer(sock)

                        self._process_message(data.decode())
                except socket.timeout:
                    continue
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

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Message processing error: {e}")

    def _create_message(self, content, message_id):
        return json.dumps({
            'sender': f"{self.host}:{self.port}",
            'content': content,
            'message_id': message_id
        })

    def _create_hello_message(self, nickname, password):
        return json.dumps({
            'mesage_type': 'hello',
            'nickname': nickname,
            'password': password
        })

    def _remove_peer(self, sock):
        with self.lock:
            if sock in self.peers:
                try:
                    sock.close()
                except:
                    pass
                del self.peers[sock]

    def stop(self):
        self.running = False
        with self.lock:
            for sock in list(self.peers.keys()):
                self._remove_peer(sock)