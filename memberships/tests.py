from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.db import IntegrityError
from decimal import Decimal
from datetime import date, timedelta, datetime

from rest_framework.test import APIClient
from rest_framework import status

from .models import Member
from .services import PricingEngine

User = get_user_model()


class MemberModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='membermodel@test.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.member = self.user.member_profile

    def test_member_auto_created_via_signal(self):
        """User oluşturulduğunda Member otomatik oluşmalı"""
        self.assertIsInstance(self.member, Member)
        self.assertEqual(self.member.user, self.user)

    def test_one_to_one_relationship_unique(self):
        """Aynı user'a ikinci Member eklenemez"""
        with self.assertRaises(IntegrityError):
            Member.objects.create(user=self.user)

    def test_membership_type_default_standard(self):
        self.assertEqual(self.member.membership_type, 'standard')

    def test_membership_type_choices_validation(self):
        self.member.membership_type = 'student'
        self.member.save()
        self.assertEqual(self.member.membership_type, 'student')

        self.member.membership_type = 'premium'
        self.member.save()
        self.assertEqual(self.member.membership_type, 'premium')

        with self.assertRaises(Exception):
            self.member.membership_type = 'invalid'
            self.member.full_clean()

    def test_gender_choices_validation(self):
        self.member.gender = 'Male'
        self.member.save()
        self.assertEqual(self.member.gender, 'Male')

        self.member.gender = 'Other'
        self.member.save()
        self.assertEqual(self.member.gender, 'Other')

        self.member.gender = 'Unknown'
        with self.assertRaises(Exception):
            self.member.full_clean()

    def test_birth_date_and_age_property(self):
        self.member.birth_date = date(1990, 5, 15)
        self.member.save()

        expected_age = 35
        self.assertEqual(self.member.age, expected_age)

        self.member.birth_date = date(1990, 12, 25)
        self.member.save()
        self.assertEqual(self.member.age, 34)

        self.member.birth_date = None
        self.member.save()
        self.assertIsNone(self.member.age)

    def test_height_and_weight_decimal_fields(self):
        self.member.height = Decimal('180.50')
        self.member.weight = Decimal('75.25')
        self.member.save()

        self.member.refresh_from_db()
        self.assertEqual(self.member.height, Decimal('180.50'))
        self.assertEqual(self.member.weight, Decimal('75.25'))

        self.member.height = None
        self.member.weight = None
        self.member.save()
        self.assertIsNone(self.member.height)
        self.assertIsNone(self.member.weight)

    def test_str_method_full_name(self):
        expected = 'Test User - Standard'
        self.assertEqual(str(self.member), expected)

    def test_str_method_only_email(self):
        user_no_name = User.objects.create_user(email='noname@test.com', password='pass')
        member_no_name = user_no_name.member_profile
        expected = 'noname@test.com - Standard'
        self.assertEqual(str(member_no_name), expected)

    def test_member_cascade_delete_on_user_delete(self):
        member_id = self.member.id
        self.user.delete()
        with self.assertRaises(Member.DoesNotExist):
            Member.objects.get(id=member_id)


class MemberSignalTests(TestCase):
    def test_signal_creates_member_on_user_creation(self):
        user = User.objects.create_user(email='signal@test.com', password='pass')
        self.assertTrue(hasattr(user, 'member_profile'))
        self.assertEqual(user.member_profile.membership_type, 'standard')

    def test_signal_save_updates_member_on_user_save(self):
        user = User.objects.create_user(email='updatesignal@test.com', password='pass')
        member = user.member_profile
        original_membership = member.membership_type

        member.membership_type = 'premium'
        member.save()

        user.first_name = 'Updated'
        user.save()

        member.refresh_from_db()
        self.assertEqual(member.membership_type, 'premium')


class UserProfileViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('user-profile')

        self.user = User.objects.create_user(
            email='profiletest@test.com',
            password='testpass123',
            first_name='Profile',
            last_name='Test'
        )
        self.member = self.user.member_profile
        self.member.gender = 'Female'
        self.member.birth_date = date(1992, 8, 10)
        self.member.height = Decimal('165.00')
        self.member.weight = Decimal('58.00')
        self.member.membership_type = 'student'
        self.member.save()

    def test_unauthenticated_access_denied(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.url, {'membership_type': 'premium'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_returns_correct_profile_data(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertEqual(data['name'], 'Profile Test')
        self.assertEqual(data['gender'], 'Female')
        self.assertEqual(data['membership_type'], 'student')
        self.assertIn('age', data)
        self.assertEqual(data['age'], 33)
        self.assertEqual(data['height'], '165.00 cm')
        self.assertEqual(data['weight'], '58.00 kg')
        self.assertIn('dateOfBirth', data)

    def test_patch_successfully_updates_membership_type(self):
        self.client.force_authenticate(user=self.user)
        data = {'membership_type': 'premium'}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['membership_type'], 'premium')

        self.member.refresh_from_db()
        self.assertEqual(self.member.membership_type, 'premium')

    def test_patch_with_active_reservation_blocked(self):
        from reservations.models import Reservation
        from classes.models import FitnessClass

        instructor = User.objects.create_user(email='inst@test.com', password='pass')
        future_class = FitnessClass.objects.create(
            name='Blocked Class',
            instructor=instructor,
            capacity=10,
            date_time=timezone.now() + timedelta(days=5),
            base_price=Decimal('100.00')
        )
        Reservation.objects.create(
            member=self.member,
            fitness_class=future_class,
            price_paid=Decimal('80.00')
        )

        self.client.force_authenticate(user=self.user)
        data = {'membership_type': 'standard'}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('rezervasyonlarınız', response.data['detail'])

    def test_patch_invalid_membership_type_rejected(self):
        self.client.force_authenticate(user=self.user)
        data = {'membership_type': 'invalid_type'}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Geçersiz üyelik tipi', response.data['detail'])

    def test_patch_missing_membership_type_rejected(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('membership_type alanı zorunludur', response.data['detail'])

    def test_patch_extra_fields_ignored(self):
        self.client.force_authenticate(user=self.user)
        data = {'membership_type': 'standard', 'gender': 'Male', 'unknown': 'test'}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.member.refresh_from_db()
        self.assertEqual(self.member.gender, 'Female')
        self.assertEqual(self.member.membership_type, 'standard')


class MemberEdgeCaseTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='edge@test.com', password='pass')
        self.member = self.user.member_profile

    def test_member_with_all_fields_filled(self):
        self.member.gender = 'Other'
        self.member.birth_date = date(2000, 1, 1)
        self.member.height = Decimal('999.99')
        self.member.weight = Decimal('999.99')
        self.member.membership_type = 'premium'
        self.member.full_clean()
        self.member.save()

        self.member.refresh_from_db()
        self.assertEqual(self.member.gender, 'Other')
        self.assertEqual(self.member.birth_date, date(2000, 1, 1))
        self.assertEqual(self.member.age, 25)  # 2025'te
        self.assertEqual(self.member.height, Decimal('999.99'))
        self.assertEqual(self.member.weight, Decimal('999.99'))
        self.assertEqual(self.member.membership_type, 'premium')

    def test_member_with_minimal_fields(self):
        user_min = User.objects.create_user(email='minimal@test.com', password='pass')
        member_min = user_min.member_profile
        self.assertEqual(member_min.gender, None)
        self.assertEqual(member_min.birth_date, None)
        self.assertEqual(member_min.height, None)
        self.assertEqual(member_min.weight, None)
        self.assertEqual(member_min.membership_type, 'standard')

    def test_age_calculation_leap_year(self):
        self.member.birth_date = date(1996, 2, 29)
        self.member.save()
        self.assertEqual(self.member.age, 29)


class PricingEngineTests(TestCase):
    def setUp(self):
        self.base_price = Decimal('200.00')

    def test_student_basic_discount(self):
        price = PricingEngine.calculate_class_price(
            base_price=self.base_price,
            membership_type='student',
            class_datetime=datetime(2025, 12, 22, 10, 0),
            current_occupancy_rate=Decimal('0.3')
        )
        self.assertEqual(price, Decimal('160.00'))

    def test_standard_no_discount(self):
        price = PricingEngine.calculate_class_price(
            base_price=self.base_price,
            membership_type='standard',
            class_datetime=datetime(2025, 12, 22, 10, 0),
            current_occupancy_rate=Decimal('0.3')
        )
        self.assertEqual(price, Decimal('200.00'))

    def test_premium_free(self):
        price = PricingEngine.calculate_class_price(
            base_price=self.base_price,
            membership_type='premium',
            class_datetime=datetime(2025, 12, 22, 19, 0),
            current_occupancy_rate=Decimal('0.95')
        )
        self.assertEqual(price, Decimal('0.00'))

    def test_student_peak_hour(self):
        price = PricingEngine.calculate_class_price(
            base_price=self.base_price,
            membership_type='student',
            class_datetime=datetime(2025, 12, 22, 19, 0),
            current_occupancy_rate=Decimal('0.3')
        )
        self.assertEqual(price, Decimal('192.00'))

    def test_standard_peak_hour(self):
        price = PricingEngine.calculate_class_price(
            base_price=self.base_price,
            membership_type='standard',
            class_datetime=datetime(2025, 12, 22, 20, 0),
            current_occupancy_rate=Decimal('0.3')
        )
        self.assertEqual(price, Decimal('300.00'))

    def test_premium_peak_hour_no_effect(self):
        price = PricingEngine.calculate_class_price(
            base_price=self.base_price,
            membership_type='premium',
            class_datetime=datetime(2025, 12, 22, 20, 0),
            current_occupancy_rate=Decimal('0.3')
        )
        self.assertEqual(price, Decimal('0.00'))

    def test_surge_pricing_standard_high_occupancy(self):
        price = PricingEngine.calculate_class_price(
            base_price=self.base_price,
            membership_type='standard',
            class_datetime=datetime(2025, 12, 22, 10, 0),
            current_occupancy_rate=Decimal('0.85')
        )
        self.assertEqual(price, Decimal('210.00'))

    def test_surge_pricing_student_with_peak_and_surge(self):
        price = PricingEngine.calculate_class_price(
            base_price=self.base_price,
            membership_type='student',
            class_datetime=datetime(2025, 12, 22, 19, 0),
            current_occupancy_rate=Decimal('0.92')
        )
        self.assertEqual(price, Decimal('211.20'))

    def test_surge_pricing_premium_no_effect(self):
        price = PricingEngine.calculate_class_price(
            base_price=self.base_price,
            membership_type='premium',
            class_datetime=datetime(2025, 12, 22, 10, 0),
            current_occupancy_rate=Decimal('0.99')
        )
        self.assertEqual(price, Decimal('0.00'))

    def test_surge_threshold_edge_cases(self):
        price = PricingEngine.calculate_class_price(
            base_price=self.base_price,
            membership_type='standard',
            class_datetime=datetime(2025, 12, 22, 10, 0),
            current_occupancy_rate=Decimal('0.80')
        )
        self.assertEqual(price, Decimal('200.00'))

        price = PricingEngine.calculate_class_price(
            base_price=self.base_price,
            membership_type='standard',
            class_datetime=datetime(2025, 12, 22, 10, 0),
            current_occupancy_rate=Decimal('0.8001')
        )
        self.assertEqual(price, Decimal('200.10'))

    def test_all_modifiers_combined_standard_peak_surge(self):
        price = PricingEngine.calculate_class_price(
            base_price=self.base_price,
            membership_type='standard',
            class_datetime=datetime(2025, 12, 22, 20, 0),
            current_occupancy_rate=Decimal('0.95')
        )
        self.assertEqual(price, Decimal('330.00'))

    def test_all_modifiers_combined_student_peak_surge(self):
        price = PricingEngine.calculate_class_price(
            base_price=self.base_price,
            membership_type='student',
            class_datetime=datetime(2025, 12, 22, 20, 0),
            current_occupancy_rate=Decimal('0.95')
        )
        self.assertEqual(price, Decimal('211.20'))

    def test_invalid_membership_type_raises_value_error(self):
        with self.assertRaises(ValueError) as context:
            PricingEngine.calculate_class_price(
                base_price=self.base_price,
                membership_type='invalid',
                class_datetime=datetime.now(),
                current_occupancy_rate=Decimal('0.5')
            )
        self.assertIn('Geçersiz üyelik tipi', str(context.exception))

    def test_non_decimal_inputs_converted(self):
        price = PricingEngine.calculate_class_price(
            base_price=200.00,  # float
            membership_type='student',
            class_datetime=datetime(2025, 12, 22, 10, 0),
            current_occupancy_rate=0.5
        )
        self.assertEqual(price, Decimal('160.00'))

    def test_refund_premium_full(self):
        refund = PricingEngine.calculate_refund_amount(
            original_price=Decimal('200.00'),
            membership_type='premium',
            hours_before_class=3
        )
        self.assertEqual(refund, Decimal('200.00'))

    def test_refund_premium_too_late(self):
        refund = PricingEngine.calculate_refund_amount(
            original_price=Decimal('200.00'),
            membership_type='premium',
            hours_before_class=1
        )
        self.assertEqual(refund, Decimal('0.00'))

    def test_refund_student_on_time(self):
        refund = PricingEngine.calculate_refund_amount(
            original_price=Decimal('160.00'),
            membership_type='student',
            hours_before_class=25
        )
        self.assertEqual(refund, Decimal('80.00'))

    def test_refund_student_late(self):
        refund = PricingEngine.calculate_refund_amount(
            original_price=Decimal('160.00'),
            membership_type='student',
            hours_before_class=20
        )
        self.assertEqual(refund, Decimal('0.00'))

    def test_refund_standard_always_zero(self):
        refund = PricingEngine.calculate_refund_amount(
            original_price=Decimal('200.00'),
            membership_type='standard',
            hours_before_class=100
        )
        self.assertEqual(refund, Decimal('0.00'))

    def test_refund_invalid_membership_type(self):
        with self.assertRaises(ValueError):
            PricingEngine.calculate_refund_amount(
                original_price=Decimal('200.00'),
                membership_type='invalid',
                hours_before_class=10
            )