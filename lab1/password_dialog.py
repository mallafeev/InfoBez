from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QApplication
from PyQt5.QtCore import Qt

class PasswordDialog(QDialog):
    def __init__(self, title="Введите пароль", message="Пароль:"):
        # === Инициализация диалога ввода пароля ===
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

        btn_layout = QVBoxLayout()

        self.ok_button = QPushButton("ОК")
        self.ok_button.clicked.connect(self.accept)
        btn_layout.addWidget(self.ok_button)

        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_button)

        layout.addLayout(btn_layout)

        self.password = None

    def get_password(self):
        # === Получение введённого пароля из диалога ===
        result = self.exec_()
        # Проверка подтверждения ввода
        if result == QDialog.Accepted:
            self.password = self.password_input.text()
        return self.password
