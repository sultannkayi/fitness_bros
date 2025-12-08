from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
# Henüz olmayan modeli import ediyoruz (Hata alacağız -> RED)
from .models import FitnessClass
from django.contrib.auth import get_user_model
from memberships.models import Member # Diğer app'ten model çağırıyoruz (Cross-App Import)

User = get_user_model()

class FitnessClassModelTests(TestCase):

    def setUp(self):
        # Yarın için bir tarih ayarla
        self.future_date = timezone.now() + timedelta(days=1)

    def test_create_valid_class(self):
        """TEST 1: Geçerli bir ders sorunsuz oluşturulmalı"""
        yoga_class = FitnessClass.objects.create(
            name="Morning Yoga",
            instructor="Yogi Bear",
            capacity=20,
            date_time=self.future_date,
            base_price=100.00
        )
        self.assertEqual(yoga_class.name, "Morning Yoga")
        self.assertEqual(yoga_class.capacity, 20)
        self.assertTrue(yoga_class.is_active)

    def test_capacity_cannot_be_negative_or_zero(self):
        """TEST 2: Kapasite 0 veya negatif olamaz"""
        # Modelde validators kullanacağımız için full_clean() çağırmalıyız
        
        # Senaryo A: 0 Kapasite
        invalid_class = FitnessClass(
            name="Full Class",
            instructor="Test",
            capacity=0,
            date_time=self.future_date,
            base_price=50
        )
        with self.assertRaises(ValidationError):
            invalid_class.full_clean() # Validasyonları tetikler
            invalid_class.save()

    def test_cannot_create_class_in_past(self):
        """TEST 3: Geçmiş tarihe ders açılamaz"""
        yesterday = timezone.now() - timedelta(days=1)
        
        past_class = FitnessClass(
            name="Past Class",
            instructor="Time Traveler",
            capacity=10,
            date_time=yesterday,
            base_price=50
        )
        with self.assertRaises(ValidationError):
            past_class.full_clean()
            past_class.save()

    def test_string_representation(self):
        """TEST 4: __str__ metodu okunabilir olmalı"""
        cls = FitnessClass.objects.create(
            name="Pilates",
            instructor="Jane",
            capacity=10,
            date_time=self.future_date,
            base_price=200
        )
        # Beklenen çıktı formatı: "Pilates - Jane (Yarın Tarihi)"
        expected_str = f"Pilates - Jane ({self.future_date.strftime('%Y-%m-%d %H:%M')})"
        # Tarih formatı locale göre değişebilir, basit kontrol yapalım:
        self.assertIn("Pilates", str(cls))
        self.assertIn("Jane", str(cls))

class ClassIntegrationTests(TestCase):
    """
    Bu test sınıfı, Classes uygulamasının diğer uygulamalarla (Auth ve Memberships)
    olan uyumunu ve ilişkilerini test eder.
    """

    def setUp(self):
        # 1. Bir Eğitmen (User) Oluştur (Auth App)
        self.instructor_user = User.objects.create_user(
            email="coach_mike@fitnessbros.com",
            password="pass",
            is_instructor=True
        )

        # 2. Bir Öğrenci (User + Member) Oluştur (Auth + Memberships App)
        self.student_user = User.objects.create_user(
            email="student_jane@fitnessbros.com",
            password="pass"
        )
        # Signal sayesinde Member profili de oluştu, onu alalım
        self.student_member = self.student_user.member

    def test_class_linked_to_real_instructor_user(self):
        """
        TEST 5: Instructor Bağlantı Testi (Auth <-> Classes)
        Senaryo: 'instructor' alanı sadece bir isim değil, 
        gerçek bir User objesine ForeignKey ile bağlı olmalı.
        """
        # Gelecek tarih
        future_date = timezone.now() + timedelta(days=2)
        
        # Eğitmen User objesini vererek ders oluşturuyoruz
        fitness_class = FitnessClass.objects.create(
            name="Advanced HIIT",
            instructor=self.instructor_user, # DİKKAT: Burada String değil Obje veriyoruz
            capacity=15,
            date_time=future_date,
            base_price=150.00
        )

        # Kontrol 1: Kayıt başarılı mı?
        self.assertEqual(fitness_class.instructor.email, "coach_mike@fitnessbros.com")
        
        # Kontrol 2: İlişki üzerinden yetki kontrolü
        self.assertTrue(fitness_class.instructor.is_instructor)

    def test_system_coexistence(self):
        """
        TEST 6: Ekosistem Testi (Auth + Memberships + Classes)
        Senaryo: Aynı veritabanı oturumunda; bir Hoca, bir Öğrenci ve bir Ders
        sorunsuz bir şekilde var olabilmeli ve verilerine erişilebilmeli.
        (Rezervasyon sistemi kurulmadan önceki 'Zemin Kontrolü')
        """
        # Ders oluştur
        yoga_class = FitnessClass.objects.create(
            name="Sunset Yoga",
            instructor=self.instructor_user,
            capacity=10,
            date_time=timezone.now() + timedelta(days=1),
            base_price=100
        )

        # Senaryo: Öğrenci sisteme girip dersin fiyatına bakıyor
        # (Henüz rezervasyon yapmıyor, sadece görüntüleme simülasyonu)
        
        # Öğrencinin tipi ne?
        student_type = self.student_member.membership_type # Memberships App'ten veri
        
        # Dersin fiyatı ne?
        class_price = yoga_class.base_price # Classes App'ten veri
        
        # Bu değerlerin hepsine aynı anda erişebiliyor olmalıyız
        self.assertEqual(student_type, 'STANDARD')
        self.assertEqual(class_price, 100)
        self.assertTrue(yoga_class.is_active)