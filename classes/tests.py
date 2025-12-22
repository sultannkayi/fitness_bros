from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import timedelta

from rest_framework.test import APIClient
from rest_framework import status

from .models import FitnessClass
from .serializers import FitnessClassSerializer

User = get_user_model()

class FitnessClassModelTests(TestCase):
    def setUp(self):
        self.instructor = User.objects.create_user(
            email='instructor@test.com',
            password='testpass123',
            first_name='Ahmet',
            last_name='Yılmaz'
        )

    def test_create_valid_class(self):
        future_time = timezone.now() + timedelta(days=3)
        fitness_class = FitnessClass.objects.create(
            name='Zumba Advanced',
            instructor=self.instructor,
            capacity=25,
            date_time=future_time,
            base_price=Decimal('180.00'),
            is_active=True
        )
        self.assertEqual(fitness_class.name, 'Zumba Advanced')
        self.assertEqual(fitness_class.capacity, 25)
        self.assertEqual(fitness_class.base_price, Decimal('180.00'))
        self.assertTrue(fitness_class.is_active)

    def test_capacity_must_be_positive(self):
        future_time = timezone.now() + timedelta(days=1)
        fitness_class = FitnessClass(
            name='Invalid Capacity',
            instructor=self.instructor,
            capacity=0,
            date_time=future_time,
            base_price=Decimal('100.00')
        )
        with self.assertRaises(ValidationError):
            fitness_class.full_clean()

        fitness_class.capacity = -10
        with self.assertRaises(ValidationError):
            fitness_class.full_clean()

    def test_date_time_must_be_in_future(self):
        past_time = timezone.now() - timedelta(days=1)
        fitness_class = FitnessClass(
            name='Past Class',
            instructor=self.instructor,
            capacity=15,
            date_time=past_time,
            base_price=Decimal('120.00')
        )
        with self.assertRaises(ValidationError):
            fitness_class.full_clean()

    def test_str_method_with_full_name(self):
        future_time = timezone.now() + timedelta(days=4)
        fitness_class = FitnessClass.objects.create(
            name='Pilates',
            instructor=self.instructor,
            capacity=20,
            date_time=future_time,
            base_price=Decimal('150.00')
        )
        expected = f"Pilates - Ahmet Yılmaz ({future_time.strftime('%Y-%m-%d %H:%M')})"
        self.assertEqual(str(fitness_class), expected)

    def test_str_method_fallback_to_email(self):
        instructor_no_name = User.objects.create_user(email='no_name@test.com', password='pass')
        future_time = timezone.now() + timedelta(days=2)
        fitness_class = FitnessClass.objects.create(
            name='HIIT',
            instructor=instructor_no_name,
            capacity=12,
            date_time=future_time,
            base_price=Decimal('200.00')
        )
        expected = f"HIIT - no_name@test.com ({future_time.strftime('%Y-%m-%d %H:%M')})"
        self.assertEqual(str(fitness_class), expected)

    def test_is_active_default_true(self):
        future_time = timezone.now() + timedelta(days=1)
        fitness_class = FitnessClass.objects.create(
            name='Default Active',
            instructor=self.instructor,
            capacity=10,
            date_time=future_time,
            base_price=Decimal('100.00')
        )
        self.assertTrue(fitness_class.is_active)

    def test_base_price_precision_and_zero_allowed(self):
        future_time = timezone.now() + timedelta(days=5)
        fitness_class = FitnessClass.objects.create(
            name='Free Workshop',
            instructor=self.instructor,
            capacity=50,
            date_time=future_time,
            base_price=Decimal('0.00')
        )
        self.assertEqual(fitness_class.base_price, Decimal('0.00'))

        fitness_class = FitnessClass.objects.create(
            name='Precision Test',
            instructor=self.instructor,
            capacity=10,
            date_time=future_time,
            base_price=Decimal('99.99')
        )
        self.assertEqual(fitness_class.base_price, Decimal('99.99'))

    def test_name_max_length(self):
        long_name = 'A' * 100
        future_time = timezone.now() + timedelta(days=1)
        fitness_class = FitnessClass.objects.create(
            name=long_name,
            instructor=self.instructor,
            capacity=20,
            date_time=future_time,
            base_price=Decimal('100.00')
        )
        self.assertEqual(fitness_class.name, long_name)

        too_long = 'A' * 101
        fitness_class = FitnessClass(
            name=too_long,
            instructor=self.instructor,
            capacity=20,
            date_time=future_time,
            base_price=Decimal('100.00')
        )
        with self.assertRaises(ValidationError):
            fitness_class.full_clean()

    def test_capacity_one_allowed(self):
        future_time = timezone.now() + timedelta(days=2)
        fitness_class = FitnessClass.objects.create(
            name='Private Session',
            instructor=self.instructor,
            capacity=1,
            date_time=future_time,
            base_price=Decimal('500.00')
        )
        self.assertEqual(fitness_class.capacity, 1)


class FitnessClassSerializerTests(TestCase):
    def setUp(self):
        self.instructor = User.objects.create_user(
            email='inst@test.com',
            password='pass',
            first_name='Mehmet',
            last_name='Demir'
        )
        self.future_time = timezone.now() + timedelta(days=7)
        self.fitness_class = FitnessClass.objects.create(
            name='Spinning Pro',
            instructor=self.instructor,
            capacity=30,
            date_time=self.future_time,
            base_price=Decimal('130.00'),
            is_active=True
        )

    def test_serializer_contains_all_fields(self):
        serializer = FitnessClassSerializer(self.fitness_class)
        data = serializer.data
        expected = ['id', 'name', 'instructor_name', 'capacity', 'date_time', 'base_price', 'is_active', 'available_spots']
        for field in expected:
            self.assertIn(field, data)

    def test_instructor_name_full_name_priority(self):
        serializer = FitnessClassSerializer(self.fitness_class)
        self.assertEqual(serializer.data['instructor_name'], 'Mehmet Demir')

    def test_instructor_name_fallback_email(self):
        no_name_inst = User.objects.create_user(email='fallback@test.com', password='pass')
        cls = FitnessClass.objects.create(
            name='Fallback Class',
            instructor=no_name_inst,
            capacity=15,
            date_time=self.future_time,
            base_price=Decimal('100.00')
        )
        serializer = FitnessClassSerializer(cls)
        self.assertEqual(serializer.data['instructor_name'], 'fallback@test.com')

    def test_available_spots_initial(self):
        serializer = FitnessClassSerializer(self.fitness_class)
        self.assertEqual(serializer.data['available_spots'], 30)

    def test_available_spots_with_reservations(self):
        from reservations.models import Reservation  # Test ortamında çalışır
        member_user = User.objects.create_user(email='resmember@test.com', password='pass')

        # 12 rezervasyon ekle
        for _ in range(12):
            Reservation.objects.create(
                member=member_user.member_profile,
                fitness_class=self.fitness_class,
                price_paid=Decimal('130.00')
            )

        serializer = FitnessClassSerializer(self.fitness_class)
        self.assertEqual(serializer.data['available_spots'], 18)


class FitnessClassListViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('fitness-class-list')

        self.instructor = User.objects.create_user(email='viewinst@test.com', password='pass')
        base_time = timezone.now() + timedelta(days=2)

        self.active_classes = []
        dates = [base_time, base_time + timedelta(days=1), base_time + timedelta(days=5)]
        for i, dt in enumerate(dates):
            cls = FitnessClass.objects.create(
                name=f'Active {i+1}',
                instructor=self.instructor,
                capacity=20 + i * 5,
                date_time=dt,
                base_price=Decimal('100.00') + Decimal(i * 20),
                is_active=True
            )
            self.active_classes.append(cls)

        FitnessClass.objects.create(
            name='Inactive 1',
            instructor=self.instructor,
            capacity=15,
            date_time=base_time + timedelta(days=10),
            base_price=Decimal('150.00'),
            is_active=False
        )
        FitnessClass.objects.create(
            name='Inactive 2',
            instructor=self.instructor,
            capacity=10,
            date_time=base_time + timedelta(days=15),
            base_price=Decimal('200.00'),
            is_active=False
        )

    def test_list_returns_only_active_classes(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_list_orders_by_date_time_ascending(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        dates = [item['date_time'] for item in response.data]
        self.assertTrue(dates[0] < dates[1] < dates[2])

    def test_list_includes_all_calculated_fields(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.data:
            self.assertIn('instructor_name', item)
            self.assertIn('available_spots', item)
            self.assertIsInstance(item['available_spots'], int)
            self.assertIsInstance(item['capacity'], int)
            self.assertIsInstance(item['base_price'], str)

    def test_list_anonymous_access_allowed(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_response_structure_complete(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        sample = response.data[0]
        expected_keys = {'id', 'name', 'instructor_name', 'capacity', 'date_time', 'base_price', 'is_active', 'available_spots'}
        self.assertEqual(set(sample.keys()), expected_keys)

    def test_list_with_no_classes_returns_empty(self):
        FitnessClass.objects.filter(is_active=True).delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class FitnessClassEdgeAndValidationTests(TestCase):
    def setUp(self):
        self.instructor = User.objects.create_user(email='edgeinst@test.com', password='pass')

    def test_class_with_max_capacity(self):
        future_time = timezone.now() + timedelta(days=1)
        cls = FitnessClass.objects.create(
            name='Large Class',
            instructor=self.instructor,
            capacity=1000,
            date_time=future_time,
            base_price=Decimal('50.00')
        )
        self.assertEqual(cls.capacity, 1000)

    def test_class_with_very_long_name_truncated(self):
        long_name = 'A' * 150
        future_time = timezone.now() + timedelta(days=1)
        cls = FitnessClass(
            name=long_name,
            instructor=self.instructor,
            capacity=20,
            date_time=future_time,
            base_price=Decimal('100.00')
        )
        with self.assertRaises(ValidationError):
            cls.full_clean()

    def test_class_with_exact_future_time_allowed(self):
        exact_future = timezone.now() + timedelta(minutes=1)
        cls = FitnessClass.objects.create(
            name='Soon Class',
            instructor=self.instructor,
            capacity=10,
            date_time=exact_future,
            base_price=Decimal('100.00')
        )
        self.assertTrue(cls.date_time > timezone.now())

    def test_class_with_now_time_rejected(self):
        now_time = timezone.now()
        cls = FitnessClass(
            name='Now Class',
            instructor=self.instructor,
            capacity=10,
            date_time=now_time,
            base_price=Decimal('100.00')
        )
        with self.assertRaises(ValidationError):
            cls.full_clean()