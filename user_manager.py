import sqlite3
import os
from datetime import datetime, timedelta
from crypto import decrypt_file, encrypt_file
from Crypto.Hash import MD4

class UserManager:
    def __init__(self, enc_file='data/users.db.enc', password=None):
        os.makedirs(os.path.dirname(enc_file), exist_ok=True)
        self.enc_file = enc_file
        self.db_path = 'data/users.db.tmp'
        self.conn = None
        self.load_from_encrypted(password)

    def load_from_encrypted(self, pwd):
        print(f"Расшифровываем с паролем: {pwd}")
        if not os.path.exists(self.enc_file):
            print("Файл не найден. Создаём новый.")
            self.init_db()
            self.add_user('ADMIN', '', False, False, 0, 0)
            self.save_to_encrypted(pwd)
            return

        print("Файл найден. Расшифровываем.")
        try:
            with open(self.enc_file, 'rb') as f:
                data = f.read()
            decrypted = decrypt_file(data, pwd)
            with open(self.db_path, 'wb') as f:
                f.write(decrypted)
            self.conn = sqlite3.connect(self.db_path)
            print(f"Соединение с базой: {self.conn}")
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            print(f"Ошибка расшифровки: {e}")
            QMessageBox.critical(None, "Ошибка", "Ошибка расшифровки. Неверный пароль или файл поврежден.")
            raise SystemExit

    def init_db(self):
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                username TEXT PRIMARY KEY,
                password_hash TEXT,
                locked INTEGER,
                password_policy INTEGER,
                min_length INTEGER,
                valid_months INTEGER
            )
        ''')
        self.conn.commit()

    def save_to_encrypted(self, pwd):
        with open(self.db_path, 'rb') as f:
            data = f.read()
        encrypted = encrypt_file(data, pwd)
        with open(self.enc_file, 'wb') as f:
            f.write(encrypted)

    def authenticate(self, username, password):
        cursor = self.conn.cursor()
        cursor.execute("SELECT password_hash, locked, valid_months FROM Users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if not row:
            return False, "Пользователь не найден"
        pwd_hash, locked, valid_months = row
        if locked:
            return False, "Аккаунт заблокирован"

        if pwd_hash == '':
            if password == '':
                return True, "Успешно"
            else:
                return False, "Неверный пароль"
        else:
            h = MD4.new()
            h.update(password.encode())
            input_hash = h.hexdigest()
            if pwd_hash != input_hash:
                return False, "Неверный пароль"
        if valid_months > 0:
            pass
        return True, "Успешно"

    def check_password_policy(self, password):
        has_letter = any(c.isalpha() for c in password)
        has_digit = any(c.isdigit() for c in password)
        return has_letter and has_digit

    def add_user(self, username, password_hash, locked, password_policy, min_length, valid_months):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO Users VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, password_hash, int(locked), int(password_policy), min_length, valid_months))
        self.conn.commit()

    def get_all_users(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Users")
        return cursor.fetchall()

    def toggle_lock(self, username):
        cursor = self.conn.cursor()
        cursor.execute("SELECT locked FROM Users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if row:
            new_status = 1 - row[0]
            cursor.execute("UPDATE Users SET locked = ? WHERE username = ?", (new_status, username))
            self.conn.commit()

    def toggle_policy(self, username):
        cursor = self.conn.cursor()
        cursor.execute("SELECT password_policy FROM Users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if row:
            new_status = 1 - row[0]
            cursor.execute("UPDATE Users SET password_policy = ? WHERE username = ?", (new_status, username))
            self.conn.commit()

    def change_password(self, username, old_password, new_password, confirm_password):
        cursor = self.conn.cursor()
        cursor.execute("SELECT password_hash, password_policy, min_length FROM Users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if not row:
            return False, "Пользователь не найден"

        pwd_hash, policy_enabled, min_length = row

        if pwd_hash == '':
            if old_password != '':
                return False, "Старый пароль неверен"
        else:
            h = MD4.new()
            h.update(old_password.encode())
            old_hash = h.hexdigest()
            if pwd_hash != old_hash:
                return False, "Старый пароль неверен"

        if new_password != confirm_password:
            return False, "Пароли не совпадают"

        if policy_enabled:
            if not self.check_password_policy(new_password):
                return False, f"Пароль не соответствует требованиям: должен содержать буквы и цифры."

        if len(new_password) < min_length:
            return False, f"Пароль не соответствует требованиям: минимальная длина — {min_length} символов."

        h = MD4.new()
        h.update(new_password.encode())
        new_hash = h.hexdigest()
        cursor.execute("UPDATE Users SET password_hash = ? WHERE username = ?", (new_hash, username))
        self.conn.commit()
        return True, "Пароль изменен"

    def close(self):
        if self.conn:
            self.conn.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)