import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu, QAction, QStatusBar, QPushButton, QVBoxLayout, QWidget, QMessageBox
from PyQt5.QtCore import Qt
from login_window import LoginWindow
from password_dialog import PasswordDialog

class MainWindow(QMainWindow):
    def __init__(self, db_password):
        # === Инициализация главного окна приложения ===
        super().__init__()
        self.db_password = db_password
        self.setWindowTitle("Менеджер пользователей")
        self.setGeometry(100, 100, 800, 600)

        self.create_menu()

        self.statusBar().showMessage("Готов")

        central_widget = QWidget()
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Создаём кнопку, не растягивая на всю ширину
        self.login_button = QPushButton("Войти")
        self.login_button.setMaximumWidth(200)
        self.login_button.clicked.connect(self.open_login)
        layout.addWidget(self.login_button)
        layout.setAlignment(Qt.AlignCenter)

        self.setCentralWidget(central_widget)

    def create_menu(self):
        # === Создание меню окна ===
        menubar = self.menuBar()

        # Меню "Файл"
        file_menu = menubar.addMenu('Файл')

        exit_action = QAction('Выход из системы', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Меню "Справка"
        help_menu = menubar.addMenu('Справка')

        about_action = QAction('О программе', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def show_about(self):
        # === Отображение информации о программе ===
        QMessageBox.about(self, "О программе", 
            "Программа разграничения полномочий пользователей\n"
            "на основе парольной аутентификации c использованием встроенных криптопровайдеров.\n\n"
            "Автор: Малафеев Леонид Сергеевич. Студент гр. ПИбд-41.\n"
            "Задание: Вариант 19. Наличие букв и цифр.\n"
            "Шифрование: DES-CFB\n"
            "Хеширование: MD4")

    def open_login(self):
        # === Открытие окна входа ===
        self.login_window = LoginWindow(self.db_password, self)
        self.login_window.show()
        self.hide()

if __name__ == "__main__":
    # === Запуск приложения ===
    app = QApplication(sys.argv)

    # --- Авторизация БД при запуске ---
    if os.path.exists('data/users.db.enc'):
        # Проверка существования зашифрованного файла базы данных
        pwd_dialog = PasswordDialog("Расшифровка", "Введите пароль для расшифровки файла:")
    else:
        # Если файл не существует — создаём новый
        pwd_dialog = PasswordDialog("Шифрование", "Введите пароль для шифрования файла:")

    pwd = pwd_dialog.get_password()
    # Проверка подтверждения ввода пароля
    if not pwd:
        sys.exit()

    main_window = MainWindow(pwd)
    main_window.show()

    def on_exit():
        # === Закрытие соединения с базой данных при выходе ===
        if hasattr(main_window, 'login_window') and main_window.login_window:
            main_window.login_window.um.close()

    app.aboutToQuit.connect(on_exit)

    sys.exit(app.exec_())
