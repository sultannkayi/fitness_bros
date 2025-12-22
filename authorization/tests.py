from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.exceptions import ValidationError as DRFValidationError
from .serializers import RegisterSerializer, LoginSerializer
from decimal import Decimal


User = get_user_model()


class UserModelTests(TestCase):
    def test_create_user_with_email(self):
        user = User.objects.create_user(email='test@example.com', password='testpass123')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))

    def test_email_uniqueness_constraint(self):
        User.objects.create_user(email='unique@example.com', password='testpass123')
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                User.objects.create_user(email='unique@example.com', password='differentpass')

    def test_password_is_hashed(self):
        raw_password = 'mysecretpassword'
        user = User.objects.create_user(email='hash@example.com', password=raw_password)
        self.assertNotEqual(user.password, raw_password)
        self.assertTrue(user.check_password(raw_password))

    def test_create_user_without_email_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password='testpass123')

    def test_create_user_with_none_email_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email=None, password='testpass123')

    def test_is_instructor_default_false(self):
        user = User.objects.create_user(email='instructor@example.com', password='testpass123')
        self.assertFalse(user.is_instructor)

    def test_is_active_default_true(self):
        user = User.objects.create_user(email='active@example.com', password='testpass123')
        self.assertTrue(user.is_active)

    def test_is_staff_default_false(self):
        user = User.objects.create_user(email='staff@example.com', password='testpass123')
        self.assertFalse(user.is_staff)

    def test_email_normalization(self):
        user = User.objects.create_user(email='TEST@EXAMPLE.COM', password='testpass123')
        self.assertEqual(user.email, 'TEST@example.com')

    def test_first_name_blank_allowed(self):
        user = User.objects.create_user(email='blank@example.com', password='testpass123', first_name='')
        self.assertEqual(user.first_name, '')

    def test_last_name_blank_allowed(self):
        user = User.objects.create_user(email='blankln@example.com', password='testpass123', last_name='')
        self.assertEqual(user.last_name, '')

    def test_create_superuser(self):
        superuser = User.objects.create_superuser(email='super@example.com', password='superpass123')
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_create_superuser_without_email_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(email='', password='superpass123')

    def test_email_case_insensitive_uniqueness(self):
        """Aynı email farklı büyük/küçük harf ile kaydedilemez"""
        User.objects.create_user(email='case@test.com', password='pass')
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                User.objects.create_user(email='CASE@TEST.COM', password='pass')

    def test_email_field_max_length(self):
        """Email 254 karakter sınırı"""
        long_email = 'a' * 245 + '@example.com'
        user = User.objects.create_user(email=long_email, password='testpass123')
        self.assertEqual(user.email, long_email)

        too_long = 'a' * 246 + '@example.com' 
        with self.assertRaises(Exception):
            User.objects.create_user(email=too_long, password='testpass123')

    def test_user_str_method(self):
        user = User.objects.create_user(email='str@test.com', password='pass', first_name='Ahmet', last_name='Yılmaz')
        self.assertEqual(str(user), 'Ahmet Yılmaz')

        user_no_name = User.objects.create_user(email='noname@test.com', password='pass')
        self.assertEqual(str(user_no_name), 'noname@test.com')

    def test_user_get_full_name(self):
        user = User.objects.create_user(email='full@test.com', password='pass', first_name='Mehmet', last_name='Demir')
        self.assertEqual(user.get_full_name(), 'Mehmet Demir')

        user_only_first = User.objects.create_user(email='onlyfirst@test.com', password='pass', first_name='Ali')
        self.assertEqual(user_only_first.get_full_name(), 'Ali')

        user_no_name = User.objects.create_user(email='noname@test.com', password='pass')
        self.assertEqual(user_no_name.get_full_name(), '')

class RegisterSerializerTests(TestCase):
    def test_password_is_write_only(self):
        data = {'email': 'register@example.com', 'password': 'testpass123', 'first_name': 'Test', 'last_name': 'User'}
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        output = serializer.data
        self.assertNotIn('password', output)

    def test_user_created_in_database(self):
        data = {'email': 'created@example.com', 'password': 'testpass123'}
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertTrue(User.objects.filter(email='created@example.com').exists())

    def test_email_normalization_via_serializer(self):
        data = {'email': 'NORMALIZED@EXAMPLE.COM', 'password': 'testpass123'}
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.email, 'NORMALIZED@example.com')

    def test_missing_email_invalid(self):
        data = {'password': 'testpass123'}
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_missing_password_invalid(self):
        data = {'email': 'nopass@example.com'}
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

    def test_optional_first_and_last_name(self):
        data = {'email': 'optional@example.com', 'password': 'testpass123'}
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.first_name, '')
        self.assertEqual(user.last_name, '')

    def test_invalid_email_format(self):
        data = {'email': 'not-an-email', 'password': 'testpass123'}
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_duplicate_email_validation(self):
        User.objects.create_user(email='duplicate@test.com', password='pass')
        data = {'email': 'duplicate@test.com', 'password': 'testpass123'}
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_gender_field_validation(self):
        data = {'email': 'gender@test.com', 'password': 'testpass123', 'gender': 'Male'}
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        data_invalid = {'email': 'invalidgender@test.com', 'password': 'testpass123', 'gender': 'Invalid'}
        serializer_invalid = RegisterSerializer(data=data_invalid)
        self.assertFalse(serializer_invalid.is_valid())
        self.assertIn('gender', serializer_invalid.errors)

    def test_birth_date_format_validation(self):
        data = {'email': 'date@test.com', 'password': 'testpass123', 'birth_date': '1990-05-15'}
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        data_invalid = {'email': 'baddate@test.com', 'password': 'testpass123', 'birth_date': 'invalid-date'}
        serializer_invalid = RegisterSerializer(data=data_invalid)
        self.assertFalse(serializer_invalid.is_valid())
        self.assertIn('birth_date', serializer_invalid.errors)

    def test_decimal_fields_validation(self):
        data = {'email': 'decimal@test.com', 'password': 'testpass123', 'height': '180.50', 'weight': '75.00'}
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        data_invalid = {'email': 'big@test.com', 'password': 'testpass123', 'height': '99999.99'}
        serializer_invalid = RegisterSerializer(data=data_invalid)
        self.assertFalse(serializer_invalid.is_valid())
        self.assertIn('height', serializer_invalid.errors)


class LoginSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='login@example.com', password='correctpassword')

    def test_valid_credentials_return_access_token(self):
        data = {'email': 'login@example.com', 'password': 'correctpassword'}
        serializer = LoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertIn('access', serializer.validated_data)

    def test_invalid_email_raises_validation_error(self):
        data = {'email': 'wrong@example.com', 'password': 'somepass'}
        serializer = LoginSerializer(data=data)
        with self.assertRaises(DRFValidationError):
            serializer.is_valid(raise_exception=True)

    def test_wrong_password_raises_validation_error(self):
        data = {'email': 'login@example.com', 'password': 'wrongpass'}
        serializer = LoginSerializer(data=data)
        with self.assertRaises(DRFValidationError):
            serializer.is_valid(raise_exception=True)

    def test_missing_fields_invalid(self):
        serializer = LoginSerializer(data={'email': 'test@example.com'})
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

        serializer = LoginSerializer(data={'password': 'testpass'})
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_login_case_insensitive_email(self):
        data = {'email': 'LOGIN@EXAMPLE.COM', 'password': 'correctpassword'}
        serializer = LoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertIn('access', serializer.validated_data)


class RegisterAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/auth/register/'

    def test_register_returns_201_on_success(self):
        data = {'email': 'api@example.com', 'password': 'testpass123'}
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_creates_user_in_db(self):
        data = {'email': 'apiuser@example.com', 'password': 'testpass123'}
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='apiuser@example.com').exists())

    def test_register_returns_400_missing_email_or_password(self):
        response = self.client.post(self.register_url, {'password': 'testpass123'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(self.register_url, {'email': 'test@example.com'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_returns_400_duplicate_email(self):
        User.objects.create_user(email='duplicate@example.com', password='existing')
        data = {'email': 'duplicate@example.com', 'password': 'testpass123'}
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_invalid_email_format(self):
        data = {'email': 'invalid-email', 'password': 'testpass123'}
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_register_long_email_rejected(self):
        long_email = 'a' * 245 + '@example.com' 
        data = {'email': long_email, 'password': 'testpass123'}
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  

        too_long = 'a' * 246 + '@example.com'
        data = {'email': too_long, 'password': 'testpass123'}
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_response_structure(self):
        data = {'email': 'struct@test.com', 'password': 'testpass123', 'first_name': 'John', 'last_name': 'Doe'}
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertIn('email', response.data)
        self.assertIn('first_name', response.data)
        self.assertIn('last_name', response.data)
        self.assertNotIn('password', response.data)

    def test_register_with_additional_member_fields(self):
        data = {
            'email': 'extra@test.com',
            'password': 'testpass123',
            'gender': 'Female',
            'birth_date': '1995-08-20',
            'height': '165.00',
            'weight': '60.00'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email='extra@test.com')
        member = user.member_profile
        self.assertEqual(member.gender, 'Female')
        self.assertEqual(str(member.birth_date), '1995-08-20')
        self.assertEqual(member.height, Decimal('165.00'))
        self.assertEqual(member.weight, Decimal('60.00'))

    def test_register_password_not_returned_in_response(self):
        data = {'email': 'secure@test.com', 'password': 'testpass123'}
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('password', str(response.data))

class LoginAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = '/api/auth/login/'
        self.user = User.objects.create_user(email='loginapi@example.com', password='correctpassword')

    def test_login_returns_200_and_access_token_on_success(self):
        data = {'email': 'loginapi@example.com', 'password': 'correctpassword'}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_login_returns_400_on_invalid_credentials(self):
        data = {'email': 'loginapi@example.com', 'password': 'wrongpassword'}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {'email': 'wrong@example.com', 'password': 'correctpassword'}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_returns_400_missing_fields(self):
        response = self.client.post(self.login_url, {'email': 'test@example.com'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(self.login_url, {'password': 'testpass'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_case_insensitive_email(self):
        data = {'email': 'LOGINAPI@EXAMPLE.COM', 'password': 'correctpassword'}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_login_with_extra_fields_ignored(self):
        data = {
            'email': 'loginapi@example.com',
            'password': 'correctpassword',
            'first_name': 'Ignored'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)