from django.test import TestCase
from django.contrib.auth import get_user_model
from django. db import IntegrityError
from django.db import transaction
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.exceptions import ValidationError as DRFValidationError

from . serializers import RegisterSerializer, LoginSerializer

User = get_user_model()


class UserModelTests(TestCase):

    def test_create_user_with_email(self):
        user = User. objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user. email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))

    def test_email_uniqueness_constraint(self):
        User.objects.create_user(
            email='unique@example.com',
            password='testpass123'
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                User. objects.create_user(
                    email='unique@example.com',
                    password='differentpass'
                )

    def test_password_is_hashed(self):
        raw_password = 'mysecretpassword'
        user = User.objects.create_user(
            email='hash@example.com',
            password=raw_password
        )
        self.assertNotEqual(user.password, raw_password)
        self.assertTrue(user.check_password(raw_password))

    def test_create_user_without_email_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email='',
                password='testpass123'
            )

    def test_create_user_with_none_email_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email=None,
                password='testpass123'
            )

    def test_is_instructor_default_false(self):
        user = User.objects.create_user(
            email='instructor@example.com',
            password='testpass123'
        )
        self.assertFalse(user.is_instructor)

    def test_is_active_default_true(self):
        user = User.objects.create_user(
            email='active@example.com',
            password='testpass123'
        )
        self.assertTrue(user. is_active)

    def test_is_staff_default_false(self):
        user = User.objects.create_user(
            email='staff@example.com',
            password='testpass123'
        )
        self.assertFalse(user.is_staff)

    def test_email_normalization(self):
        user = User.objects.create_user(
            email='TEST@EXAMPLE.COM',
            password='testpass123'
        )
        self.assertEqual(user.email, 'TEST@example.com')

    def test_first_name_blank_allowed(self):
        user = User.objects.create_user(
            email='blank@example.com',
            password='testpass123',
            first_name=''
        )
        self.assertEqual(user.first_name, '')

    def test_last_name_blank_allowed(self):
        user = User.objects.create_user(
            email='blankln@example.com',
            password='testpass123',
            last_name=''
        )
        self.assertEqual(user.last_name, '')

    def test_create_superuser(self):
        superuser = User.objects.create_superuser(
            email='super@example.com',
            password='superpass123'
        )
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_create_superuser_without_email_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email='',
                password='superpass123'
            )


class RegisterSerializerTests(TestCase):

    def test_password_is_write_only(self):
        data = {
            'email': 'register@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer. is_valid())
        user = serializer.save()
        output = serializer. data
        self.assertNotIn('password', output)
        self.assertNotIn('password', output.get('user', {}))

    def test_token_returned_on_success(self):
        data = {
            'email': 'token@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        output = serializer. data
        self. assertIn('token', output)
        self.assertIsInstance(output['token'], str)
        self.assertTrue(len(output['token']) > 0)

    def test_user_object_structure_in_response(self):
        data = {
            'email': 'structure@example.com',
            'password': 'testpass123',
            'first_name': 'John',
            'last_name':  'Doe'
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        output = serializer.data
        self. assertIn('user', output)
        user_data = output['user']
        self.assertIn('email', user_data)
        self.assertIn('first_name', user_data)
        self.assertIn('last_name', user_data)
        self.assertIn('is_instructor', user_data)
        self.assertEqual(user_data['email'], 'structure@example.com')
        self.assertEqual(user_data['first_name'], 'John')
        self.assertEqual(user_data['last_name'], 'Doe')
        self.assertFalse(user_data['is_instructor'])

    def test_user_created_in_database(self):
        data = {
            'email':  'created@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertTrue(User.objects.filter(email='created@example.com').exists())

    def test_email_normalization_via_serializer(self):
        data = {
            'email': 'NORMALIZED@EXAMPLE.COM',
            'password': 'testpass123',
            'first_name':  'Test',
            'last_name': 'User'
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.email, 'NORMALIZED@example.com')

    def test_missing_email_invalid(self):
        data = {
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_missing_password_invalid(self):
        data = {
            'email': 'nopass@example.com',
            'first_name': 'Test',
            'last_name':  'User'
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

    def test_optional_first_name(self):
        data = {
            'email': 'nofirst@example.com',
            'password': 'testpass123',
            'last_name': 'User'
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer. is_valid())
        user = serializer.save()
        self.assertEqual(user.first_name, '')

    def test_optional_last_name(self):
        data = {
            'email': 'nolast@example.com',
            'password':  'testpass123',
            'first_name': 'Test'
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer. is_valid())
        user = serializer.save()
        self.assertEqual(user.last_name, '')


class LoginSerializerTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='login@example.com',
            password='correctpassword'
        )

    def test_valid_credentials_return_access_token(self):
        data = {
            'email': 'login@example.com',
            'password': 'correctpassword'
        }
        serializer = LoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertIn('access', serializer.validated_data)
        self.assertIsInstance(serializer.validated_data['access'], str)
        self.assertTrue(len(serializer.validated_data['access']) > 0)

    def test_invalid_email_raises_validation_error(self):
        data = {
            'email': 'nonexistent@example.com',
            'password': 'somepassword'
        }
        serializer = LoginSerializer(data=data)
        with self.assertRaises(DRFValidationError) as context:
            serializer.is_valid(raise_exception=True)
        self.assertIn('Invalid credentials', str(context.exception. detail))

    def test_wrong_password_raises_validation_error(self):
        data = {
            'email': 'login@example.com',
            'password': 'wrongpassword'
        }
        serializer = LoginSerializer(data=data)
        with self.assertRaises(DRFValidationError) as context:
            serializer.is_valid(raise_exception=True)
        self.assertIn('Invalid credentials', str(context.exception.detail))

    def test_email_case_sensitivity(self):
        data = {
            'email': 'LOGIN@example.com',
            'password':  'correctpassword'
        }
        serializer = LoginSerializer(data=data)
        is_valid = serializer.is_valid()
        if is_valid:
            self. assertIn('access', serializer.validated_data)
        else:
            self. assertTrue('email' in serializer.errors or 'non_field_errors' in serializer. errors)

    def test_missing_email_invalid(self):
        data = {
            'password': 'somepassword'
        }
        serializer = LoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_missing_password_invalid(self):
        data = {
            'email': 'login@example. com'
        }
        serializer = LoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)


class RegisterAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/auth/register/'

    def test_register_returns_201_on_success(self):
        data = {
            'email': 'api@example.com',
            'password': 'testpass123',
            'first_name': 'API',
            'last_name':  'User'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_returns_token(self):
        data = {
            'email': 'apitoken@example.com',
            'password': 'testpass123',
            'first_name': 'API',
            'last_name': 'User'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)

    def test_register_returns_user_object(self):
        data = {
            'email': 'apiuser@example.com',
            'password': 'testpass123',
            'first_name':  'API',
            'last_name': 'User'
        }
        response = self. client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)

    def test_register_returns_400_missing_email(self):
        data = {
            'password': 'testpass123',
            'first_name': 'API',
            'last_name': 'User'
        }
        response = self.client.post(self. register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_returns_400_missing_password(self):
        data = {
            'email':  'nopass@example.com',
            'first_name': 'API',
            'last_name':  'User'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_returns_400_invalid_email(self):
        data = {
            'email': 'not-an-email',
            'password': 'testpass123',
            'first_name': 'API',
            'last_name': 'User'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_returns_400_duplicate_email(self):
        User.objects.create_user(
            email='duplicate@example.com',
            password='existingpass'
        )
        data = {
            'email':  'duplicate@example.com',
            'password': 'testpass123',
            'first_name': 'API',
            'last_name': 'User'
        }
        response = self.client.post(self. register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.login_url = '/api/auth/login/'
        self.user = User.objects.create_user(
            email='loginapi@example.com',
            password='correctpassword'
        )

    def test_login_returns_200_on_success(self):
        data = {
            'email': 'loginapi@example.com',
            'password': 'correctpassword'
        }
        response = self.client.post(self. login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_returns_access_token(self):
        data = {
            'email': 'loginapi@example.com',
            'password': 'correctpassword'
        }
        response = self.client.post(self. login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_login_returns_400_invalid_credentials(self):
        data = {
            'email': 'loginapi@example. com',
            'password': 'wrongpassword'
        }
        response = self.client. post(self.login_url, data)
        self.assertEqual(response.status_code, status. HTTP_400_BAD_REQUEST)

    def test_login_returns_400_nonexistent_user(self):
        data = {
            'email': 'doesnotexist@example.com',
            'password': 'somepassword'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response. status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_returns_400_missing_email(self):
        data = {
            'password': 'somepassword'
        }
        response = self.client. post(self.login_url, data)
        self.assertEqual(response.status_code, status. HTTP_400_BAD_REQUEST)

    def test_login_returns_400_missing_password(self):
        data = {
            'email': 'loginapi@example.com'
        }
        response = self.client. post(self.login_url, data)
        self.assertEqual(response.status_code, status. HTTP_400_BAD_REQUEST)
