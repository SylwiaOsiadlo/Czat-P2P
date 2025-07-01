import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QLineEdit,
    QPushButton, QMessageBox, QLabel
)
from gui.chat_window import ChatTab
from utils.auth import register_user, authenticate_user
from utils.logger import logger
from storage.chat_db import init_db, set_user_active
from config import settings


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("P2P Chat - Multiuser")
        self.resize(800, 600)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.login_tab = QWidget()
        self.tabs.addTab(self.login_tab, "Logowanie")
        self.init_login_ui()

    def init_login_ui(self):
        layout = QVBoxLayout()
        self.login_tab.setLayout(layout)

        self.info_label = QLabel("Zaloguj się lub zarejestruj nowego użytkownika")
        layout.addWidget(self.info_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nazwa użytkownika")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Hasło")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.login_button = QPushButton("Zaloguj")
        self.login_button.clicked.connect(self.login_user)
        layout.addWidget(self.login_button)

        self.register_button = QPushButton("Zarejestruj")
        self.register_button.clicked.connect(self.register_user)
        layout.addWidget(self.register_button)

    def login_user(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not authenticate_user(username, password):
            QMessageBox.warning(self, "Błąd", "Nieprawidłowe dane logowania")
            return

        port = settings.default_base_port + hash(username) % 1000
        set_user_active(username, port)

        chat_tab = ChatTab(username, port)
        index = self.tabs.addTab(chat_tab, username)
        self.tabs.setCurrentIndex(index)

        logger.info(f"[MAIN] Dodano zakładkę użytkownika {username} (port {port})")

    def register_user(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Błąd", "Wprowadź nazwę użytkownika i hasło")
            return

        if not register_user(username, password):
            QMessageBox.warning(self, "Błąd", "Użytkownik już istnieje")
            return

        QMessageBox.information(self, "Sukces", "Użytkownik zarejestrowany pomyślnie")


if __name__ == '__main__':
    init_db()
    app = QApplication(sys.argv)

    # Apply stylesheet
    try:
        with open("styles/theme.qss", "r") as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        print("Nie udało się załadować stylu:", e)

    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec_())

