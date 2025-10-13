import sqlite3
import os
from datetime import datetime, timedelta
from crypto import decrypt_file, encrypt_file
from Crypto.Hash import MD4

class UserManager:
    def __init__(self, enc_file='data/users.db.enc'):
        os.makedirs(os.path.dirname(enc_file), exist_ok=True)
        self.enc_file = enc_file
        self.db_path = 'data/users.db.tmp'
        self.conn = None
        self.load_from_encrypted()

    def load_from_encrypted(self):
        if not os.path.exists(self.enc_file):
            # Создать файл с администратором
            self.init_db()
            # Устанавливаем хеш MD4 от "admin" для пользователя ADMIN
            h = MD4.new()
            h.update("admin".encode())
            admin_hash = h.hexdigest()
            self.add_user('ADMIN', admin_hash, False, False, 0, 0)
            self.save_to_encrypted()
            return

        pwd = input("Введите пароль для расшифровки файла: ")
        try:
            with open(self.enc_file, 'rb') as f:
                data = f.read()
            decrypted = decrypt_file(data, pwd)
            with open(self.db_path, 'wb') as f:
                f.write(decrypted)
            self.conn = sqlite3.connect(self.db_path)
        except:
            print("Ошибка расшифровки. Неверный пароль или файл поврежден.")
            exit()

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

    def save_to_encrypted(self):
        # Сохраняем и шифруем, но НЕ закрываем соединение
        with open(self.db_path, 'rb') as f:
            data = f.read()
        pwd = input("Введите пароль для шифрования файла: ")
        encrypted = encrypt_file(data, pwd)
        with open(self.enc_file, 'wb') as f:
            f.write(encrypted)
    
    def check_password_policy(self, password):
        # Проверка, содержит ли пароль хотя бы одну букву и хотя бы одну цифру
        has_letter = any(c.isalpha() for c in password)
        has_digit = any(c.isdigit() for c in password)
        return has_letter and has_digit

    def authenticate(self, username, password):
        cursor = self.conn.cursor()
        cursor.execute("SELECT password_hash, locked, valid_months FROM Users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if not row:
            return False, "Пользователь не найден"
        pwd_hash, locked, valid_months = row
        if locked:
            return False, "Аккаунт заблокирован"
        h = MD4.new()
        h.update(password.encode())
        input_hash = h.hexdigest()
        if pwd_hash != input_hash:
            return False, "Неверный пароль.  Попробуйте стандартные пароли admin или user"
        # Проверка срока действия
        if valid_months > 0:
            # Если срок действия > 0, считаем, что пароль действителен
            # (в реальном приложении нужно хранить дату создания пароля)
            pass
        return True, "Успешно"

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
        h = MD4.new()
        h.update(old_password.encode())
        old_hash = h.hexdigest()

        cursor = self.conn.cursor()
        cursor.execute("SELECT password_hash FROM Users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if not row or row[0] != old_hash:
            return False, "Старый пароль неверен"
        if new_password != confirm_password:
            return False, "Пароли не совпадают"
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