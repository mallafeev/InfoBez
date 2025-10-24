from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QPushButton, QListWidget, QMessageBox, QHBoxLayout, QInputDialog, QLineEdit, QMenuBar, QMenu, QAction, QStatusBar
)

class AdminWindow(QMainWindow):
    def __init__(self, um, parent_window):
        # === Инициализация окна администратора ===
        super().__init__()
        self.um = um
        self.parent_window = parent_window
        self.setWindowTitle("Панель администратора")
        self.setGeometry(300, 300, 900, 500)

        self.create_menu()

        self.statusBar().showMessage("Режим администратора")
        # Создаём элементы окна
        layout = QVBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.user_list = QListWidget()
        self.refresh_user_list()
        layout.addWidget(self.user_list)

        btn_layout = QHBoxLayout()

        btn_add = QPushButton("Добавить пользователя")
        btn_add.clicked.connect(self.add_user)
        btn_layout.addWidget(btn_add)

        btn_toggle_lock = QPushButton("Переключить блокировку")
        btn_toggle_lock.clicked.connect(self.toggle_lock)
        btn_layout.addWidget(btn_toggle_lock)

        btn_toggle_policy = QPushButton("Переключить ограничения")
        btn_toggle_policy.clicked.connect(self.toggle_policy)
        btn_layout.addWidget(btn_toggle_policy)

        btn_edit_min_length = QPushButton("Изменить мин. длину")
        btn_edit_min_length.clicked.connect(self.edit_min_length)
        btn_layout.addWidget(btn_edit_min_length)

        btn_edit_valid_months = QPushButton("Изменить срок действия (мес.)")
        btn_edit_valid_months.clicked.connect(self.edit_valid_months)
        btn_layout.addWidget(btn_edit_valid_months)

        btn_change_admin_password = QPushButton("Сменить пароль администратора")
        btn_change_admin_password.clicked.connect(self.change_admin_password)
        btn_layout.addWidget(btn_change_admin_password)

        btn_delete_user = QPushButton("Удалить пользователя")
        btn_delete_user.clicked.connect(self.delete_user)
        btn_layout.addWidget(btn_delete_user)

        layout.addLayout(btn_layout)

        btn_exit_main = QPushButton("Выйти на страницу входа")
        btn_exit_main.clicked.connect(self.exit_to_main)
        layout.addWidget(btn_exit_main)

    def create_menu(self):
        # === Создание меню окна ===
        menubar = self.menuBar()

        # Меню "Файл"
        file_menu = menubar.addMenu('Файл')

        # Добавление действия "Выход из системы"
        exit_action = QAction('Выход из системы', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Меню "Справка"
        help_menu = menubar.addMenu('Справка')

        # Добавление действия "О программе"
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

    def refresh_user_list(self):
        # === Обновление списка пользователей в интерфейсе ===
        self.user_list.clear()
        users = self.um.get_all_users()
        for user in users:
            username = user[0]
            pwd_hash = user[1]
            locked = bool(user[2])
            policy = bool(user[3])
            min_length = user[4]
            valid_months = user[5]

            status = "Да" if locked else "Нет"
            policy_status = "Да" if policy else "Нет"
            valid_text = f"{valid_months} месяцев" if valid_months > 0 else "бессрочно"

            item_text = (
                f"Пользователь: {username} | Заблокирован: {status} | "
                f"Ограничения: {policy_status} | Мин. длина: {min_length} | "
                f"Срок действия: {valid_text}"
            )
            self.user_list.addItem(item_text)

    def add_user(self):
        # === Добавление нового пользователя в базу данных ===
        name, ok = QInputDialog.getText(self, "Новый пользователь", "Имя:")
        # Проверка подтверждения ввода имени
        if not ok or not name:
            return

        cursor = self.um.conn.cursor()
        cursor.execute("SELECT username FROM Users WHERE username = ?", (name,))
        result = cursor.fetchone()
        # Проверка, существует ли пользователь с таким именем
        if result:
            QMessageBox.critical(self, "Ошибка", f"Пользователь с именем '{name}' уже существует.")
            return

        self.um.add_user(name, '', False, False, 0, 0)
        self.refresh_user_list()

    def toggle_policy(self):
        # === Переключение статуса ограничений для выбранного пользователя ===
        current = self.user_list.currentItem()
        if current:
            full_text = current.text()
            username_part = full_text.split(' | ')[0]
            username = username_part.replace("Пользователь: ", "")
            self.um.toggle_policy(username)
            self.refresh_user_list()

    def toggle_lock(self):
        # === Переключение статуса блокировки для выбранного пользователя ===
        current = self.user_list.currentItem()
        if current:
            full_text = current.text()
            username_part = full_text.split(' | ')[0]
            username = username_part.replace("Пользователь: ", "")
            self.um.toggle_lock(username)
            self.refresh_user_list()

    def edit_valid_months(self):
        # === Изменение срока действия пароля для выбранного пользователя ===
        current = self.user_list.currentItem()
        if current:
            full_text = current.text()
            username_part = full_text.split(' | ')[0]
            username = username_part.replace("Пользователь: ", "")
            cursor = self.um.conn.cursor()
            cursor.execute("SELECT valid_months FROM Users WHERE username = ?", (username,))
            result = cursor.fetchone()
            if result:
                current_months = result[0]
                months, ok = QInputDialog.getInt(self, "Срок действия пароля", "Введите количество месяцев (0 = бессрочно):", current_months, 0, 120, 1)
                # Проверка, подтверждён ли ввод
                if ok:
                    cursor.execute("UPDATE Users SET valid_months = ? WHERE username = ?", (months, username))
                    self.um.conn.commit()
                    self.refresh_user_list()

    def edit_min_length(self):
        # === Изменение минимальной длины пароля для выбранного пользователя ===
        current = self.user_list.currentItem()
        if current:
            username = current.text().split(' | ')[0].replace("Пользователь: ", "")
            cursor = self.um.conn.cursor()
            cursor.execute("SELECT min_length FROM Users WHERE username = ?", (username,))
            result = cursor.fetchone()
            if result:
                current_length = result[0]
                length, ok = QInputDialog.getInt(self, "Мин. длина пароля", "Введите новую длину:", current_length, 0, 100, 1)
                # Проверка, подтверждён ли ввод
                if ok:
                    cursor.execute("UPDATE Users SET min_length = ? WHERE username = ?", (length, username))
                    self.um.conn.commit()
                    self.refresh_user_list()

    def delete_user(self):
        # === Удаление выбранного пользователя из базы данных ===
        current = self.user_list.currentItem()
        if current:
            username = current.text().split(' | ')[0]
            # Проверка, что не пытаемся удалить администратора
            if username == 'ADMIN':
                QMessageBox.critical(self, "Ошибка", "Нельзя удалить администратора!")
                return
            reply = QMessageBox.question(self, "Удалить пользователя", f"Удалить пользователя {username}?", 
                                         QMessageBox.Yes | QMessageBox.No)
            # Русские кнопки
            yes_button = reply.button(QMessageBox.Yes)
            if yes_button:
                yes_button.setText("Да")
            no_button = reply.button(QMessageBox.No)
            if no_button:
                no_button.setText("Нет")

            # Проверка подтверждения удаления
            if reply == QMessageBox.Yes:
                try:
                    cursor = self.um.conn.cursor()
                    cursor.execute("DELETE FROM Users WHERE username = ?", (username,))
                    self.um.conn.commit()
                    self.refresh_user_list()
                    QMessageBox.information(self, "Успех", f"Пользователь {username} удалён.")
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении: {str(e)}")

    def change_admin_password(self):
        # === Смена пароля администратора с проверкой старого пароля и ограничений ===
        from PyQt5.QtWidgets import QLineEdit
        old_pwd, ok1 = QInputDialog.getText(self, "Старый пароль", "Введите старый пароль:", echo=QLineEdit.Password)
        # Проверка подтверждения ввода старого пароля
        if not ok1:
            return

        from Crypto.Hash import MD4
        h = MD4.new()
        h.update(old_pwd.encode())
        old_hash = h.hexdigest()

        cursor = self.um.conn.cursor()
        cursor.execute("SELECT password_hash FROM Users WHERE username = ?", ("ADMIN",))
        result = cursor.fetchone()
        # Проверка, существует ли администратор
        if not result:
            QMessageBox.critical(self, "Ошибка", "Пользователь ADMIN не найден.")
            return

        pwd_hash = result[0]
        # Проверка старого пароля: если в базе пустой — введённый должен быть пустым
        if pwd_hash == '':
            if old_pwd != '':
                QMessageBox.critical(self, "Ошибка", "Неверный старый пароль.")
                return
        else:
            # Если в базе не пустой — сравниваем хеши
            if pwd_hash != old_hash:
                QMessageBox.critical(self, "Ошибка", "Неверный старый пароль.")
                return

        new_pwd, ok2 = QInputDialog.getText(self, "Новый пароль", "Введите новый пароль:", echo=QLineEdit.Password)
        # Проверка подтверждения ввода нового пароля
        if not ok2:
            return

        confirm_pwd, ok3 = QInputDialog.getText(self, "Подтверждение", "Повторите новый пароль:", echo=QLineEdit.Password)
        # Проверка подтверждения ввода подтверждения пароля
        if not ok3:
            return

        # Проверка совпадения нового пароля и его подтверждения
        if new_pwd != confirm_pwd:
            QMessageBox.critical(self, "Ошибка", "Пароли не совпадают.")
            return

        # Проверка, включены ли ограничения для администратора
        cursor.execute("SELECT password_policy FROM Users WHERE username = ?", ("ADMIN",))
        result = cursor.fetchone()
        if result and result[0]:
            # Если ограничения включены — проверяем, содержит ли пароль буквы и цифры
            if not self.um.check_password_policy(new_pwd):
                reply = QMessageBox.question(self, "Ошибка", 
                                             f"Пароль не соответствует требованиям: должен содержать буквы и цифры.\n"
                                             "Повторить ввод?", 
                                             QMessageBox.Yes | QMessageBox.No, 
                                             QMessageBox.Yes)
                # Русские кнопки
                yes_button = reply.button(QMessageBox.Yes)
                if yes_button:
                    yes_button.setText("Да")
                no_button = reply.button(QMessageBox.No)
                if no_button:
                    no_button.setText("Нет")

                # Проверка подтверждения повторного ввода
                if reply == QMessageBox.Yes:
                    self.change_admin_password()
                return

        # Проверка минимальной длины пароля
        cursor.execute("SELECT min_length FROM Users WHERE username = ?", ("ADMIN",))
        result = cursor.fetchone()
        if result and result[0] > 0:
            # Извлекаем минимальную длину
            min_len = result[0]
            # Проверка, достаточно ли длинный пароль
            if len(new_pwd) < min_len:
                reply = QMessageBox.question(self, "Ошибка", 
                                             f"Пароль не соответствует требованиям: минимальная длина — {min_len} символов.\n"
                                             "Повторить ввод?", 
                                             QMessageBox.Yes | QMessageBox.No, 
                                             QMessageBox.Yes)
                # Русские кнопки
                yes_button = reply.button(QMessageBox.Yes)
                if yes_button:
                    yes_button.setText("Да")
                no_button = reply.button(QMessageBox.No)
                if no_button:
                    no_button.setText("Нет")

                # Проверка подтверждения повторного ввода
                if reply == QMessageBox.Yes:
                    self.change_admin_password()
                return

        # === Хеширование нового пароля и обновление в базе данных ===
        h = MD4.new()
        h.update(new_pwd.encode())
        new_hash = h.hexdigest()

        cursor.execute("UPDATE Users SET password_hash = ? WHERE username = ?", (new_hash, "ADMIN"))
        self.um.conn.commit()
        QMessageBox.information(self, "Успех", "Пароль администратора изменён.")

    def exit_to_main(self):
        # === Шифрование базы данных и возврат на главное окно ===
        pwd, ok = QInputDialog.getText(self, "Шифрование", "Введите пароль для шифрования файла:", echo=QLineEdit.Password)
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
        self.parent_window.show()
