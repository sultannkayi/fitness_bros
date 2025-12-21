# Fitness Bros Test Planı ve Stratejisi

**Proje Adı:** Fitness Bros - Spor Salonu Yönetim Sistemi  
**Dokümantasyon Versiyonu:** 1.0  
**Hazırlanma Tarihi:** 15 Aralık 2025  
**Sorumlu:** Test Engineering Team  

---

## 📋 İçindekiler

1. [Proje Özeti](#proje-özeti)
2. [Test Seviyeleri](#test-seviyeleri)
3. [Kullanılacak Araçlar](#kullanılacak-araçlar)
4. [Hedeflenen Coverage Oranları](#hedeflenen-coverage-oranları)
5. [Test Kategorileri](#test-kategorileri)
6. [Test Execution Strategy](#test-execution-strategy)

---

## 🎯 Proje Özeti

Fitness Bros, spor salonu rezervasyon ve üyelik yönetim sistemidir. Dinamik fiyatlandırma, kapasite kontrolü ve rezervasyon yönetimi gibi kritik business logic içermektedir. Bu test planı, sistemin tüm katmanlarının kapsamlı şekilde test edilmesini sağlamak için hazırlanmıştır.

---

## 🧪 1. Uygulanacak Test Seviyeleri

### 1.1 Unit Tests (Birim Testleri)

**Amaç:** Sistemin en küçük bileşenlerini izole ederek test etmek.

**Kapsam:**
- **Models:** User, Member, FitnessClass, Reservation, Booking model validasyonları
- **Services (Business Logic):**
  - `PricingService` → Üyelik fiyat hesaplama, indirim mantığı, kupon uygulaması
  - `ReservationService` → Rezervasyon doğrulama, iptal işlemleri, çakışma kontrolü
  - `CapacityCalculator` → Kapasite kontrol algoritmaları, doluluk oranı hesaplama
- **Validators:** Email format, password güçlülük, kapasite sınırları
- **Utilities:** Date/time işlemleri, format dönüşümleri, helper functions

**Yaklaşım:** Test-Driven Development (TDD) ve mocking kullanarak external dependencies'den bağımsız testler.

### 1.2 Integration Tests (Entegrasyon Testleri)

**Amaç:** Farklı modüllerin birlikte çalışmasını test etmek.

**Kapsam:**
- **API Endpoints:** REST API uçlarının doğru çalışması (GET, POST, PUT, DELETE)
- **Database:** Model ilişkileri, foreign key constraints, cascade operations
- **Authentication:** JWT token oluşturma ve doğrulama akışı
- **Service Integration:** Servisler arası veri akışı ve bağımlılıklar
- **Cross-App Integration:** Authorization ↔ Memberships ↔ Reservations ↔ Classes

**Yaklaşım:** Django TestCase ile transaction rollback, test database kullanımı.

### 1.3 System Tests (Sistem Testleri)

**Amaç:** Sistemin tamamının uçtan uca çalışmasını test etmek.

**Kapsam:**
- **End-to-End Flows:** Kullanıcı kayıttan rezervasyona tam akış
- **API Contract Testing:** OpenAPI specification uyumluluğu
- **Cross-browser Testing:** Web arayüzü uyumluluğu (React frontend - gelecek)
- **Mobile Responsiveness:** Farklı ekran boyutlarında kullanılabilirlik

**Yaklaşım:** REST Framework Test Client ile simüle edilmiş gerçek kullanıcı senaryoları.

### 1.4 Performance Tests (Performans Testleri)

**Amaç:** Sistem performansını ve ölçeklenebilirliğini değerlendirmek.

**Kapsam:**
- **Load Testing:** Yoğun kullanıcı altında response time (hedef: <200ms)
- **Stress Testing:** Sistem limitleri ve bottleneck tespiti
- **Database Performance:** Query optimization doğrulama, N+1 problem kontrolü
- **Concurrent Operations:** Eşzamanlı rezervasyon işlemlerinde consistency

**Yaklaşım:** Django test client timing + JMeter/k6 (production-like ortamda).

### 1.5 Security Tests (Güvenlik Testleri)

**Amaç:** Sistemin güvenlik açıklarını tespit etmek ve önlemek.

**Kapsam:**
- **Authentication Security:** Login/logout güvenlik testleri, brute force koruması
- **Authorization:** Yetki kontrolü testleri, privilege escalation önleme
- **Input Validation:** SQL injection, XSS, CSRF koruması
- **OWASP ZAP Scanning:** Otomatik güvenlik açığı taraması
- **Token Security:** JWT expiration, refresh token güvenliği

**Yaklaşım:** OWASP ZAP + bandit static analysis + manual security testing.

---

## 🛠️ 2. Kullanılacak Araçlar

### 2.1 Unit Test Framework
- **pytest (v8.4.2):** Ana test framework'ü
  - Parametrize testler için `@pytest.mark.parametrize`
  - Fixture system ile test data yönetimi
- **Django TestCase:** Django-specific test utilities
  - Database transaction management
  - Test client ile API testing

### 2.2 Coverage Analysis
- **coverage.py (v7.10.7):** Line ve branch coverage ölçümü
  - `coverage run --branch` ile branch coverage
  - `coverage html` ile görsel raporlar
- **Hedef Oranlar:**
  - Line Coverage > 80%
  - Branch Coverage > 70%
  - Critical modules > 90%

### 2.3 Mocking ve Isolation
- **unittest.mock:** Python standard library
  - `@patch` decorator ile dependency injection
  - `MagicMock` ile complex object mocking
- **pytest-mock:** Pytest integration
- **Mock edilecek bağımlılıklar:**
  - Database queries (test isolation için)
  - Email service (SMTP bağımlılığı kaldırma)
  - Payment gateway (external API simülasyonu)
  - Timezone/datetime (test consistency için)

### 2.4 API Testing
- **Django REST Framework Test Client:** API endpoint testleri
  - `APIClient()` ile authenticated requests
  - Response validation
- **Postman + Newman (opsiyonel):** Contract testing ve CI/CD integration

### 2.5 Mutation Testing
- **mutmut (v3.3.1):** Test kalitesi ölçümü
  - Kod mutasyonları oluşturma
  - Test suite güçlülük analizi
  - Survived mutant detection

### 2.6 Performance Testing
- **Django test client timing:** Response time ölçümü
- **django-silk (opsiyonel):** SQL query profiling
- **JMeter/k6 (gelecek):** Load testing ve stress testing

### 2.7 Security Testing
- **OWASP ZAP:** Automated security testing
  - SQL injection detection
  - XSS vulnerability scanning
  - Authentication bypass attempts
- **bandit:** Python security linting
  - Static code analysis
  - Security anti-pattern detection

---

## 📊 3. Hedeflenen Coverage Oranları

### 3.1 Line Coverage Hedefleri

| Modül Kategorisi | Hedef Coverage | Öncelik |
|------------------|----------------|---------|
| **Critical Modules** (services, business logic) | > 90% | P0 |
| **Models** (validation, constraints) | > 85% | P0 |
| **API Views** (endpoints) | > 85% | P1 |
| **Utility Functions** | > 80% | P1 |
| **Configuration Files** (settings, urls) | > 60% | P2 |
| **Overall Project** | > 80% | P0 |

### 3.2 Branch Coverage Hedefleri

| Kod Tipi | Hedef Coverage | Açıklama |
|----------|----------------|----------|
| **Business Logic** | > 75% | Tüm if-else-elif dalları |
| **Error Handling** | > 70% | try-except blokları |
| **Input Validation** | > 80% | Guard clauses |
| **Overall Project** | > 70% | Genel branch coverage |

### 3.3 Mutation Test Score
- **Hedef Mutation Score:** > 75%
- **Killed mutants:** > 75%
- **Survived mutants:** < 25% (analiz ve improvement için)

---

## 🧪 4. Test Kategorileri

### 4.1 Happy Path Tests (Normal Akış Testleri)
✅ Normal kullanıcı kayıt akışı  
✅ Başarılı login işlemi  
✅ Sınıf rezervasyonu oluşturma  
✅ Üyelik satın alma  
✅ Kapasite içinde rezervasyon  
✅ Fiyat hesaplama (standart senaryolar)

### 4.2 Edge Cases (Sınır Değer Testleri)
🔍 Boundary value testing:
  - Kapasite = 0
  - Kapasite = maximum
  - Son kalan yer rezervasyonu
🔍 Null/empty input handling:
  - Boş string, None, undefined değerler
🔍 Unicode ve özel karakter desteği:
  - Emoji, çoklu dil karakterleri
🔍 Timezone edge cases:
  - Gece yarısı geçişleri
  - Yaz-kış saati değişimi
🔍 Concurrent reservation attempts:
  - Race condition testleri
  - Optimistic locking

### 4.3 Error Scenarios (Hata Senaryoları)
❌ Authentication failures:
  - Yanlış şifre
  - Expired token
  - Invalid credentials
❌ Authorization denials:
  - Insufficient permissions
  - Unauthorized access attempts
❌ Database constraint violations:
  - Unique constraint
  - Foreign key violations
  - Integrity errors
❌ Network timeout simulations (mocked):
  - API timeouts
  - Database connection errors
❌ Invalid input validation errors:
  - Format hataları
  - Type mismatches
❌ Capacity overflow scenarios:
  - Overbooking attempts
  - Double booking prevention
❌ Payment processing failures (mocked):
  - Declined card
  - Insufficient funds

### 4.4 Performance Scenarios
⚡ High concurrency load:
  - 100+ simultaneous users
⚡ Large dataset operations:
  - 10,000+ reservations query
⚡ Memory usage optimization:
  - Memory leak detection
⚡ Database query performance:
  - N+1 query problem check
  - Index effectiveness

---

## 🚀 5. Test Execution Strategy

### 5.1 Development Phase
```bash
# Her commit öncesi:
pytest -x --ff  # Fast fail, run failed tests first

# Her PR öncesi:
pytest --cov=. --cov-report=html
coverage report --fail-under=80
```

**Kriterleri:**
- Tüm testler pass olmalı
- Coverage < 80% ise PR reddedilir
- Linting errors olmamalı

### 5.2 CI/CD Pipeline

**GitHub Actions Workflow:**
```yaml
1. Pre-commit hooks:
   - black (code formatting)
   - flake8 (linting)
   - isort (import sorting)

2. PR Review Stage:
   - Full test suite
   - Coverage report (>80%)
   - Mutation testing
   - Security scan (bandit)

3. Staging Deployment:
   - Integration tests
   - System tests
   - Performance benchmarks

4. Production Deployment:
   - Health checks
   - Smoke tests
   - Rollback capability
```

### 5.3 Mutation Testing Schedule
- **Haftalık:** Mutation testing çalıştırılır
- **Survived mutant analizi:** Test gaps belirlenir
- **Test iyileştirme:** Eksik test coverage kapatılır

### 5.4 Test Data Management
- **Fixtures:** pytest fixtures ile reusable test data
- **Factory pattern:** Model factory'leri ile dynamic test data
- **Database seeding:** Realistic test scenarios için seed data

---

## 📈 6. Test Metrics ve Monitoring

### 6.1 Takip Edilecek Metrikler

**Coverage Metrics:**
- Line coverage percentage
- Branch coverage percentage
- Function coverage percentage
- Missing lines raporu

**Quality Metrics:**
- Test execution time (<2 minutes hedef)
- Test failure rate (<5% hedef)
- Mutation test score (>75% hedef)
- Code complexity vs test coverage korelasyonu

**Performance Metrics:**
- Average API response time
- Database query count per endpoint
- Memory usage per test suite
- Test suite parallelization efficiency

### 6.2 Success Criteria

✅ All tests pass (100% pass rate)  
✅ Line coverage > 80%, Branch coverage > 70%  
✅ Mutation score > 75%  
✅ No high-severity security issues (bandit, OWASP ZAP)  
✅ Performance benchmarks met (<200ms response time)  
✅ No flaky tests (test stability >99%)

---

## 📋 7. Risk Assessment ve Mitigation

### 7.1 High Risk Areas

| Risk Alanı | Risk Seviyesi | Mitigation Stratejisi |
|------------|---------------|----------------------|
| **Payment Processing** | 🔴 Kritik | Extra test coverage, manual testing, staging tests |
| **Authentication/Authorization** | 🔴 Kritik | Security-focused tests, penetration testing |
| **Capacity Management** | ⚠️ Yüksek | Race condition tests, stress testing |
| **Data Migration** | ⚠️ Yüksek | Backup strategy, rollback tests |
| **Dynamic Pricing** | ⚠️ Yüksek | Extensive unit tests, decision table testing |

### 7.2 Mitigation Strategies

**Critical Paths:**
- Minimum 90% test coverage
- Peer review zorunlu
- Production monitoring

**Payment Flows:**
- Mocked tests + staging environment tests
- Financial transaction audit logs
- Rollback mechanism

**Security:**
- Weekly security scans
- Dependency vulnerability checks (Snyk, Dependabot)
- Security training for team

---

## 📅 Test Plan Review Schedule

- **Weekly:** Test metrics review, flaky test fixing
- **Sprint sonunda:** Coverage gaps analizi, test plan update
- **Monthly:** Mutation testing full run, security assessment
- **Quarterly:** Test strategy review, tool evaluation

---

## 📞 İletişim ve Sorumluluklar

**Test Lead:** Test Engineering Team  
**Sorumlu Geliştiriciler:** Backend Team  
**Security Consultant:** Security Team (external)  

**Raporlama:**
- Test coverage raporları: Her PR
- Mutation testing raporları: Haftalık
- Security scan raporları: Aylık
- Performance benchmark raporları: Her release

---

**Döküman Sonu**  
**Son Güncelleme:** 15 Aralık 2025  
**Versiyon:** 1.0  
**Durum:** ✅ Aktif
