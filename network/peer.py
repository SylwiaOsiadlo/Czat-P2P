import socket
import threading
import json
import uuid
from config import settings
from utils.logger import logger
from storage.chat_db import save_message, get_history

class Peer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.peers = []
        self.chat_window = None
        self.received_messages = set()
        self.connected_endpoints = set()

    def bind_chat_window(self, chat_window):
        self.chat_window = chat_window

    def start(self):
        threading.Thread(target=self._server_loop, daemon=True).start()

    def _server_loop(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        logger.info(f"[PEER] Nasłuchiwanie na {self.host}:{self.port}")

        while True:
            conn, addr = self.server_socket.accept()
            logger.info(f"[PEER] Połączono z {addr}")
            self.peers.append(conn)
            threading.Thread(target=self._receive_loop, args=(conn,), daemon=True).start()

    def connect(self, remote_ip, remote_port):
        endpoint = f"{remote_ip}:{remote_port}"
        if endpoint in self.connected_endpoints:
            logger.info(f"[PEER] Już połączony z {endpoint}")
            return

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((remote_ip, remote_port))
            self.peers.append(s)
            self.connected_endpoints.add(endpoint)
            threading.Thread(target=self._receive_loop, args=(s,), daemon=True).start()
            logger.info(f"[PEER] Połączono z {endpoint}")
        except Exception as e:
            logger.warning(f"[PEER] Błąd połączenia z {endpoint}: {e}")

    def send_connection_request(self, remote_ip, remote_port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((remote_ip, remote_port))
            request = json.dumps({
                "message_type": "connection_request",
                "from": f"{self.host}:{self.port}"
            })
            s.sendall(request.encode())
            s.close()
        except Exception as e:
            logger.warning(f"[PEER] Nie udało się wysłać żądania połączenia: {e}")

    def broadcast(self, content):
        message_id = str(uuid.uuid4())
        message = json.dumps({
            "message_type": "message",
            "sender": f"{self.host}:{self.port}",
            "content": content,
            "message_id": message_id
        })

        self.received_messages.add(message_id)
        save_message(self.chat_window.username, content)

        for peer in self.peers:
            try:
                peer.sendall(message.encode())
            except:
                logger.warning("[PEER] Błąd podczas rozsyłania wiadomości")

    def _receive_loop(self, conn):
        while True:
            try:
                data = conn.recv(4096)
                if not data:
                    break

                try:
                    payload = json.loads(data.decode())
                except json.JSONDecodeError:
                    continue

                msg_type = payload.get("message_type")

                if msg_type == "message":
                    msg_id = payload.get("message_id")
                    if msg_id in self.received_messages:
                        continue
                    self.received_messages.add(msg_id)

                    content = payload.get("content")
                    sender = payload.get("sender")

                    if self.chat_window:
                        self.chat_window.display_message(content)

                    save_message(sender, content)

                    for peer in self.peers:
                        if peer != conn:
                            try:
                                peer.sendall(data)
                            except:
                                pass

                elif msg_type == "history_request":
                    logger.info("[PEER] Otrzymano żądanie historii")
                    history = get_history(50)
                    history_payload = json.dumps({
                        "message_type": "history_sync",
                        "messages": history
                    })
                    try:
                        conn.sendall(history_payload.encode())
                    except:
                        logger.warning("[PEER] Nie udało się wysłać historii")

                elif msg_type == "history_sync":
                    messages = payload.get("messages", [])
                    if self.chat_window:
                        for sender, content, timestamp in messages:
                            self.chat_window.display_message(f"{sender}: {content}")

                elif msg_type == "connection_request":
                    requester = payload.get("from")
                    if self.chat_window:
                        accept = self.chat_window.ask_connection_approval(requester)
                        if accept:
                            ip, port = requester.split(":")
                            self.connect(ip, int(port))
                            logger.info(f"[PEER] Zaakceptowano połączenie od {requester}")

            except:
                break