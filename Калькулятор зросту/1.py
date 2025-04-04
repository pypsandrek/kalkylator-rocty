from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QMessageBox, QLabel, QVBoxLayout
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
import random
import sys
import cv2
import numpy as np

class CameraWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Камера активована")
        self.setGeometry(100, 100, 640, 480)
        self.label = QLabel(self)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)
        
        try:
            self.camera = cv2.VideoCapture(0)
            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(self.update_frame)
            self.timer.start(30)
        except:
            self.label.setText("Не вдалося підключити камеру")

    def update_frame(self):
        ret, frame = self.camera.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.label.setPixmap(QPixmap.fromImage(q_img).scaled(
                self.label.width(), self.label.height(), QtCore.Qt.KeepAspectRatio))

    def closeEvent(self, event):
        if hasattr(self, 'timer'):
            self.timer.stop()
        if hasattr(self, 'camera'):
            self.camera.release()
        event.accept()

class HeightCalculator(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.camera_window = None
        self.setup_ui()
        self.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint)  # Відключаємо кнопку закриття
        
    def setup_ui(self):
        self.setWindowTitle("Калькулятор зросту (жартівливий)")
        self.resize(790, 596)
        
        # Заголовок
        self.label = QtWidgets.QLabel("Калькулятор зросту", self)
        self.label.setGeometry(200, 50, 394, 80)
        self.label.setFont(QtGui.QFont("Arial", 26))
        
        # Поле для введення (метри)
        self.textEdit = QtWidgets.QTextEdit(self)
        self.textEdit.setGeometry(270, 190, 241, 69)
        
        # Статичні написали "М" і "СМ" (приховані спочатку)
        self.label_m = QtWidgets.QLabel("М", self)
        self.label_m.setGeometry(520, 190, 89, 71)
        self.label_m.setFont(QtGui.QFont("Arial", 28))
        self.label_m.setAlignment(QtCore.Qt.AlignCenter)
        self.label_m.hide()
        
        self.label_cm = QtWidgets.QLabel("СМ", self)
        self.label_cm.setGeometry(520, 290, 89, 71)
        self.label_cm.setFont(QtGui.QFont("Arial", 28))
        self.label_cm.setAlignment(QtCore.Qt.AlignCenter)
        self.label_cm.hide()
        
        # Поля для виводу результату (приховані спочатку)
        self.result_m = QtWidgets.QTextEdit(self)
        self.result_m.setGeometry(270, 190, 241, 71)
        self.result_m.setReadOnly(True)
        self.result_m.setFont(QtGui.QFont("Arial", 28))
        self.result_m.hide()
        
        self.result_cm = QtWidgets.QTextEdit(self)
        self.result_cm.setGeometry(270, 290, 241, 71)
        self.result_cm.setReadOnly(True)
        self.result_cm.setFont(QtGui.QFont("Arial", 28))
        self.result_cm.hide()
        
        # Текстовий лейбл для жартів
        self.joke_label = QtWidgets.QLabel("", self)
        self.joke_label.setGeometry(190, 370, 441, 30)
        self.joke_label.setFont(QtGui.QFont("Arial", 12))
        self.joke_label.setAlignment(QtCore.Qt.AlignCenter)
        self.joke_label.setStyleSheet("color: red;")
        
        # Прогрес-бар
        self.progressBar = QtWidgets.QProgressBar(self)
        self.progressBar.setGeometry(190, 410, 441, 31)
        self.progressBar.hide()
        
        # Кнопка
        self.pushButton = QtWidgets.QPushButton("РОЗПОЧАТИ АНАЛІЗ", self)
        self.pushButton.setGeometry(320, 470, 160, 80)
        self.pushButton.clicked.connect(self.start_analysis)

    def keyPressEvent(self, event):
        """Обробка натискання клавіш - закриття тільки на 'g'"""
        if event.key() == Qt.Key_G:
            self.force_close()
        super().keyPressEvent(event)
            
    def force_close(self):
        """Примусове закриття програми"""
        self.stop_camera()
        QtWidgets.QApplication.quit()
        
    def closeEvent(self, event):
        """Блокуємо всі спроби закриття, крім натискання 'g'"""
        event.ignore()
        QMessageBox.information(self, "Увага", 
                              "Програма закривається ТІЛЬКИ при натисканні клавіші 'g'")

    def start_analysis(self):
        """Запускає жартівливе 'сканування' і виводить результат."""
        self.pushButton.hide()
        self.progressBar.show()
        self.progressBar.setValue(0)
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(100)
        
        self.scary_messages = [
            "Підключення до камери...",
            "Сканування WiFi...",
            "Скачування троянів...",
            "Скачування вірусів",
            "Ваш зріст передається в NSA...",
        ]
        self.current_message = 0

    def update_progress(self):
        current_value = self.progressBar.value() + 1
        self.progressBar.setValue(current_value)
        
        if current_value % 20 == 0:
            message = random.choice(self.scary_messages)
            self.joke_label.setText(message)
            
            if "камери" in message and not self.camera_window:
                self.connect_camera()
            
            QtWidgets.QApplication.processEvents()
        
        if current_value >= 100:
            self.timer.stop()
            self.stop_camera()
            self.show_results()

    def connect_camera(self):
        """Відкриває окреме вікно з камерою"""
        try:
            self.camera_window = CameraWindow()
            self.camera_window.show()
        except Exception as e:
            print(f"Помилка камери: {e}")
            self.joke_label.setText("Помилка підключення камери")

    def stop_camera(self):
        """Закриває вікно камери"""
        if self.camera_window:
            self.camera_window.close()
            self.camera_window = None

    def show_results(self):
        """Показує результати після завершення аналізу"""
        try:
            height_m = float(self.textEdit.toPlainText().replace(",", "."))
            height_cm = height_m * 100
            
            self.result_m.setPlainText(f"{height_m:.2f}")
            self.result_cm.setPlainText(f"{height_cm:.2f}")
            
            self.label_m.show()
            self.label_cm.show()
            self.result_m.show()
            self.result_cm.show()
            
            final_jokes = [
                "Дані успішно викрадено!",
                "Gmail акаунт успішно викрадено!",
                "Ваші дані тепер у DarkWeb","Виявлено аномалії в ДНК",
                "Я БАЧУ ТЕБЕ"
            ]
            self.joke_label.setText(random.choice(final_jokes))
            
            self.pushButton.show()
            
        except:
            QMessageBox.warning(self, "ПОМИЛКА", "Введіть коректне число!")
            self.pushButton.show()
            self.progressBar.hide()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    calculator = HeightCalculator()
    calculator.show()
    sys.exit(app.exec_())