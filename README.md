Plaka Tanıma Sistemi
Bu proje, kamera görüntülerinden plaka tanıma yaparak plakaları bir veritabanında eşleştiren ve gerekli durumlarda Arduino üzerinden kontrol edilen bir işlem gerçekleştiren bir sistemdir.

Özellikler
Gerçek Zamanlı Plaka Tanıma: YOLO modeli ve OCR (Tesseract) kullanarak plakaları algılar ve okur.
Veritabanı Yönetimi: Plakaları SQLite veritabanında saklama, silme ve listeleme özellikleri.
Arduino Entegrasyonu: Eşleşen plaka durumunda Arduino'ya komut gönderir.
Kullanıcı Dostu Arayüz: PyQt5 ile oluşturulan bir GUI üzerinden plaka yönetimi ve kamera kontrolü.
Gereksinimler
Bu projeyi çalıştırmak için aşağıdaki yazılımlara ve kütüphanelere ihtiyaç vardır:

Python 3.x
OpenCV
YOLO (Ultralytics)
Tesseract OCR (Kurulum için Tesseract OCR)
SQLite
PyQt5
PySerial
Kurulum Adımları
Gerekli Python Kütüphanelerini Kurun:

bash
Kodu kopyala
pip install opencv-python ultralytics pytesseract pyqt5 pyserial
Tesseract OCR Kurulumu:

Tesseract'ı buradan indirip kurun.
pytesseract.pytesseract.tesseract_cmd satırında, Tesseract'ın yüklü olduğu yolu belirtin.
Model Dosyasını Yükleyin:

best1.pt dosyasını, proje dosyalarıyla aynı klasöre yerleştirin veya yolunu doğru bir şekilde belirtin.
Arduino Ayarları:

Arduino cihazınızı bağlayın ve doğru COM portunu belirtin.
Kullanım
Uygulamayı çalıştırın:
bash
Kodu kopyala
python PTSAI.py
Plaka yönetimi ve kamera kontrolü için kullanıcı arayüzünü kullanın.
Eşleşen plakalar için duruma bağlı olarak Arduino'dan servo motor kontrolü yapılır.
Dosya Yapısı
PTSAI.py: Ana Python dosyası, tüm fonksiyonellik bu dosyada sağlanır.
best1.pt: YOLO modeli için eğitimli ağırlık dosyası.
