from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QPushButton, QMessageBox, QLineEdit, QInputDialog, QHBoxLayout, QMenuBar, QMenu, QAction, QStatusBar
)

class UserWindow(QMainWindow):
    def __init__(self, um, username, parent_window=None):
        # === Инициализация окна пользователя ===
        super().__init__()
        # Храним UserManager
        self.um = um
        # Храним имя пользователя
        self.username = username
        # Храним ссылку на родительское окно
        self.parent_window = parent_window
        # Устанавливаем заголовок окна
        self.setWindowTitle(f"Пользователь: {username}")
        # Устанавливаем размеры окна
        self.setGeometry(300, 300, 300, 200)

        # Создаём меню
        self.create_menu()

        # Создаём строку состояния
        self.statusBar().showMessage(f"Пользователь: {username}")

        layout = QVBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        btn_change = QPushButton("Сменить пароль")
        btn_change.clicked.connect(self.change_password)
        layout.addWidget(btn_change)

        btn_exit_main = QPushButton("Выйти на страницу входа")
        btn_exit_main.clicked.connect(self.exit_to_main)
        layout.addWidget(btn_exit_main)

    def create_menu(self):
        # === Создание меню окна ===
        menubar = self.menuBar()

        # Меню "Файл"
        file_menu = menubar.addMenu('Файл')

        exit_action = QAction('Выход из системы', self)
        exit_action.triggered.connect(self.exit_app)
        file_menu.addAction(exit_action)

        # Меню "Справка"
        help_menu = menubar.addMenu('Справка')

        about_action = QAction('О программе', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def show_about(self):
        # === Отображение информации о программе ===
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.about(self, "О программе", 
            "Программа разграничения полномочий пользователей\n"
            "на основе парольной аутентификации c использованием встроенных криптопровайдеров.\n\n"
            "Автор: Малафеев Леонид Сергеевич. Студент гр. ПИбд-41.\n"
            "Задание: Вариант 19. Наличие букв и цифр.\n"
            "Шифрование: DES-CFB\n"
            "Хеширование: MD4")

    def change_password(self):
        # === Смена пароля пользователя с проверками ===
        from PyQt5.QtWidgets import QLineEdit
        old_pwd, ok1 = self.get_text_input("Старый пароль", "Введите старый пароль:", QLineEdit.Password)
        # Проверка подтверждения ввода старого пароля
        if not ok1:
            return
        new_pwd, ok2 = self.get_text_input("Новый пароль", "Введите новый пароль:", QLineEdit.Password)
        # Проверка подтверждения ввода нового пароля
        if not ok2:
            return
        confirm_pwd, ok3 = self.get_text_input("Подтверждение", "Повторите новый пароль:", QLineEdit.Password)
        # Проверка подтверждения ввода подтверждения
        if not ok3:
            return

        success, msg = self.um.change_password(self.username, old_pwd, new_pwd, confirm_pwd)
        # Проверка, успешна ли смена пароля
        if not success:
            # Если ошибка — предоставляем выбор
            reply = QMessageBox.question(self, "Ошибка", 
                                         f"{msg}\n"
                                         "Повторить ввод?", 
                                         QMessageBox.Yes | QMessageBox.No)
            # Русские кнопки
            yes_button = reply.button(QMessageBox.Yes)
            if yes_button:
                yes_button.setText("Да")
            no_button = reply.button(QMessageBox.No)
            if no_button:
                no_button.setText("Нет")

            # Проверка подтверждения повторного ввода
            if reply == QMessageBox.Yes:
                # Повторить смену пароля
                self.change_password()
            return
        else:
            QMessageBox.information(self, "Результат", msg)

    def exit_to_main(self):
        # === Шифрование базы данных и возврат на главное окно ===
        pwd, ok = self.get_text_input("Шифрование", "Введите пароль для шифрования файла:", QLineEdit.Password)
        # Проверка подтверждения ввода пароля
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

    def exit_app(self):
        # === Завершение работы приложения с шифрованием базы данных ===
        pwd, ok = self.get_text_input("Шифрование", "Введите пароль для шифрования файла:", QLineEdit.Password)
        # Проверка подтверждения ввода пароля
        if not ok or not pwd:
            return
        from crypto import encrypt_file
        with open(self.um.db_path, 'rb') as f:
            data = f.read()
        encrypted = encrypt_file(data, pwd)
        with open(self.um.enc_file, 'wb') as f:
            f.write(encrypted)
        self.um.close()
        self.close()

    def get_text_input(self, title, label, echo_mode):
        # === Получение текстового ввода с русскими кнопками ===
        dialog = QInputDialog(self)
        dialog.setWindowTitle(title)
        dialog.setLabelText(label)
        dialog.setTextEchoMode(echo_mode)

        # Русские кнопки
        ok_button = dialog.findChild(QPushButton)
        if ok_button:
            ok_button.setText("ОК")
        cancel_button = dialog.findChild(QPushButton, "cancel")
        if cancel_button:
            cancel_button.setText("Отмена")

        if dialog.exec_() == QInputDialog.Accepted:
            return dialog.textValue(), True
        else:
            return "", False