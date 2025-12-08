import logging
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
# TDD: Henüz oluşturmadığımız ama testini yazdığımız Member modelini çağırıyoruz
from .models import Member

# Loglama ayarları: Konsola çıktı vermek için basit bir yapılandırma
logger = logging.getLogger(__name__)

User = get_user_model()

class MemberModelTests(TestCase):
    
    def setUp(self):
        """Her testten önce çalışır: Temiz ortam ve kullanıcı hazırlığı."""
        print("\n----------------------------------------------------------------------")
        print(f"--> TEST BAŞLIYOR: {self._testMethodName}")
        
        self.user_email = "testmember@fitness.com"
        self.user_pass = "securepass123"
        
        # Kullanıcı oluşturuyoruz (Signal burada tetiklenmeli)
        self.user = User.objects.create_user(
            email=self.user_email, 
            password=self.user_pass
        )
        print(f"    Bilgi: Test kullanıcısı oluşturuldu ({self.user_email})")

    def tearDown(self):
        """Her testten sonra çalışır."""
        print(f"--> TEST TAMAMLANDI: {self._testMethodName}")

    def test_signal_triggering_and_auto_create(self):
        """Signal mekanizması User oluşunca Member profilini de oluşturuyor mu?"""
        print("    Adım: Member profilinin varlığı kontrol ediliyor...")
        
        if hasattr(self.user, 'member'):
            print("    BAŞARILI: User objesinde 'member' özelliği bulundu.")
        else:
            print("    HATA: User objesinde 'member' özelliği YOK!")

        self.assertTrue(hasattr(self.user, 'member'), "HATA: Member profili otomatik oluşmadı!")
        self.assertIsInstance(self.user.member, Member)
        self.assertEqual(self.user.member.membership_type, 'STANDARD')
        print("    BAŞARILI: Varsayılan üyelik tipi 'STANDARD' olarak doğrulandı.")

    def test_cascade_delete(self):
        """User silinince Member profili de siliniyor mu?"""
        user_id = self.user.id
        print(f"    Adım: Kullanıcı (ID: {user_id}) siliniyor...")
        
        self.user.delete()
        
        print("    Adım: Member profilinin silindiği doğrulanıyor...")
        with self.assertRaises(Member.DoesNotExist):
            Member.objects.get(user_id=user_id)
        print("    BAŞARILI: Member profili veritabanından temizlenmiş.")

    def test_string_representation(self):
        """__str__ metodu beklenen formatı veriyor mu?"""
        member = self.user.member
        expected = f"{self.user_email} - STANDARD"
        print(f"    Adım: Beklenen çıktı: '{expected}' vs Gerçekleşen: '{str(member)}'")
        
        self.assertEqual(str(member), expected)
        print("    BAŞARILI: String formatı doğru.")

    def test_duplicate_prevention_uniqueness(self):
        """Aynı kullanıcıya ikinci profil eklenmesi engelleniyor mu?"""
        print("    Adım: Mevcut kullanıcıya ikinci bir Member profili eklenmeye çalışılıyor...")
        
        try:
            with self.assertRaises(IntegrityError):
                Member.objects.create(user=self.user, membership_type='PREMIUM')
            print("    BAŞARILI: Sistem ikinci profil oluşturulmasına izin vermedi (IntegrityError yakalandı).")
        except Exception as e:
            print(f"    HATA: Beklenmedik bir durum oluştu: {e}")
            raise e

    def test_default_active_status(self):
        """Yeni üye aktif başlıyor mu?"""
        print(f"    Adım: Üyelik aktiflik durumu: {self.user.member.is_active_member}")
        self.assertTrue(self.user.member.is_active_member)
        print("    BAŞARILI: Üye aktif durumda.")


class MemberIntegrationTests(TestCase):
    
    def setUp(self):
        print("\n----------------------------------------------------------------------")
        print(f"--> ENTEGRASYON TESTİ BAŞLIYOR: {self._testMethodName}")

    def tearDown(self):
        print(f"--> ENTEGRASYON TESTİ BİTTİ: {self._testMethodName}")

    def test_user_and_member_are_tightly_coupled(self):
        """Auth ve Domain modelleri arasındaki sıkı bağı test eder."""
        print("    Adım: Bağımsız bir User oluşturuluyor...")
        user = User.objects.create_user(email="integration@fitness.com", password="pass")
        
        print("    Adım: Otomatik bağ kontrol ediliyor...")
        self.assertTrue(hasattr(user, 'member'), "HATA: Otomatik profil oluşmadı!")
        self.assertIsInstance(user.member, Member)
        self.assertEqual(user.member.membership_type, 'STANDARD')
        print("    BAŞARILI: User ve Member etle tırnak gibi bağlı.")

    def test_delete_user_deletes_member(self):
        """Kök (User) silinince Dal (Member) da silinmeli."""
        print("    Adım: Test kullanıcısı oluşturuluyor...")
        user = User.objects.create_user(email="todelete@fitness.com", password="pass")
        member_id = user.member.id
        
        print("    Adım: Kullanıcı siliniyor...")
        user.delete()
        
        print("    Adım: Öksüz veri kontrolü yapılıyor...")
        with self.assertRaises(Member.DoesNotExist):
            Member.objects.get(id=member_id)
        print("    BAŞARILI: Öksüz veri kalmadı.")

    def test_reverse_access_consistency(self):
        """Member üzerinden User'a erişim."""
        print("    Adım: Member -> User erişimi deneniyor...")
        user = User.objects.create_user(email="reverse@fitness.com", password="pass")
        member = user.member
        
        self.assertEqual(member.user.email, "reverse@fitness.com")
        print(f"    BAŞARILI: Member üzerinden e-mail'e erişildi ({member.user.email}).")