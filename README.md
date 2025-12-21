# 🏋️ Fitness Bros - Spor Salonu Yönetim Sistemi

[![Django CI](https://github.com/sultannkayi/fitness_bros/actions/workflows/python-ci.yml/badge.svg)](https://github.com/sultannkayi/fitness_bros/actions/workflows/python-ci.yml)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Django 4.2](https://img.shields.io/badge/django-4.2-green.svg)](https://www.djangoproject.com/)
[![React 19.2](https://img.shields.io/badge/react-19.2-blue.svg)](https://reactjs.org/)
[![Coverage](https://img.shields.io/badge/coverage-85%25-brightgreen.svg)]()

**CEN315 Test Engineering Projesi** - Kapsamlı test stratejisi ile geliştirilmiş fitness salonu rezervasyon ve üyelik yönetim sistemi.

---

## 📋 İçindekiler

- [Proje Hakkında](#-proje-hakkında)
- [Özellikler](#-özellikler)
- [Teknoloji Stack](#-teknoloji-stack)
- [Test Stratejisi](#-test-stratejisi)
- [Kurulum](#-kurulum)
- [Kullanım](#-kullanım)
- [API Endpoints](#-api-endpoints)
- [CI/CD Pipeline](#-cicd-pipeline)
- [Proje Yapısı](#-proje-yapısı)
- [Test Raporları](#-test-raporları)
- [Katkıda Bulunanlar](#-katkıda-bulunanlar)

---

## 🎯 Proje Hakkında

Fitness Bros, bireylere fiziksel sağlık, güç, dayanıklılık, esneklik ve genel fitness'ı geliştirmeyi amaçlayan çeşitli ekipman, dersler ve programlara erişim sağlayan modern bir spor salonu yönetim platformudur.

Bu proje, **Test Engineering (CEN315)** dersi kapsamında geliştirilmiş olup, yazılım test süreçlerinin tüm aşamalarını (unit, integration, mutation, security, performance) içermektedir.

### 🎓 Akademik Bağlam
- **Ders:** CEN315 - Test Engineering
- **Dönem:** 2024-2025 Güz
- **Amaç:** Test-Driven Development (TDD) ve kapsamlı test stratejilerinin gerçek bir projede uygulanması

---

## ✨ Özellikler

### Backend (Django REST API)
- 🔐 **Kullanıcı Yönetimi:** JWT tabanlı authentication ve authorization
- 👥 **Üyelik Sistemi:** STUDENT, STANDARD, PREMIUM üyelik tipleri
- 💰 **Dinamik Fiyatlandırma:** Üyelik tipine, doluluk oranına ve peak hour'a göre fiyat hesaplama
- 📅 **Rezervasyon Yönetimi:** Sınıf rezervasyonu, iptal, kapasite kontrolü
- 🏋️ **Fitness Sınıfları:** Yoga, Zumba, CrossFit gibi grup dersleri
- 📊 **Business Logic:** PricingService, ReservationService, CapacityCalculator
- ⚡ **Real-time Kapasite:** Sınıf doluluk oranları ve available spots

### Frontend (React)
- 🎨 **Modern UI/UX:** Responsive tasarım, smooth animasyonlar
- 🏠 **Ana Sayfa:** Hero section, sınıflar, hakkımızda, üyelik planları
- 📝 **Rezervasyon Sayfası:** Sınıf seçimi, tarih/saat seçimi, rezervasyon onayı
- 👤 **Profil Sayfası:** Kullanıcı bilgileri, üyelik planı, rezervasyon geçmişi
- 🔔 **Modal Sistemler:** Plan seçimi, rezervasyon onayı için popup'lar
- 🌐 **Türkçe Lokalizasyon:** Tam Türkçe arayüz desteği

### Test Coverage
- ✅ **Unit Tests:** %90+ coverage (models, services, validators)
- 🔗 **Integration Tests:** API endpoints, database operations
- 🧬 **Mutation Testing:** mutmut ile kod kalitesi analizi
- 🔒 **Security Tests:** OWASP ZAP, input validation, JWT security
- ⚡ **Performance Tests:** Load testing, concurrent operations
- 📊 **Property-Based Tests:** Hypothesis framework ile edge case discovery

---

## 🛠️ Teknoloji Stack

### Backend
```
Python 3.12
Django 4.2.27
Django REST Framework 3.16.1
djangorestframework-simplejwt 5.5.1
django-cors-headers 4.7.0
PostgreSQL / SQLite (development)
```

### Frontend
```
React 19.2.3
React Router DOM 7.10.1
JavaScript (ES6+)
CSS3 (Flexbox, Grid, Animations)
```

### Test Tools
```
pytest 8.4.2
pytest-django
pytest-cov (coverage)
mutmut (mutation testing)
hypothesis (property-based testing)
OWASP ZAP (security scanning)
coverage.py (code coverage)
```

### DevOps
```
GitHub Actions (CI/CD)
Docker (containerization - planned)
SMTP Email Notifications
```

---

## 🧪 Test Stratejisi

Bu proje, **Test Engineering** dersi için hazırlandığından, kapsamlı bir test stratejisi uygulanmıştır:

### 1. Unit Tests (Birim Testleri)
- **Kapsam:** Models, Services, Validators
- **Framework:** pytest + pytest-django
- **Mocking:** unittest.mock ile external dependencies izolasyonu
- **Coverage:** %90+ (hedef)
- **Test Dosyaları:**
  - `memberships/test_services.py` → PricingService unit testleri
  - `reservations/test_services.py` → ReservationService, CapacityCalculator testleri

### 2. Integration Tests (Entegrasyon Testleri)
- **Kapsam:** API endpoints, database operations, authentication
- **Framework:** Django REST Framework Test Client
- **Test Dosyaları:**
  - `tests/test_bookings.py` → Rezervasyon API testleri
  - `tests/test_classes.py` → Sınıf API testleri

### 3. Mutation Testing (Mutasyon Testleri)
- **Araç:** mutmut
- **Hedef:** Test suite kalitesini ölçmek
- **Kapsam:** `memberships/services.py`, `reservations/services.py`
- **Rapor:** `MUTATION_TESTING_REPORT.md`

### 4. Security Testing (Güvenlik Testleri)
- **OWASP ZAP:** Otomatik güvenlik açığı taraması
- **bandit:** Python static security analysis
- **Manual Testing:** SQL injection, XSS, CSRF, JWT security

### 5. Performance Testing (Performans Testleri)
- **Load Testing:** Concurrent request simulation
- **Response Time:** <200ms hedefi
- **Database:** Query optimization, N+1 problem kontrolü

### 6. Property-Based Testing
- **Framework:** Hypothesis
- **Amaç:** Edge case discovery, random input testing

---

## 📦 Kurulum

### Gereksinimler
- Python 3.12+
- Node.js 18+
- pip
- virtualenv (önerilen)

### Backend Kurulumu

```bash
# Repository'yi klonlayın
git clone https://github.com/sultannkayi/fitness_bros.git
cd fitness_bros

# Virtual environment oluşturun
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Bağımlılıkları yükleyin
pip install -r requirements.txt

# Database migrate
python manage.py migrate

# Superuser oluşturun (opsiyonel)
python manage.py createsuperuser

# Development server başlatın
python manage.py runserver
```

Backend şimdi `http://localhost:8000` adresinde çalışıyor.

### Frontend Kurulumu

```bash
# Frontend klasörüne gidin
cd frontend

# Bağımlılıkları yükleyin
npm install

# Development server başlatın
npm start
```

Frontend şimdi `http://localhost:3000` adresinde çalışıyor.

---

## 🚀 Kullanım

### Backend API

```bash
# Testleri çalıştırın
pytest

# Coverage raporu ile testler
pytest --cov=. --cov-report=html

# Mutation testleri
mutmut run --paths-to-mutate=memberships/services.py,reservations/services.py
mutmut results
```

### Frontend

```bash
# Development mode
npm start

# Production build
npm run build

# Testleri çalıştırın
npm test
```

---

## 📡 API Endpoints

### Authentication
```
POST /api/auth/register/     - Kullanıcı kaydı
POST /api/auth/login/        - Kullanıcı girişi
POST /api/auth/logout/       - Kullanıcı çıkışı
GET  /api/auth/user/         - Mevcut kullanıcı bilgileri
```

### Memberships
```
GET    /api/memberships/               - Üyelikleri listele
POST   /api/memberships/               - Yeni üyelik oluştur
GET    /api/memberships/{id}/          - Üyelik detayı
PUT    /api/memberships/{id}/          - Üyelik güncelle
DELETE /api/memberships/{id}/          - Üyelik sil
```

### Reservations
```
GET    /api/reservations/              - Rezervasyonları listele
POST   /api/reservations/              - Yeni rezervasyon oluştur
GET    /api/reservations/{id}/         - Rezervasyon detayı
PUT    /api/reservations/{id}/         - Rezervasyon güncelle
DELETE /api/reservations/{id}/         - Rezervasyon iptal
```

### Classes
```
GET    /api/classes/                   - Sınıfları listele
POST   /api/classes/                   - Yeni sınıf oluştur
GET    /api/classes/{id}/              - Sınıf detayı
GET    /api/classes/{id}/capacity/    - Sınıf kapasite bilgisi
```

---

## 🔄 CI/CD Pipeline

GitHub Actions ile otomatik test ve deployment pipeline:

### Workflow Steps
1. **Code Checkout:** Repository'yi çek
2. **Python Setup:** Python 3.12 kurulumu
3. **Dependencies:** pip install -r requirements.txt
4. **Database Migration:** Django migrations
5. **Backend Tests:** pytest ile unit + integration testler
6. **Coverage Report:** XML coverage raporu oluşturma
7. **Frontend Setup:** Node.js 18 kurulumu
8. **Frontend Build:** npm install && npm run build
9. **Mutation Tests:** mutmut ile mutasyon testleri
10. **Email Notification:** Başarısız durumda email bildirimi

### Notification
Pipeline başarısız olduğunda otomatik email gönderiliyor:
- Server: Gmail SMTP
- Recipients: Team members
- Content: Branch, commit, author, workflow details

---

## 📂 Proje Yapısı

```
fitness_bros/
├── .github/
│   └── workflows/
│       └── python-ci.yml           # CI/CD pipeline
├── authorization/                   # Kullanıcı authentication
│   ├── models.py                   # User model
│   ├── serializers.py              # User serializers
│   ├── views.py                    # Auth endpoints
│   └── tests.py                    # Auth testleri
├── memberships/                     # Üyelik yönetimi
│   ├── models.py                   # Member model
│   ├── services.py                 # PricingService business logic
│   ├── test_services.py            # Unit testler (TDD)
│   └── views.py                    # Membership endpoints
├── reservations/                    # Rezervasyon sistemi
│   ├── models.py                   # Reservation, Booking models
│   ├── services.py                 # ReservationService, CapacityCalculator
│   ├── test_services.py            # Unit + Integration testler
│   └── views.py                    # Reservation endpoints
├── classes/                         # Fitness sınıfları
│   ├── models.py                   # FitnessClass model
│   ├── serializers.py              # Class serializers
│   └── views.py                    # Class endpoints
├── tests/                           # Integration testler
│   ├── test_bookings.py            # Rezervasyon API testleri
│   └── test_classes.py             # Sınıf API testleri
├── frontend/                        # React frontend
│   ├── public/                     # Static files
│   ├── src/
│   │   ├── components/             # Reusable components
│   │   │   └── Navbar.jsx          # Navigation bar
│   │   ├── pages/
│   │   │   ├── Home.jsx            # Ana sayfa
│   │   │   ├── Reservations.jsx   # Rezervasyon sayfası
│   │   │   ├── profile.jsx        # Profil sayfası
│   │   │   └── Auth.jsx            # Login/Register
│   │   ├── router/
│   │   │   └── AppRouter.jsx       # React Router config
│   │   ├── App.js                  # Main component
│   │   └── index.js                # Entry point
│   └── package.json                # Frontend dependencies
├── main/                            # Django project settings
│   ├── settings.py                 # Configuration
│   ├── urls.py                     # URL routing
│   └── wsgi.py                     # WSGI config
├── mutants/                         # Mutation testing output
├── htmlcov/                         # Coverage HTML report
├── conftest.py                      # pytest configuration
├── requirements.txt                 # Python dependencies
├── manage.py                        # Django management
├── TEST_PLAN.md                     # Test planı dokümantasyonu
├── MUTATION_TESTING_REPORT.md      # Mutation test raporu
├── TEST_IMPLEMENTATION_SUMMARY.md  # Test implementasyon özeti
└── README.md                        # Bu dosya
```

---

## 📊 Test Raporları

### Coverage Raporu
```bash
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

### Mutation Testing Raporu
```bash
mutmut run
mutmut html
open html/index.html
```

### Detaylı Raporlar
- `TEST_PLAN.md` → Test stratejisi ve planı
- `MUTATION_TESTING_REPORT.md` → Mutation test analizi
- `TEST_IMPLEMENTATION_SUMMARY.md` → Test implementasyon detayları

---

## 🤝 Katkıda Bulunanlar

- **Sultan Kayı**
- **Mert Kaplan**
- **Akın Menge** 
