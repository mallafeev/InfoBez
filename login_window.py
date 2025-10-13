from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox
)
from user_manager import UserManager

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вход")
        self.setGeometry(300, 300, 300, 150)

        layout = QVBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        layout.addWidget(QLabel("Имя:"))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel("Пароль:"))
        layout.addWidget(self.password_input)

        btn = QPushButton("Войти")
        btn.clicked.connect(self.login)
        layout.addWidget(btn)

        self.um = UserManager()

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        success, msg = self.um.authenticate(username, password)
        if success:
            if username == "ADMIN":
                from admin_window import AdminWindow
                self.admin_window = AdminWindow(self.um, self)
                self.admin_window.show()
                self.hide()
            else:
                from user_window import UserWindow
                self.user_window = UserWindow(self.um, username)  # Убираем self
                self.user_window.show()
                self.hide()
        else:
            QMessageBox.critical(self, "Ошибка", msg)