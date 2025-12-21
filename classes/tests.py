from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
from decimal import Decimal
from django.contrib.auth import get_user_model

from . models import FitnessClass

User = get_user_model()


class FitnessClassModelTests(TestCase):

    def setUp(self):
        self.future_date = timezone.now() + timedelta(days=1)
        self.instructor_user = User.objects.create_user(
            email="instructor@test. com",
            password="testpass123",
            is_instructor=True
        )

    def test_create_valid_fitness_class(self):
        fitness_class = FitnessClass.objects.create(
            name="Morning Yoga",
            instructor=self.instructor_user,
            capacity=20,
            date_time=self.future_date,
            base_price=Decimal("100.00")
        )
        self.assertEqual(fitness_class.name, "Morning Yoga")
        self.assertEqual(fitness_class. capacity, 20)
        self.assertEqual(fitness_class.instructor, self.instructor_user)
        self.assertEqual(fitness_class.base_price, Decimal("100.00"))

    def test_capacity_zero_raises_validation_error(self):
        fitness_class = FitnessClass(
            name="Zero Capacity Class",
            instructor=self. instructor_user,
            capacity=0,
            date_time=self.future_date,
            base_price=Decimal("50.00")
        )
        with self.assertRaises(ValidationError) as context:
            fitness_class.full_clean()
        self.assertIn("Capacity must be positive", str(context. exception))

    def test_capacity_negative_raises_validation_error(self):
        fitness_class = FitnessClass(
            name="Negative Capacity Class",
            instructor=self. instructor_user,
            capacity=-5,
            date_time=self.future_date,
            base_price=Decimal("50.00")
        )
        with self.assertRaises(ValidationError):
            fitness_class. full_clean()

    def test_past_date_raises_validation_error(self):
        past_date = timezone.now() - timedelta(days=1)
        fitness_class = FitnessClass(
            name="Past Class",
            instructor=self. instructor_user,
            capacity=10,
            date_time=past_date,
            base_price=Decimal("50.00")
        )
        with self.assertRaises(ValidationError) as context:
            fitness_class.full_clean()
        self.assertIn("Class date must be in the future", str(context. exception))

    def test_is_active_defaults_to_true(self):
        fitness_class = FitnessClass. objects.create(
            name="Active Class",
            instructor=self.instructor_user,
            capacity=15,
            date_time=self.future_date,
            base_price=Decimal("75.00")
        )
        self.assertTrue(fitness_class.is_active)

    def test_is_active_can_be_set_to_false(self):
        fitness_class = FitnessClass.objects. create(
            name="Inactive Class",
            instructor=self. instructor_user,
            capacity=15,
            date_time=self.future_date,
            base_price=Decimal("75.00"),
            is_active=False
        )
        self.assertFalse(fitness_class.is_active)

    def test_str_contains_class_name(self):
        fitness_class = FitnessClass.objects.create(
            name="Pilates",
            instructor=self.instructor_user,
            capacity=10,
            date_time=self.future_date,
            base_price=Decimal("200.00")
        )
        self.assertIn("Pilates", str(fitness_class))

    def test_str_contains_instructor_first_name_when_present(self):
        self.instructor_user.first_name = "Jane"
        self.instructor_user.save()
        fitness_class = FitnessClass.objects.create(
            name="Spinning",
            instructor=self.instructor_user,
            capacity=12,
            date_time=self.future_date,
            base_price=Decimal("150.00")
        )
        self.assertIn("Jane", str(fitness_class))

    def test_str_contains_instructor_email_when_no_first_name(self):
        instructor_no_name = User.objects.create_user(
            email="noname@test.com",
            password="testpass123",
            is_instructor=True
        )
        fitness_class = FitnessClass.objects.create(
            name="HIIT",
            instructor=instructor_no_name,
            capacity=8,
            date_time=self.future_date,
            base_price=Decimal("120.00")
        )
        self.assertIn("noname@test.com", str(fitness_class))

    def test_instructor_foreign_key_relationship(self):
        fitness_class = FitnessClass.objects.create(
            name="CrossFit",
            instructor=self.instructor_user,
            capacity=12,
            date_time=self.future_date,
            base_price=Decimal("180.00")
        )
        self.assertEqual(fitness_class.instructor.email, "instructor@test.com")
        self.assertTrue(fitness_class. instructor.is_instructor)

    def test_base_price_accepts_decimal(self):
        fitness_class = FitnessClass.objects.create(
            name="Boxing",
            instructor=self.instructor_user,
            capacity=10,
            date_time=self.future_date,
            base_price=Decimal("99.99")
        )
        self.assertEqual(fitness_class.base_price, Decimal("99.99"))

    def test_base_price_max_digits(self):
        fitness_class = FitnessClass.objects. create(
            name="Premium Class",
            instructor=self.instructor_user,
            capacity=5,
            date_time=self.future_date,
            base_price=Decimal("99999.99")
        )
        self.assertEqual(fitness_class. base_price, Decimal("99999.99"))

    def test_date_time_stores_future_date(self):
        future_date = timezone.now() + timedelta(days=7)
        fitness_class = FitnessClass.objects.create(
            name="Future Class",
            instructor=self.instructor_user,
            capacity=20,
            date_time=future_date,
            base_price=Decimal("100.00")
        )
        self.assertEqual(fitness_class.date_time, future_date)

    def test_name_max_length(self):
        long_name = "A" * 100
        fitness_class = FitnessClass.objects.create(
            name=long_name,
            instructor=self.instructor_user,
            capacity=10,
            date_time=self.future_date,
            base_price=Decimal("50.00")
        )
        self.assertEqual(fitness_class.name, long_name)
        self.assertEqual(len(fitness_class.name), 100)

    def test_instructor_cascade_delete(self):
        temp_instructor = User.objects.create_user(
            email="temp@test.com",
            password="testpass123",
            is_instructor=True
        )
        fitness_class = FitnessClass.objects.create(
            name="Temp Class",
            instructor=temp_instructor,
            capacity=10,
            date_time=self.future_date,
            base_price=Decimal("50.00")
        )
        class_id = fitness_class.id
        temp_instructor.delete()
        self.assertFalse(FitnessClass.objects.filter(id=class_id).exists())