import sys
import struct
# Импорты для PyQt5 GUI
from PyQt5.QtWidgets import (QApplication, QMainWindow, QFileDialog, QMessageBox,
                             QPushButton, QLabel, QVBoxLayout, QWidget, QMenuBar,
                             QAction, QTextEdit, QHBoxLayout, QGroupBox, QDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class SHA1Calculator:
    # Константы для четырех раундов алгоритма
    K = [0x5A827999, 0x6ED9EBA1, 0x8F1BBCDC, 0xCA62C1D6]

    @staticmethod
    def _left_rotate(value, shift):
        # Циклический сдвиг 32-битного значения влево
        return ((value << shift) | (value >> (32 - shift))) & 0xFFFFFFFF

    @classmethod
    def calculate(cls, data: bytes) -> str:
        # Длина исходных данных в байтах и битах
        original_byte_len = len(data)
        original_bit_len = original_byte_len * 8

        # Добавление бита '1' к концу сообщения
        padded = data + b'\x80'

        # Добавление нулей до тех пор, пока длина не станет 448 бит по модулю 512
        while len(padded) % 64 != 56: # 56 байт = 448 бит
            padded += b'\x00'

        # Добавление длины исходного сообщения в битах (64-бит, big-endian)
        padded += struct.pack('>Q', original_bit_len)

        # Инициализация буфера хеша пятью 32-битными значениями
        h0 = 0x67452301
        h1 = 0xEFCDAB89
        h2 = 0x98BADCFE
        h3 = 0x10325476
        h4 = 0xC3D2E1F0

        # Обработка сообщения по 512-битным блокам
        for i in range(0, len(padded), 64):
            chunk = padded[i:i+64]

            # Преобразование 512-битного блока в 16 32-битных слов
            w = list(struct.unpack('>16I', chunk))

            # Расширение 16 слов до 80 слов по правилу SHA-1
            for t in range(16, 80):
                value = w[t-3] ^ w[t-8] ^ w[t-14] ^ w[t-16]
                w.append(cls._left_rotate(value, 1) & 0xFFFFFFFF)

            # Инициализация рабочих переменных
            a, b, c, d, e = h0, h1, h2, h3, h4

            # Основной цикл из 80 итераций
            for t in range(80):
                # Выбор функции и константы в зависимости от раунда
                if 0 <= t <= 19:
                    f = (b & c) | ((~b) & d)
                    k = cls.K[0]
                elif 20 <= t <= 39:
                    f = b ^ c ^ d
                    k = cls.K[1]
                elif 40 <= t <= 59:
                    f = (b & c) | (b & d) | (c & d)
                    k = cls.K[2]
                elif 60 <= t <= 79:
                    f = b ^ c ^ d
                    k = cls.K[3]

                # Обеспечение 32-битности результатов
                f = f & 0xFFFFFFFF
                k = k & 0xFFFFFFFF

                # Вычисление временного значения для обновления переменных
                temp = (cls._left_rotate(a, 5) + f + e + k + w[t]) & 0xFFFFFFFF
                e = d
                d = c
                c = cls._left_rotate(b, 30) & 0xFFFFFFFF
                b = a
                a = temp

            # Обновление значений буфера хеша
            h0 = (h0 + a) & 0xFFFFFFFF
            h1 = (h1 + b) & 0xFFFFFFFF
            h2 = (h2 + c) & 0xFFFFFFFF
            h3 = (h3 + d) & 0xFFFFFFFF
            h4 = (h4 + e) & 0xFFFFFFFF

        # Формирование итогового 160-битного хеша из пяти 32-битных значений
        result = (h0 << 128) | (h1 << 96) | (h2 << 64) | (h3 << 32) | h4
        return f'{result:040x}'

# Окно с информацией о программе и авторе
class AboutDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("О программе")
        self.setGeometry(300, 300, 400, 200)

        layout = QVBoxLayout()

        # Текстовое поле с информацией
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setText(
            "Лабораторная работа №2\n"
            "Изучение криптографических алгоритмов.\n"
            "Алгоритмы хэширования.\n"
            "Алгоритм: SHA-1\n\n"
            "Автор: Малафеев Леонид Сергеевич\n"
            "Группа: ПИбд-41"
        )
        layout.addWidget(info_text)

        self.setLayout(layout)

# Основное окно приложения
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SHA-1 Хеширование")
        self.setGeometry(100, 100, 600, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Создание меню
        self.menubar = self.menuBar()
        self.file_menu = self.menubar.addMenu('Файл')
        self.help_menu = self.menubar.addMenu('Справка')

        # Действие выхода
        self.exit_action = QAction('Выход', self)
        self.exit_action.triggered.connect(self.close)
        self.file_menu.addAction(self.exit_action)

        # Действие "О программе"
        self.about_action = QAction('О программе', self)
        self.about_action.triggered.connect(self.show_about)
        self.help_menu.addAction(self.about_action)

        # Группа с информацией о работе
        info_group = QGroupBox("Информация о работе")
        info_layout = QVBoxLayout()
        info_label = QLabel(
            "Лабораторная работа №2\n"
            "Изучение криптографических алгоритмов.\n"
            "Алгоритмы хэширования.\n"
            "Алгоритм: SHA-1\n"
            "Автор: Малафеев Леонид Сергеевич\n"
            "Группа: ПИбд-41"
        )
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setFont(QFont("Arial", 10))
        info_layout.addWidget(info_label)
        info_group.setLayout(info_layout)
        self.layout.addWidget(info_group)

        # Группа с элементами для хеширования файла
        hash_group = QGroupBox("Хеширование файла")
        hash_layout = QVBoxLayout()

        self.file_path_label = QLabel("Файл не выбран")
        hash_layout.addWidget(self.file_path_label)

        self.select_file_button = QPushButton("Выбрать файл")
        self.select_file_button.clicked.connect(self.select_file)
        hash_layout.addWidget(self.select_file_button)

        self.calculate_button = QPushButton("Вычислить SHA-1")
        self.calculate_button.clicked.connect(self.calculate_sha1)
        hash_layout.addWidget(self.calculate_button)

        self.result_label = QLabel("Хеш появится здесь...")
        self.result_label.setWordWrap(True)
        hash_layout.addWidget(self.result_label)

        hash_group.setLayout(hash_layout)
        self.layout.addWidget(hash_group)

        # Состояния интерфейса
        self.file_path = None
        self.calculate_button.setEnabled(False) # Кнопка неактивна без файла


    def select_file(self):
        # Диалог выбора файла
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл для хеширования", "", "Все файлы (*)"
        )
        if file_path:
            # Проверка размера файла не менее 1 КБ
            import os
            try:
                file_size = os.path.getsize(file_path)
                if file_size < 1024: # 1 КБ = 1024 байта
                    QMessageBox.critical(self, "Ошибка", f"Файл должен быть не менее 1 КБ.\nРазмер выбранного файла: {file_size} байт.")
                    return
            except OSError:
                QMessageBox.critical(self, "Ошибка", f"Не удалось получить размер файла.")
                return

            self.file_path = file_path
            self.file_path_label.setText(f"Выбран файл: {os.path.basename(file_path)}")
            self.calculate_button.setEnabled(True) # Активация кнопки хеширования

    def calculate_sha1(self):
        # Вычисление и отображение SHA-1 хеша
        if not self.file_path:
            QMessageBox.warning(self, "Предупреждение", "Сначала выберите файл.")
            return

        try:
            with open(self.file_path, 'rb') as f:
                data = f.read()
            hash_result = SHA1Calculator.calculate(data)
            self.result_label.setText(f"SHA-1 хеш:\n{hash_result}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при вычислении хеша:\n{str(e)}")

    def show_about(self):
        # Открытие окна "О программе"
        self.about_dialog = AboutDialog()
        self.about_dialog.exec_()

def main():
    # Запуск PyQt приложения
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()