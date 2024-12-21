import cv2
from ultralytics import YOLO
import pytesseract
from collections import Counter
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout,
    QWidget, QLineEdit, QTableWidget, QTableWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
import threading
import serial
import time

# Tesseract OCR'ın tam yolunu belirtin
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

# Veritabanı bağlantısı
conn = sqlite3.connect("plates.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS plates (id INTEGER PRIMARY KEY, plate TEXT)")
conn.commit()

# Modeli yükle
model = YOLO(r"modelin bulunduğu yol ör: c:\\Desktop\best1.pt")

# Arduino bağlantısı
arduino = serial.Serial(port='COM3', baudrate=9600, timeout=1)  # Arduino'nun bağlı olduğu portu değiştirin

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Plaka Tanıma Sistemi")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Ana düzen
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Plaka Ekleme
        self.plate_input = QLineEdit()
        self.plate_input.setPlaceholderText("Plaka girin (örn: 34ABC123)")
        self.layout.addWidget(self.plate_input)

        self.add_plate_button = QPushButton("Plaka Ekle")
        self.add_plate_button.clicked.connect(self.add_plate)
        self.layout.addWidget(self.add_plate_button)

        # Plaka Silme
        self.delete_plate_button = QPushButton("Plaka Sil")
        self.delete_plate_button.clicked.connect(self.delete_plate)
        self.layout.addWidget(self.delete_plate_button)

        # Veritabanını Göster
        self.plate_table = QTableWidget()
        self.plate_table.setColumnCount(1)
        self.plate_table.setHorizontalHeaderLabels(["Plakalar"])
        self.layout.addWidget(self.plate_table)
        self.load_database()

        # Kamera Görüntüsü
        self.camera_label = QLabel()
        self.layout.addWidget(self.camera_label)

        # Anlık Okunan Plaka
        self.current_plate_label = QLabel("Okunan Plaka: ")
        self.layout.addWidget(self.current_plate_label)

        # Durum Göstergesi
        self.status_indicator = QLabel()
        self.status_indicator.setFixedSize(30, 30)
        self.layout.addWidget(self.status_indicator)

        # Kamerayı Başlat
        self.start_camera_button = QPushButton("Kamerayı Başlat")
        self.start_camera_button.clicked.connect(self.start_camera)
        self.layout.addWidget(self.start_camera_button)

        self.stop_camera_button = QPushButton("Kamerayı Durdur")
        self.stop_camera_button.clicked.connect(self.stop_camera)
        self.layout.addWidget(self.stop_camera_button)

        self.running = False
        self.match_timer = None  # Eşleşme zamanlayıcısı
        self.last_matched_plate = None  # Son eşleşen plaka

    def load_database(self):
        cursor.execute("SELECT plate FROM plates")
        plates = cursor.fetchall()
        self.plate_table.setRowCount(len(plates))
        for row, plate in enumerate(plates):
            self.plate_table.setItem(row, 0, QTableWidgetItem(plate[0]))

    def add_plate(self):
        plate = self.plate_input.text().strip().upper()
        if plate:
            cursor.execute("INSERT INTO plates (plate) VALUES (?)", (plate,))
            conn.commit()
            self.load_database()
            self.plate_input.clear()
            QMessageBox.information(self, "Başarılı", f"{plate} plakası eklendi.")

    def delete_plate(self):
        plate = self.plate_input.text().strip().upper()
        if plate:
            cursor.execute("DELETE FROM plates WHERE plate = ?", (plate,))
            conn.commit()
            self.load_database()
            self.plate_input.clear()
            QMessageBox.information(self, "Başarılı", f"{plate} plakası silindi.")

    def start_camera(self):
        self.running = True
        self.camera_thread = threading.Thread(target=self.run_camera, daemon=True)
        self.camera_thread.start()

    def stop_camera(self):
        self.running = False

    def preprocess_for_ocr(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (7, 7), 0)
        thresholded = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        enhanced = cv2.convertScaleAbs(thresholded, alpha=2, beta=6)
        return enhanced

    def update_status_indicator(self, match):
        if match:
            self.status_indicator.setStyleSheet("background-color: green; border-radius: 15px;")

            # Eğer eşleşen plaka sürekli aynı ise Arduino komutu gönder
            if self.last_matched_plate != self.current_plate_label.text():
                self.last_matched_plate = self.current_plate_label.text()
                if self.match_timer is not None:
                    self.match_timer.cancel()

                self.match_timer = threading.Timer(1.0, self.activate_servo)
                self.match_timer.start()
        else:
            self.status_indicator.setStyleSheet("background-color: red; border-radius: 15px;")
            self.last_matched_plate = None  # Plaka eşleşmesi kaybolursa sıfırla
            if self.match_timer is not None:
                self.match_timer.cancel()

    def activate_servo(self):
        try:
            arduino.write(b"ACTIVATE\n")  # Arduino'ya komut gönder
            time.sleep(1)
        except Exception as e:
            print(f"Servo kontrol hatası: {e}")

    def run_camera(self):
        cap = cv2.VideoCapture(0)
        ocr_results = []
        while self.running:
            ret, frame = cap.read()
            if not ret:
                continue

            results = model.predict(source=frame, show=False, conf=0.5)

            found_plate = False

            for result in results:
                boxes = result.boxes.xyxy.cpu().numpy() if result.boxes else []
                for box in boxes:
                    x1, y1, x2, y2 = map(int, box[:4])
                    cropped_plate = frame[y1:y2, x1:x2]
                    if cropped_plate.size > 0:
                        height, width, _ = cropped_plate.shape
                        ocr_ready_plate = cropped_plate[int(height * 0.15):int(height * 0.95), int(width * 0.10):int(width * 0.98)]
                        preprocessed_plate = self.preprocess_for_ocr(ocr_ready_plate)

                        config = "--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
                        ocr_text = pytesseract.image_to_string(preprocessed_plate, config=config).strip()

                        if ocr_text:
                            if len(ocr_text) > 1 and ocr_text[0].upper() == "O":
                                ocr_text = "0" + ocr_text[1:]
                            if len(ocr_text) > 1 and ocr_text[1].upper() == "O":
                                ocr_text = ocr_text[0] + "0" + ocr_text[2:]

                            ocr_results.append(ocr_text)
                            if len(ocr_results) > 10:
                                ocr_results.pop(0)
                            most_common_text = Counter(ocr_results).most_common(1)[0][0]

                            self.current_plate_label.setText(f"Okunan Plaka: {most_common_text}")

                            cursor.execute("SELECT plate FROM plates WHERE plate = ?", (most_common_text,))
                            match = cursor.fetchone()

                            self.update_status_indicator(match is not None)

                            found_plate = True

            if not found_plate:
                self.update_status_indicator(False)

            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            qt_image = QImage(rgb_image.data, w, h, ch * w, QImage.Format_RGB888)
            self.camera_label.setPixmap(QPixmap.fromImage(qt_image))

        cap.release()

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    main_app = MainApp()
    main_app.show()
    sys.exit(app.exec_())
