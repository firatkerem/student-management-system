# 🎓 Öğrenci Yönetim Sistemi

Flask ve SQLite kullanılarak geliştirilmiş kapsamlı bir öğrenci yönetim sistemi.

## 🌟 Özellikler

### 👥 Kullanıcı Rolleri
- **Öğretmen**: Öğrenci, kurs, not yönetimi, PDF raporları, duyuru yayınlama
- **Öğrenci**: Kurs görüntüleme, not takibi, PDF indirme, duyuru okuma

### 📄 PDF Rapor Sistemi
- Öğrenci kişisel raporları
- Kurs detay raporları  
- Genel istatistik raporları
- İngilizce format

### 📝 Kişisel Not Sistemi
- Öğretmen ve öğrenci notları
- Başlık ve içerik organizasyonu
- Tarih takibi

### 📢 Duyuru Sistemi
- Öğretmenler tarafından yayınlama
- Öğrenciler tarafından görüntüleme
- Tarih sıralaması

## 🛠️ Teknoloji Stack

- **Backend**: Flask, SQLAlchemy, Flask-Login
- **Frontend**: Bootstrap 5, Font Awesome, Jinja2
- **Database**: SQLite
- **PDF**: ReportLab

## 🚀 Kurulum

```bash
# Projeyi klonlayın
git clone <repository-url>
cd student-management-system

# Sanal ortam oluşturun
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# Bağımlılıkları yükleyin
pip install -r requirements.txt

# Uygulamayı çalıştırın
python app.py
```

Tarayıcıda açın: `http://localhost:8080`

## 👤 Test Kullanıcıları

### Öğretmen Hesabı
- **Email**: teacher@test.com
- **Şifre**: password

### Öğrenci Hesabı  
- **Email**: student@test.com
- **Şifre**: password

## 📁 Proje Yapısı

```
student-management-system/
├── app.py                 # Ana Flask uygulaması
├── config.py             # Konfigürasyon
├── models.py             # Veritabanı modelleri
├── routes.py             # Flask route'ları
├── add_sample_data.py    # Örnek veri scripti
├── requirements.txt      # Bağımlılıklar
├── templates/            # HTML template'leri
│   ├── base.html        # Ana template
│   ├── student/         # Öğrenci sayfaları
│   └── teacher/         # Öğretmen sayfaları
└── static/              # CSS, JS dosyaları
```

## 🗄️ Veritabanı Tabloları

- **users**: Kullanıcı bilgileri (öğretmen/öğrenci)
- **courses**: Kurs bilgileri
- **enrollments**: Kurs kayıtları
- **grades**: Not bilgileri
- **notes**: Kişisel notlar
- **announcements**: Duyurular

## 🔧 Kullanım

### Öğretmen İşlemleri
1. Giriş yapın (`teacher@test.com` / `password`)
2. Dashboard'dan istediğiniz işlemi seçin:
   - Öğrenci yönetimi
   - Kurs yönetimi
   - Not yönetimi
   - PDF raporları
   - Duyuru yönetimi

### Öğrenci İşlemleri
1. Giriş yapın (`student@test.com` / `password`)
2. Dashboard'da kurslarınızı ve notlarınızı görüntüleyin
3. PDF raporunuzu indirin
4. Duyuruları takip edin

## 🛡️ Güvenlik

- Şifre hashleme (Werkzeug)
- Rol tabanlı erişim kontrolü
- Session yönetimi (Flask-Login)
- SQL injection koruması (SQLAlchemy)

## 📝 Lisans

MIT Lisansı

---

**© 2024 Öğrenci Yönetim Sistemi** 