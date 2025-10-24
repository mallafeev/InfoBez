import sys
import os
from PyQt5.QtWidgets import QApplication
from login_window import LoginWindow
from password_dialog import PasswordDialog

if __name__ == "__main__":
    app = QApplication(sys.argv)

    if os.path.exists('data/users.db.enc'):
        print("Файл существует. Требуется расшифровка.")
        pwd_dialog = PasswordDialog("Расшифровка", "Введите пароль для расшифровки файла:")
    else:
        print("Файл не существует. Требуется шифрование.")
        pwd_dialog = PasswordDialog("Шифрование", "Введите пароль для шифрования файла:")

    pwd = pwd_dialog.get_password()
    if not pwd:
        sys.exit()

    login = LoginWindow(pwd)
    login.show()

    def on_exit():
        login.um.close()

    app.aboutToQuit.connect(on_exit)

    sys.exit(app.exec_())