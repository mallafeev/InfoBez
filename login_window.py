from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox
)
from user_manager import UserManager

class LoginWindow(QMainWindow):
    def __init__(self, db_password, main_window):
        # === Инициализация окна входа ===
        super().__init__()
        self.main_window = main_window
        self.db_password = db_password
        self.um = UserManager(password=self.db_password)
        self.setWindowTitle("Вход")
        self.setGeometry(300, 300, 300, 150)

        # Счётчик попыток
        self.attempts = 0
        # Максимальное количество попыток
        self.max_attempts = 3

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

        back_btn = QPushButton("Выйти на главную")
        back_btn.clicked.connect(self.go_back_to_main)
        layout.addWidget(back_btn)

    def login(self):
        # === Обработка попытки входа пользователя ===
        username = self.username_input.text()
        password = self.password_input.text()
        success, msg = self.um.authenticate(username, password)

        if success:
            # Сброс попыток при успешном входе
            self.attempts = 0
            if username == "ADMIN":
                from admin_window import AdminWindow
                self.admin_window = AdminWindow(self.um, self)
                self.admin_window.show()
                self.hide()
            else:
                from user_window import UserWindow
                self.user_window = UserWindow(self.um, username, self)
                self.user_window.show()
                self.hide()
        else:
            # Если пользователь не найден — сбрасываем счётчик
            if "Пользователь не найден" in msg:
                reply = self.show_custom_question("Ошибка", f"{msg}. Повторить ввод?")
                # Проверка подтверждения повторного ввода
                if reply == QMessageBox.Yes:
                    self.username_input.clear()
                    self.password_input.clear()
                else:
                    self.close()
            else:
                # Увеличиваем счётчик при неправильном пароле
                self.attempts += 1
                remaining = self.max_attempts - self.attempts
                # Проверка, есть ли ещё попытки
                if remaining > 0:
                    QMessageBox.critical(self, "Ошибка", f"Неверный пароль, осталось попыток: {remaining}")
                    self.password_input.clear()
                else:
                    QMessageBox.critical(self, "Ошибка", "Превышено количество попыток. Программа завершена.")
                    self.close()
                    import sys
                    sys.exit()

    def go_back_to_main(self):
        # === Возврат на главное окно ===
        self.close()
        self.main_window.show()

    def show_custom_question(self, title, text):
        # === Отображение диалога с русскими кнопками ===
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.Yes)

        # Русские надписи на кнопках
        yes_button = msg_box.button(QMessageBox.Yes)
        if yes_button:
            yes_button.setText("Да")
        no_button = msg_box.button(QMessageBox.No)
        if no_button:
            no_button.setText("Нет")

        return msg_box.exec_()
