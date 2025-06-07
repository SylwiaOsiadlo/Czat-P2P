# === p2p_chat/main.py ===
from chat.peer import Peer
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton
from PyQt5.QtCore import QMetaObject, Qt, Q_ARG, pyqtSlot, QTimer
import threading
import time
import sys

import sys
import time
import threading
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget,
    QVBoxLayout, QTextEdit, QLineEdit, QPushButton
)
from PyQt5.QtCore import QTimer, pyqtSlot

from chat.peer import Peer  # zakładam poprawny import

class ChatTab(QWidget):
    def __init__(self, peer):
        super().__init__()
        self.peer = peer
        self.layout = QVBoxLayout(self)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.layout.addWidget(self.chat_display)

        self.message_input = QLineEdit()
        self.layout.addWidget(self.message_input)

        self.send_button = QPushButton("Wyślij")
        self.layout.addWidget(self.send_button)

        self.send_button.clicked.connect(self.send_message)
        self.message_input.returnPressed.connect(self.send_message)

    def display_message(self, message):
        self.chat_display.append(message)

    def send_message(self):
        message = self.message_input.text()
        if message:
            self.peer.broadcast(message)
            self.display_message(f"You: {message}")
            self.message_input.clear()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("P2P Chat - Multi Peer")
        self.setGeometry(100, 100, 600, 400)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.peers = []

    @pyqtSlot(object)
    def add_peer_tab(self, peer):
        chat_tab = ChatTab(peer)
        peer.set_tab(chat_tab)       # peer knows its tab
        peer.gui = chat_tab              # peer can call display_message
        self.peers.append(peer)
        self.tabs.addTab(chat_tab, f"Peer {peer.port}")
        print(f"[GUI] Dodaję zakładkę dla {peer.port}")

    def display_message(self, sender, message):
        # Find the peer and tab matching sender
        for peer in self.peers:
            if f"{peer.host}:{peer.port}" == sender and hasattr(peer, 'tab_widget'):
                peer.tab_widget.display_message(message)
                break

# app = QApplication(sys.argv)
# window = MainWindow()
# window.show()

def start_peer(port, connect_to=None):
    peer = Peer("127.0.0.1", port)
    peer.start()
    time.sleep(1)
    if connect_to:
        peer.connect("127.0.0.1", connect_to)
    time.sleep(1)
    peer.broadcast(f"Hello from {port}")

    QTimer.singleShot(0, lambda: window.add_peer_tab(peer))

    return peer

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    def launch_peers():
        start_peer(6000)
        start_peer(6001, 6000)
        start_peer(6002, 6001)

    QTimer.singleShot(0, launch_peers)

    sys.exit(app.exec_())
