from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

# Henüz oluşturmadığımız Member modelini import ediyoruz (TDD)
from .models import Member

User = get_user_model()


class MemberModelTests(TestCase):

    def setUp(self):
        """
        Her testten önce temiz bir ortam hazırlar.
        Burada oluşturduğumuz kullanıcı, test veritabanında geçici olarak saklanır.
        """
        self.user_email = "testmember@fitness.com"
        self.user_pass = "securepass123"

        # Kullanıcıyı oluşturuyoruz
        # create_user kullandığımız için Signal tetiklenmeli ve Member da oluşmalı
        self.user = User.objects.create_user(
            email=self.user_email,
            password=self.user_pass
        )

    def test_signal_triggering_and_auto_create(self):
        """
        TEST 1: Signal Tetiklenme Kontrolü
        Senaryo: User.objects.create_user() çağrıldığında, 
        arka planda otomatik olarak bir Member profili oluşmalı.
        """
        # Kullanıcının 'member' adında bir ilişkisi var mı?
        self.assertTrue(
            hasattr(self.user, 'member'),
            "HATA: Kullanıcı oluştu ama Member profili otomatik oluşmadı!"
        )

        # Oluşan obje gerçekten Member sınıfından mı?
        self.assertIsInstance(self.user.member, Member)

        # Varsayılan üyelik tipi 'STANDARD' mı?
        self.assertEqual(self.user.member.membership_type, 'STANDARD')

    def test_cascade_delete(self):
        """
        TEST 2: Cascade Delete (Veri Temizliği)
        Senaryo: Ana kullanıcı (User) silindiğinde, 
        ona bağlı olan Member profili de veritabanından silinmeli.
        """
        user_id = self.user.id

        # İlişkili Member profili mevcut mu?
        self.assertTrue(Member.objects.filter(user_id=user_id).exists())

        # Kullanıcıyı sil
        self.user.delete()

        # Member profili artık olmamalı
        with self.assertRaises(Member.DoesNotExist):
            Member.objects.get(user_id=user_id)

    def test_string_representation(self):
        """
        TEST 3: __str__ kontrolü
        Beklenen format: "email - UYELIK_TIPI"
        """
        member = self.user.member
        expected_string = f"{self.user_email} - STANDARD"
        self.assertEqual(str(member), expected_string)

    def test_duplicate_prevention_uniqueness(self):
        """
        TEST 4: Duplicate Prevention (OneToOne koruması)
        Bir kullanıcı için ikinci bir Member profili oluşturulursa hata vermeli.
        """
        with self.assertRaises(IntegrityError):
            Member.objects.create(
                user=self.user,
                membership_type='PREMIUM'
            )

    def test_default_active_status(self):
        """
        TEST 5: Default Value
        Yeni oluşturulan bir üye varsayılan olarak 'Aktif' başlamalı.
        """
        self.assertTrue(self.user.member.is_active_member)
