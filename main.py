import sys
from PyQt5.QtWidgets import QApplication
from login_window import LoginWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginWindow()
    login.show()

    def on_exit():
        login.um.close()

    app.aboutToQuit.connect(on_exit)

    sys.exit(app.exec_())