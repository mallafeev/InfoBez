from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QApplication
from PyQt5.QtCore import Qt

class PasswordDialog(QDialog):
    def __init__(self, title="Введите пароль", message="Пароль:"):
        super().__init__()
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(300, 100)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.label = QLabel(message)
        layout.addWidget(self.label)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.button = QPushButton("ОК")
        self.button.clicked.connect(self.accept)
        layout.addWidget(self.button)

        self.password = None

    def get_password(self):
        if self.exec_() == QDialog.Accepted:
            self.password = self.password_input.text()
        return self.password