from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget,
    QVBoxLayout, QTextEdit, QLineEdit, QPushButton
)
from PyQt5.QtCore import QTimer, pyqtSlot, QObject, pyqtSignal
from chat.peer import Peer
import sys
import time


class ChatTab(QWidget):
    def __init__(self, peer):
        super().__init__()
        self.peer = peer
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)

        # Pole wyświetlające wiadomości
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.layout.addWidget(self.chat_display)

        # Pole wprowadzania wiadomości
        self.message_input = QLineEdit()
        self.layout.addWidget(self.message_input)

        # Przycisk wysyłania
        self.send_button = QPushButton("Wyślij")
        self.layout.addWidget(self.send_button)

        # Połączenia sygnałów
        self.send_button.clicked.connect(self.send_message)
        self.message_input.returnPressed.connect(self.send_message)

    def send_message(self):
        message = self.message_input.text().strip()
        if message:
            self.peer.broadcast(message)
            self.display_message(f"You: {message}")
            self.message_input.clear()

    def display_message(self, message):
        self.chat_display.append(message)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.peers = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("P2P Chat - Multi Peer")
        self.setGeometry(100, 100, 800, 600)

        # Główny widget z zakładkami
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

    @pyqtSlot(object)
    def add_peer_tab(self, peer):
        # Tworzenie nowej zakładki dla peera
        chat_tab = ChatTab(peer)
        peer.tab_widget = chat_tab

        # Połączenie sygnału od peera z metodą głównego okna
        peer.signals.message_received.connect(self.handle_received_message)

        self.peers.append(peer)
        self.tabs.addTab(chat_tab, f"Peer {peer.port}")

    @pyqtSlot(str, str)
    def handle_received_message(self, sender, message):
        # Wyświetl wiadomość we wszystkich zakładkach OPRÓCZ nadawcy
        for peer in self.peers:
            if hasattr(peer, 'tab_widget'):
                peer.tab_widget.display_message(f"{sender}: {message}")


def start_peer(port, connect_to=None):
    peer = Peer("127.0.0.1", port)
    peer.start()

    # Małe opóźnienie dla stabilności
    time.sleep(0.5)

    if connect_to:
        peer.connect("127.0.0.1", connect_to)

    # Dodanie peera do GUI
    QTimer.singleShot(0, lambda: window.add_peer_tab(peer))
    return peer


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    # Uruchomienie peerów z opóźnieniem dla stabilności połączeń
    QTimer.singleShot(100, lambda: start_peer(6000))
    QTimer.singleShot(200, lambda: start_peer(6001, 6000))
    QTimer.singleShot(300, lambda: start_peer(6002, 6001))

    sys.exit(app.exec_())