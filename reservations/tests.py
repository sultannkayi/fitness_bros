import pytest
import json
from datetime import timedelta
from unittest.mock import patch
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from rest_framework.test import APIClient
from rest_framework import status

# Diğer uygulamalardan modelleri çağırıyoruz (Cross-App Integration)
from classes.models import FitnessClass
from memberships.models import Member

# HENÜZ OLMAYAN (TDD) Modül ve Servisleri çağırıyoruz
from .models import Reservation
from .services import PricingEngine

User = get_user_model()

@pytest.mark.django_db
class PricingEngineUnitTests(TestCase):
    """
    BÖLÜM 1: MANTIK TESTLERİ (UNIT TEST)
    Veritabanına gitmeden, sadece fiyat hesaplama algoritmasını (Business Logic) test eder.
    PDF Madde 4.4 ve 5.5 (Decision Tables) gereksinimlerini karşılar.
    """

    def setUp(self):
        self.base_price = Decimal('100.00')

    def test_standard_member_low_occupancy(self):
        """Senaryo 1: Standart üye + Boş sınıf = Taban Fiyat"""
        calculated_price = PricingEngine.calculate_price(
            base_price=self.base_price,
            membership_type='STANDARD',
            occupancy_rate=0.10,  # %10 dolu
            is_peak_hour=False
        )
        self.assertEqual(calculated_price, Decimal('100.00'))

    def test_premium_member_discount(self):
        """Senaryo 2: Premium üye her zaman %20 indirim alır"""
        calculated_price = PricingEngine.calculate_price(
            base_price=self.base_price,
            membership_type='PREMIUM',
            occupancy_rate=0.10,
            is_peak_hour=False
        )
        # 100 * 0.80 = 80
        self.assertEqual(calculated_price, Decimal('80.00'))

    def test_surge_pricing_high_occupancy(self):
        """Senaryo 3: Doluluk %80'in üzerindeyse %50 zam (Surge Pricing)"""
        calculated_price = PricingEngine.calculate_price(
            base_price=self.base_price,
            membership_type='STANDARD',
            occupancy_rate=0.85,  # %85 dolu (Kritik Eşik)
            is_peak_hour=False
        )
        # 100 * 1.50 = 150
        self.assertEqual(calculated_price, Decimal('150.00'))

    def test_peak_hour_pricing(self):
        """Senaryo 4: Yoğun saatlerde (Peak Hour) taban fiyata %25 zam gelir"""
        calculated_price = PricingEngine.calculate_price(
            base_price=self.base_price,
            membership_type='STANDARD',
            occupancy_rate=0.50,
            is_peak_hour=True  # Yoğun saat
        )
        # 100 * 1.25 = 125
        self.assertEqual(calculated_price, Decimal('125.00'))

    def test_complex_scenario_student_and_surge(self):
        """
        Senaryo 5 (Kombinatoryal): Öğrenci (%50 indirim) + Çok Dolu (%50 zam).
        Matematik: 100 * 0.5 (Öğrenci) = 50. Sonra 50 * 1.5 (Surge) = 75.
        (Sıralama iş mantığında belirlenecek, test bunu sabitler)
        """
        calculated_price = PricingEngine.calculate_price(
            base_price=self.base_price,
            membership_type='STUDENT',
            occupancy_rate=0.90,
            is_peak_hour=False
        )
        self.assertEqual(calculated_price, Decimal('75.00'))


@pytest.mark.django_db
class ReservationModelTests(TestCase):
    """
    BÖLÜM 2: MODEL VE DATABASE TESTLERİ (INTEGRATION)
    Kapasite kontrolü, mükerrer kayıt engelleme gibi veritabanı kısıtlarını test eder.
    PDF Madde 4.3 (Capacity Control)
    """

    def setUp(self):
        # 1. Eğitmen
        self.instructor = User.objects.create_user(email="coach@fit.com", password="pass", is_instructor=True)
        
        # 2. Ders (Kapasite: 2 kişi - Sınır testi için küçük verdik)
        self.future_time = timezone.now() + timedelta(days=1)
        self.fitness_class = FitnessClass.objects.create(
            name="Tiny Yoga Class",
            instructor=self.instructor,
            capacity=2,
            date_time=self.future_time,
            base_price=Decimal('100.00')
        )

        # 3. İki farklı üye
        self.user1 = User.objects.create_user(email="user1@fit.com", password="pass")
        self.user2 = User.objects.create_user(email="user2@fit.com", password="pass")
        self.user3 = User.objects.create_user(email="user3@fit.com", password="pass")

    def test_capacity_enforcement(self):
        """
        KRİTİK TEST: Kapasite dolduğunda 3. kişi rezervasyon yapamamalı.
        """
        # 1. Kişi Rezervasyonu
        Reservation.objects.create(member=self.user1.member, fitness_class=self.fitness_class)
        
        # 2. Kişi Rezervasyonu (Kapasite Doldu)
        Reservation.objects.create(member=self.user2.member, fitness_class=self.fitness_class)
        
        # 3. Kişi Denemesi -> HATA VERMELİ (ValidationError)
        with self.assertRaises(ValidationError):
            res = Reservation(member=self.user3.member, fitness_class=self.fitness_class)
            res.full_clean() # Model validasyonunu tetikle
            res.save()

    def test_prevent_double_booking(self):
        """
        Senaryo: Aynı kullanıcı aynı derse iki kere rezervasyon yapamaz.
        """
        # İlk kayıt başarılı
        Reservation.objects.create(member=self.user1.member, fitness_class=self.fitness_class)
        
        # İkinci kayıt denemesi -> IntegrityError (UniqueConstraint)
        with self.assertRaises(IntegrityError):
            Reservation.objects.create(member=self.user1.member, fitness_class=self.fitness_class)

    def test_price_is_frozen_at_booking(self):
        """
        Senaryo: Rezervasyon anındaki fiyat veritabanına kaydedilmeli.
        Sonradan ders fiyatı değişse bile, kullanıcının ödediği (price_paid) değişmemeli.
        """
        # Fiyatı hesapla ve kaydet
        res = Reservation.objects.create(
            member=self.user1.member, 
            fitness_class=self.fitness_class,
            price_paid=Decimal('90.00')
        )
        
        # Dersin fiyatını güncelle
        self.fitness_class.base_price = Decimal('500.00')
        self.fitness_class.save()
        
        # Rezervasyondaki fiyat hala 90 olmalı
        res.refresh_from_db()
        self.assertEqual(res.price_paid, Decimal('90.00'))


@pytest.mark.django_db
class ReservationAPITests(TestCase):
    """
    BÖLÜM 3: END-TO-END API TESTLERİ
    Kullanıcı arayüzünden (React/Postman) gelen istekleri simüle eder.
    PDF Madde 5.4 (Integration and API Testing)
    """

    def setUp(self):
        self.client = APIClient()
        
        # Premium Üye Oluştur
        self.user = User.objects.create_user(email="richie@fit.com", password="pass")
        self.user.member.membership_type = 'PREMIUM'
        self.user.member.save()
        
        # Token al ve giriş yap
        self.client.force_authenticate(user=self.user)
        
        # Ders oluştur
        self.instructor = User.objects.create_user(email="coach@fit.com", password="pass", is_instructor=True)
        self.fitness_class = FitnessClass.objects.create(
            name="Spinning",
            instructor=self.instructor,
            capacity=20,
            date_time=timezone.now() + timedelta(days=2),
            base_price=Decimal('100.00')
        )
        
        self.list_url = '/api/reservations/'
        self.detail_url = lambda id: f'/api/reservations/{id}/'

    def test_create_reservation_end_to_end(self):
        """
        E2E: Kullanıcı derse ID ile istek atar, sistem fiyatı hesaplar ve kaydeder.
        """
        payload = {
            'fitness_class_id': self.fitness_class.id
        }
        
        # POST isteği at
        response = self.client.post(self.list_url, payload)
        
        # 1. Status 201 Created mi?
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 2. Veritabanında oluştu mu?
        self.assertTrue(Reservation.objects.filter(member=self.user.member).exists())
        
        # 3. Dinamik Fiyat Doğru Hesaplandı mı?
        # Premium üye (%20 indirim) -> 100 TL yerine 80 TL ödemeli
        reservation = Reservation.objects.get(member=self.user.member)
        self.assertEqual(reservation.price_paid, Decimal('80.00'))

    def test_cancel_reservation(self):
        """
        E2E: Rezervasyon iptal (DELETE) testi.
        """
        # Önce bir rezervasyon oluştur
        reservation = Reservation.objects.create(
            member=self.user.member, 
            fitness_class=self.fitness_class,
            price_paid=Decimal('100.00')
        )
        
        # Silme isteği gönder
        response = self.client.delete(self.detail_url(reservation.id))
        
        # 204 No Content dönmeli
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Veritabanından silinmiş olmalı (veya status=CANCELLED olmalı, tasarıma göre)
        # Bizim tasarımda siliyoruz:
        self.assertFalse(Reservation.objects.filter(id=reservation.id).exists())

    def test_cannot_reserve_full_class_api(self):
        """
        E2E: Dolu derse API üzerinden istek atılırsa 400 Bad Request dönmeli.
        """
        # Dersi dolduralım (Kapasiteyi 0 yap hileyle)
        self.fitness_class.capacity = 0
        self.fitness_class.save()
        
        payload = {'fitness_class_id': self.fitness_class.id}
        response = self.client.post(self.list_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("full", str(response.data).lower())