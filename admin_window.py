from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QPushButton, QListWidget, QMessageBox, QHBoxLayout, QInputDialog, QLineEdit
)

class AdminWindow(QMainWindow):
    def __init__(self, um, parent_window):
        super().__init__()
        self.um = um
        self.parent_window = parent_window
        self.setWindowTitle("Панель администратора")
        self.setGeometry(300, 300, 900, 500)

        layout = QVBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.user_list = QListWidget()
        self.refresh_user_list()
        layout.addWidget(self.user_list)

        # Кнопки
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

        # Кнопка "Сохранить и выйти"
        btn_save_and_exit = QPushButton("Сохранить и выйти")
        btn_save_and_exit.clicked.connect(self.save_and_exit)
        layout.addWidget(btn_save_and_exit)

    def refresh_user_list(self):
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
        name, ok = QInputDialog.getText(self, "Новый пользователь", "Имя:")
        if not ok or not name:
            return

        # Устанавливаем пароль по умолчанию
        default_password = "user"
        from Crypto.Hash import MD4
        h = MD4.new()
        h.update(default_password.encode())
        pwd_hash = h.hexdigest()

        self.um.add_user(name, pwd_hash, False, False, 0, 0)
        self.refresh_user_list()

    def toggle_lock(self):
        current = self.user_list.currentItem()
        if current:
            username = current.text().split(' | ')[0]
            self.um.toggle_lock(username)
            self.refresh_user_list()

    def toggle_policy(self):
        current = self.user_list.currentItem()
        if current:
            username = current.text().split(' | ')[0]
            self.um.toggle_policy(username)
            self.refresh_user_list()

    def edit_min_length(self):
        current = self.user_list.currentItem()
        if current:
            username = current.text().split(' | ')[0]
            # Получаем текущую длину из базы
            cursor = self.um.conn.cursor()
            cursor.execute("SELECT min_length FROM Users WHERE username = ?", (username,))
            result = cursor.fetchone()
            if result:
                current_length = result[0]
                length, ok = QInputDialog.getInt(self, "Мин. длина пароля", "Введите новую длину:", current_length, 0, 100, 1)
                if ok:
                    cursor.execute("UPDATE Users SET min_length = ? WHERE username = ?", (length, username))
                    self.um.conn.commit()
                    self.refresh_user_list()

    def edit_valid_months(self):
        current = self.user_list.currentItem()
        if current:
            username = current.text().split(' | ')[0]
            # Получаем текущий срок из базы
            cursor = self.um.conn.cursor()
            cursor.execute("SELECT valid_months FROM Users WHERE username = ?", (username,))
            result = cursor.fetchone()
            if result:
                current_months = result[0]
                months, ok = QInputDialog.getInt(self, "Срок действия пароля", "Введите количество месяцев (0 = бессрочно):", current_months, 0, 120, 1)
                if ok:
                    cursor.execute("UPDATE Users SET valid_months = ? WHERE username = ?", (months, username))
                    self.um.conn.commit()
                    self.refresh_user_list()

    def delete_user(self):
        current = self.user_list.currentItem()
        if current:
            username = current.text().split(' | ')[0]
            if username == 'ADMIN':
                QMessageBox.critical(self, "Ошибка", "Нельзя удалить администратора!")
                return
            reply = QMessageBox.question(self, "Удалить пользователя", f"Удалить пользователя {username}?", 
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                cursor = self.um.conn.cursor()
                cursor.execute("DELETE FROM Users WHERE username = ?", (username,))
                self.um.conn.commit()
                self.refresh_user_list()

    def change_admin_password(self):
        from PyQt5.QtWidgets import QLineEdit
        old_pwd, ok1 = QInputDialog.getText(self, "Старый пароль", "Введите старый пароль:", echo=QLineEdit.Password)
        if not ok1:
            return

        # Проверяем, совпадает ли старый пароль с хешем администратора
        from Crypto.Hash import MD4
        h = MD4.new()
        h.update(old_pwd.encode())
        old_hash = h.hexdigest()

        cursor = self.um.conn.cursor()
        cursor.execute("SELECT password_hash FROM Users WHERE username = ?", ("ADMIN",))
        result = cursor.fetchone()
        if not result or result[0] != old_hash:
            QMessageBox.critical(self, "Ошибка", "Неверный старый пароль.")
            return

        new_pwd, ok2 = QInputDialog.getText(self, "Новый пароль", "Введите новый пароль:", echo=QLineEdit.Password)
        if not ok2:
            return

        confirm_pwd, ok3 = QInputDialog.getText(self, "Подтверждение", "Повторите новый пароль:", echo=QLineEdit.Password)
        if not ok3:
            return

        if new_pwd != confirm_pwd:
            QMessageBox.critical(self, "Ошибка", "Пароли не совпадают.")
            return

        # Проверяем, включены ли ограничения для администратора
        cursor.execute("SELECT password_policy FROM Users WHERE username = ?", ("ADMIN",))
        result = cursor.fetchone()
        if result and result[0]:
            # Ограничения включены: проверяем, содержит ли пароль буквы и цифры
            if not self.um.check_password_policy(new_pwd):
                QMessageBox.critical(self, "Ошибка", "Пароль не соответствует требованиям: должен содержать буквы и цифры.")
                return

        # Хешируем новый пароль и обновляем в базе
        h = MD4.new()
        h.update(new_pwd.encode())
        new_hash = h.hexdigest()

        cursor.execute("UPDATE Users SET password_hash = ? WHERE username = ?", (new_hash, "ADMIN"))
        self.um.conn.commit()
        QMessageBox.information(self, "Успех", "Пароль администратора изменён.")

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
        self.parent_window.show()