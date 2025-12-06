from django.test import TestCase
from django.contrib.auth import get_user_model
# Hata alacağımızı bile bile import ediyoruz (Çünkü henüz model yok)
# TDD'de buna "Compilation Error" aşaması denir.
from .models import Member 

User = get_user_model()

class MemberModelTests(TestCase):
    
    def test_member_profile_created_automatically(self):
        """a
        SENARYO: Yeni bir User (auth app) kaydedildiğinde, 
        sistem otomatik olarak ona bağlı bir Member (memberships app) profili oluşturmalı.
        Bu test, 'Signal' yapısının çalışıp çalışmadığını denetler.
        """
        # 1. Kullanıcıyı oluştur
        user = User.objects.create_user(
            email="newmember@fitness.com", 
            password="pass"
        )
        
        # 2. Member profili oluşmuş mu kontrol et
        # Eğer signal yazmazsak burası patlar (DoesNotExist veya AttributeError verir)
        self.assertTrue(hasattr(user, 'member'), "Kullanıcı oluşturuldu ama Member profili otomatik oluşmadı!")
        self.assertIsInstance(user.member, Member)
        
        # Varsayılan üyelik tipi 'STANDARD' olmalı
        self.assertEqual(user.member.membership_type, 'STANDARD')

    def test_update_membership_type(self):
        """
        SENARYO: Kullanıcının üyelik tipi 'STUDENT' veya 'PREMIUM' olarak değiştirilebilmeli.
        Fiyatlandırma motoru bu alanı kullanacak.
        """
        user = User.objects.create_user(email="student@fitness.com", password="pass")
        
        # Member profili signal ile oluşmuş olmalı
        member_profile = user.member
        
        # Değişiklik yap
        member_profile.membership_type = 'STUDENT'
        member_profile.save()
        
        # Veritabanından tazeleyip kontrol et
        updated_member = Member.objects.get(user=user)
        self.assertEqual(updated_member.membership_type, 'STUDENT')