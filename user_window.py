from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QPushButton, QMessageBox, QLineEdit, QInputDialog, QHBoxLayout
)

class UserWindow(QMainWindow):
    def __init__(self, um, username, parent_window=None):
        super().__init__()
        self.um = um
        self.username = username
        self.parent_window = parent_window
        self.setWindowTitle(f"Пользователь: {username}")
        self.setGeometry(300, 300, 300, 200)

        layout = QVBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        btn_change = QPushButton("Сменить пароль")
        btn_change.clicked.connect(self.change_password)
        layout.addWidget(btn_change)

        btn_save_and_exit = QPushButton("Сохранить и выйти")
        btn_save_and_exit.clicked.connect(self.save_and_exit)
        layout.addWidget(btn_save_and_exit)

    def change_password(self):
        from PyQt5.QtWidgets import QLineEdit
        old_pwd, ok1 = QInputDialog.getText(self, "Старый пароль", "Введите старый пароль:", echo=QLineEdit.Password)
        if not ok1:
            return
        new_pwd, ok2 = QInputDialog.getText(self, "Новый пароль", "Введите новый пароль:", echo=QLineEdit.Password)
        if not ok2:
            return
        confirm_pwd, ok3 = QInputDialog.getText(self, "Подтверждение", "Повторите новый пароль:", echo=QLineEdit.Password)
        if not ok3:
            return

        success, msg = self.um.change_password(self.username, old_pwd, new_pwd, confirm_pwd)
        QMessageBox.information(self, "Результат", msg)

    def save_and_exit(self):
        pwd, ok = QInputDialog.getText(self, "Шифрование", "Введите пароль для шифрования файла:", echo=QLineEdit.Password)
        if not ok or not pwd:
            return

        from crypto import encrypt_file
        with open(self.um.db_path, 'rb') as f:
            data = f.read()
        encrypted = encrypt_file(data, pwd)
        with open(self.um.enc_file, 'wb') as f:
            f.write(encrypted)

        self.close()
        if self.parent_window:
            self.parent_window.show()