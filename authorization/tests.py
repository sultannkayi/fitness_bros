from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

class AuthSystemTests(TestCase):
    #Assert
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
        self.login_url = '/api/auth/login/'
        self.user_data = {
            'email': 'test@fitnessbros.com',
            'password': 'strongpassword123',
            'first_name': 'Test',
            'last_name': 'User'
        }

    def test_create_user_model(self):

        User = get_user_model()
        user = User.objects.create_user(
            email='modeltest@test.com',
            password='pass',
            is_instructor=False
        )
        self.assertEqual(user.email, 'modeltest@test.com')
        self.assertTrue(user.check_password('pass'))
        self.assertFalse(user.is_instructor)

    def test_register_api(self):
       
        response = self.client.post(self.register_url, self.user_data)
        
        # Henüz endpoint'i yazmadığımız için bu test 404 verecek (RED)
        # Ama biz 201 Created bekliyoruz.
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data) # Başarılı kayıtta token dönmeli
        self.assertIn('user', response.data)

    def test_login_api(self):
        """3. API Testi: Login endpoint'i çalışıyor mu?"""
        # Önce kullanıcıyı oluştur
        User = get_user_model()
        User.objects.create_user(**self.user_data)

        # Login yapmayı dene
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        response = self.client.post(self.login_url, login_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data) # JWT access token