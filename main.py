from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget,
    QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, QDialog, QFormLayout
)
from PyQt5.QtCore import QTimer, pyqtSlot, QObject, pyqtSignal
from chat.peer import Peer
import sys
import time


class ChatTab(QWidget):
    def __init__(self):
        super().__init__()
        self.peer = None
        self.nickname = None
        self.room_password = "1"  # domyślne hasło do pokoju
        self.init_login_ui()
        self.tab_index = 0

    def bind_index(self, index):
        self.tab_index = index

    def init_login_ui(self):
        self.layout = QVBoxLayout(self)

        self.login_label = QLabel("Podaj nickname i hasło, aby dołączyć do pokoju:")
        self.layout.addWidget(self.login_label)

        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("Port")
        self.port_input.setText("6000")
        self.layout.addWidget(self.port_input)

        self.nickname_input = QLineEdit()
        self.nickname_input.setPlaceholderText("Nickname")
        self.layout.addWidget(self.nickname_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Hasło")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.password_input)

        self.login_button = QPushButton("Dołącz")
        self.login_button.clicked.connect(self.join_room)
        self.layout.addWidget(self.login_button)

        self.create_button = QPushButton("Utwórz i dołącz")
        self.create_button.clicked.connect(self.create_room)
        self.layout.addWidget(self.create_button)

    def create_room(self):
        nickname = self.nickname_input.text().strip()
        port_text = self.port_input.text().strip()
        password_text = self.password_input.text().strip()
        port_number = 6000

        try:
            port_number = int(port_text)
        except ValueError:
            port_number = None

        peer = start_peer(port_number)
        peer.tab_widget = self
        peer.signals.message_received.connect(window.handle_received_message)
        window.peers.append(peer)

        self.nickname = nickname
        self.peer = peer
        self.room_password = password_text

        window.tabs.setTabText(self.tab_index, nickname)

        self.clear_layout()
        self.init_chat_ui()

    def validate_login(self, nickname, password):
        if password == self.room_password:
            return True

        return False

    def join_room(self):
        nickname = self.nickname_input.text().strip()
        password = self.password_input.text().strip()
        if nickname:
            self.nickname = nickname

            peer = start_peer(6001, 6000, password)
            peer.tab_widget = self
            peer.signals.message_received.connect(window.handle_received_message)
            window.peers.append(peer)
            self.peer = peer

            window.tabs.setTabText(self.tab_index, nickname)

            self.clear_layout()
            self.init_chat_ui()

        else:
            self.login_label.setText("Błędny nickname lub hasło. Spróbuj ponownie:")

    def clear_layout(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def init_chat_ui(self):
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.layout.addWidget(self.chat_display)

        self.message_input = QLineEdit()
        self.layout.addWidget(self.message_input)

        self.send_button = QPushButton("Wyślij")
        self.layout.addWidget(self.send_button)

        self.send_button.clicked.connect(self.send_message)
        self.message_input.returnPressed.connect(self.send_message)

    def send_message(self):
        if not self.nickname:
            return
        message = self.message_input.text().strip()
        if message:
            self.peer.broadcast(f"{self.nickname}: {message}")
            self.display_message(f"You: {message}")
            self.message_input.clear()

    def display_message(self, message):
        if self.nickname:
            self.chat_display.append(message)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.peers = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("P2P Chat - Multi Peer")
        self.setGeometry(100, 100, 800, 600)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

    @pyqtSlot(object)
    def add_peer_tab(self):
        chat_tab = ChatTab()
        index = self.tabs.addTab(chat_tab, f"Peer {self.tabs.count()+1}")
        chat_tab.bind_index(index)

    @pyqtSlot(str, str)
    def handle_received_message(self, sender, message):
        for peer in self.peers:
            if hasattr(peer, 'tab_widget') and peer.tab_widget.nickname:
                peer.tab_widget.display_message(message)


def start_peer(port, connect_to=None, password=None):
    peer = Peer("127.0.0.1", port)
    peer.start()

    time.sleep(0.5)

    if connect_to:
        peer.connect("127.0.0.1", connect_to, password)

    #QTimer.singleShot(0, lambda: window.add_peer_tab(peer))
    return peer


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    window.add_peer_tab()
    window.add_peer_tab()
    window.add_peer_tab()

    sys.exit(app.exec_())