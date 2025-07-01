from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton,
    QLabel, QMessageBox, QHBoxLayout, QTextEdit, QListWidget
)
from PyQt5.QtCore import QTimer, pyqtSignal
from network.peer import Peer
from utils.logger import logger
from storage.chat_db import save_message, get_active_users, get_history
from config import settings


class ChatTab(QWidget):
    connection_requested = pyqtSignal(str)

    def __init__(self, username, local_port):
        super().__init__()
        self.username = username
        self.local_port = local_port

        self.peer = Peer(settings.default_host, self.local_port)
        self.peer.bind_chat_window(self)
        self.peer.start()

        self.init_ui()
        self.load_local_history()
        self.refresh_active_users()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        self.message_input = QLineEdit()
        layout.addWidget(self.message_input)

        self.send_button = QPushButton("Wyślij")
        self.send_button.clicked.connect(self.send_message)
        layout.addWidget(self.send_button)

        self.user_list = QListWidget()
        layout.addWidget(self.user_list)

        self.connect_user_button = QPushButton("Połącz z użytkownikiem")
        self.connect_user_button.clicked.connect(self.connect_to_selected_user)
        layout.addWidget(self.connect_user_button)

        ip_port_layout = QHBoxLayout()
        self.remote_ip_input = QLineEdit()
        self.remote_ip_input.setPlaceholderText("IP peera")
        ip_port_layout.addWidget(self.remote_ip_input)

        self.remote_port_input = QLineEdit()
        self.remote_port_input.setPlaceholderText("Port peera")
        ip_port_layout.addWidget(self.remote_port_input)

        self.connect_button = QPushButton("Połącz")
        self.connect_button.clicked.connect(self.connect_to_peer)
        ip_port_layout.addWidget(self.connect_button)

        layout.addLayout(ip_port_layout)

    def load_local_history(self):
        messages = get_history(limit=100)
        for sender, content, timestamp in messages:
            self.chat_display.append(f"{sender}: {content}")

    def send_message(self):
        content = self.message_input.text().strip()
        if content:
            formatted = f"{self.username}: {content}"
            self.chat_display.append(f"Ty: {content}")
            self.peer.broadcast(formatted)
            save_message(self.username, content)
            self.message_input.clear()

    def connect_to_peer(self):
        ip = self.remote_ip_input.text().strip()
        port_text = self.remote_port_input.text().strip()

        if not ip or not port_text:
            self.show_error("Podaj IP i port.")
            return

        try:
            port = int(port_text)
            self.peer.connect(ip, port)
            self.chat_display.append(f"[System] Połączono z {ip}:{port}")
        except ValueError:
            self.show_error("Nieprawidłowy port.")

    def connect_to_selected_user(self):
        selected = self.user_list.currentItem()
        if selected:
            username_port = selected.text()
            parts = username_port.split(":")
            if len(parts) == 2:
                ip = settings.default_host
                try:
                    port = int(parts[1])
                    self.peer.connect(ip, port)
                    self.chat_display.append(f"[System] Wysłano żądanie połączenia do {username_port}")
                except ValueError:
                    self.show_error("Błędny format portu")

    def refresh_active_users(self):
        self.user_list.clear()
        users = get_active_users()
        for user, port in users:
            if user != self.username:
                self.user_list.addItem(f"{user}:{port}")
        QTimer.singleShot(5000, self.refresh_active_users)

    def display_message(self, message):
        self.chat_display.append(message)

    def ask_connection_approval(self, requester):
        if self.isVisible():
            result = QMessageBox.question(
                self,
                "Prośba o połączenie",
                f"Użytkownik {requester} chce się połączyć. Zaakceptować?",
                QMessageBox.Yes | QMessageBox.No
            )
            return result == QMessageBox.Yes
        return False

    def show_error(self, message):
        QMessageBox.critical(self, "Błąd", message)
