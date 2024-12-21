

---

# Plaka Tanıma Sistemi

Bu proje, kamera görüntülerinden plaka tanıma yaparak plakaları bir veritabanında eşleştiren ve gerekli durumlarda Arduino üzerinden kontrol edilen bir işlem gerçekleştiren bir sistemdir.

## Özellikler

- **Gerçek Zamanlı Plaka Tanıma**: YOLO modeli ve OCR (Tesseract) kullanarak plakaları algılar ve okur.
- **Veritabanı Yönetimi**: Plakaları SQLite veritabanında saklama, silme ve listeleme özellikleri.
- **Arduino Entegrasyonu**: Eşleşen plaka durumunda Arduino'ya komut gönderir.
- **Kullanıcı Dostu Arayüz**: PyQt5 ile oluşturulan bir GUI üzerinden plaka yönetimi ve kamera kontrolü.

## Gereksinimler

Bu projeyi çalıştırmak için aşağıdaki yazılımlara ve kütüphanelere ihtiyaç vardır:

- Python 3.x
- OpenCV
- YOLO (Ultralytics)
- Tesseract OCR (Kurulum için [Tesseract OCR](https://github.com/tesseract-ocr/tesseract))
- SQLite
- PyQt5
- PySerial

### Kurulum Adımları

1. **Gerekli Python Kütüphanelerini Kurun**:
    ```bash
    pip install opencv-python ultralytics pytesseract pyqt5 pyserial
    ```
2. **Tesseract OCR Kurulumu**:
   - Tesseract'ı [buradan](https://github.com/tesseract-ocr/tesseract) indirip kurun.
   - `pytesseract.pytesseract.tesseract_cmd` satırında, Tesseract'ın yüklü olduğu yolu belirtin.

3. **Model Dosyasını Yükleyin**:
   - `best1.pt` dosyasını, proje dosyalarıyla aynı klasöre yerleştirin veya yolunu doğru bir şekilde belirtin.

4. **Arduino Ayarları**:
   - Arduino cihazınızı bağlayın ve doğru COM portunu belirtin.

## Kullanım

1. Uygulamayı çalıştırın:
   ```bash
   python PTSAI.py
   ```
2. Plaka yönetimi ve kamera kontrolü için kullanıcı arayüzünü kullanın.
3. Eşleşen plakalar için duruma bağlı olarak Arduino'dan servo motor kontrolü yapılır.

## Dosya Yapısı

- `PTSAI.py`: Ana Python dosyası, tüm fonksiyonellik bu dosyada sağlanır.
- `best1.pt`: YOLO modeli için eğitimli ağırlık dosyası.

## İletişim:

Sidar Yurdusever
sidaryurdusever@gmail.com

--- 
