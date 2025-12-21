from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from django. core.exceptions import ValidationError
from django.db. utils import IntegrityError
from rest_framework.test import APIClient
from rest_framework import status

from classes.models import FitnessClass
from memberships.models import Member
from . models import Reservation
from .services import PricingEngine, ReservationService, CapacityCalculator

User = get_user_model()


class ReservationModelFieldTests(TestCase):

    def setUp(self):
        self.instructor = User.objects.create_user(
            email="instructor@test.com",
            password="testpass123",
            is_instructor=True
        )
        self.user = User.objects.create_user(
            email="member@test.com",
            password="testpass123"
        )
        self.future_date = timezone.now() + timedelta(days=2)
        self.fitness_class = FitnessClass.objects.create(
            name="Test Class",
            instructor=self.instructor,
            capacity=20,
            date_time=self.future_date,
            base_price=Decimal("100.00")
        )

    def test_reservation_has_member_field(self):
        reservation = Reservation.objects.create(
            member=self.user. member,
            fitness_class=self.fitness_class,
            price_paid=Decimal("100.00")
        )
        self.assertEqual(reservation.member, self.user.member)

    def test_reservation_has_fitness_class_field(self):
        reservation = Reservation.objects.create(
            member=self.user.member,
            fitness_class=self.fitness_class,
            price_paid=Decimal("100.00")
        )
        self.assertEqual(reservation.fitness_class, self.fitness_class)

    def test_reservation_has_price_paid_field(self):
        reservation = Reservation.objects.create(
            member=self.user.member,
            fitness_class=self.fitness_class,
            price_paid=Decimal("85.50")
        )
        self.assertEqual(reservation.price_paid, Decimal("85.50"))

    def test_reservation_has_created_at_field(self):
        reservation = Reservation.objects.create(
            member=self.user. member,
            fitness_class=self.fitness_class,
            price_paid=Decimal("100.00")
        )
        self.assertIsNotNone(reservation.created_at)

    def test_price_paid_allows_null(self):
        reservation = Reservation(
            member=self.user. member,
            fitness_class=self.fitness_class,
            price_paid=None
        )
        reservation.save()
        self.assertIsNotNone(reservation.price_paid)

    def test_created_at_auto_populates(self):
        reservation = Reservation.objects.create(
            member=self.user.member,
            fitness_class=self.fitness_class,
            price_paid=Decimal("100.00")
        )
        self.assertIsNotNone(reservation.created_at)
        self.assertLessEqual(reservation.created_at, timezone.now())

    def test_price_paid_accepts_zero(self):
        reservation = Reservation.objects.create(
            member=self.user.member,
            fitness_class=self. fitness_class,
            price_paid=Decimal("0.00")
        )
        self.assertEqual(reservation.price_paid, Decimal("0.00"))


class ReservationModelRelationshipTests(TestCase):

    def setUp(self):
        self.instructor = User.objects. create_user(
            email="instructor@test.com",
            password="testpass123",
            is_instructor=True
        )
        self.user = User. objects.create_user(
            email="member@test.com",
            password="testpass123"
        )
        self.future_date = timezone.now() + timedelta(days=2)
        self.fitness_class = FitnessClass.objects.create(
            name="Test Class",
            instructor=self.instructor,
            capacity=20,
            date_time=self.future_date,
            base_price=Decimal("100.00")
        )

    def test_reservation_member_foreign_key(self):
        reservation = Reservation.objects.create(
            member=self.user. member,
            fitness_class=self.fitness_class,
            price_paid=Decimal("100.00")
        )
        self.assertEqual(reservation.member. user. email, "member@test.com")

    def test_reservation_fitness_class_foreign_key(self):
        reservation = Reservation. objects.create(
            member=self.user.member,
            fitness_class=self.fitness_class,
            price_paid=Decimal("100.00")
        )
        self.assertEqual(reservation.fitness_class.name, "Test Class")

    def test_member_can_access_reservations_via_related_name(self):
        Reservation.objects.create(
            member=self.user.member,
            fitness_class=self. fitness_class,
            price_paid=Decimal("100.00")
        )
        reservations = self.user.member.reservations. all()
        self.assertEqual(reservations.count(), 1)

    def test_fitness_class_can_access_reservations_via_related_name(self):
        Reservation.objects.create(
            member=self.user. member,
            fitness_class=self.fitness_class,
            price_paid=Decimal("100.00")
        )
        reservations = self.fitness_class.reservations.all()
        self.assertEqual(reservations.count(), 1)

    def test_reservation_cascade_delete_on_member_delete(self):
        reservation = Reservation.objects.create(
            member=self.user. member,
            fitness_class=self.fitness_class,
            price_paid=Decimal("100.00")
        )
        reservation_id = reservation.id
        self.user.delete()
        self.assertFalse(Reservation.objects.filter(id=reservation_id).exists())

    def test_reservation_cascade_delete_on_fitness_class_delete(self):
        reservation = Reservation.objects.create(
            member=self.user.member,
            fitness_class=self. fitness_class,
            price_paid=Decimal("100.00")
        )
        reservation_id = reservation.id
        self.fitness_class.delete()
        self.assertFalse(Reservation.objects.filter(id=reservation_id).exists())


class ReservationModelConstraintTests(TestCase):

    def setUp(self):
        self.instructor = User.objects. create_user(
            email="instructor@test.com",
            password="testpass123",
            is_instructor=True
        )
        self.user1 = User.objects.create_user(
            email="member1@test.com",
            password="testpass123"
        )
        self.user2 = User.objects.create_user(
            email="member2@test.com",
            password="testpass123"
        )
        self.user3 = User.objects.create_user(
            email="member3@test.com",
            password="testpass123"
        )
        self.future_date = timezone.now() + timedelta(days=2)
        self.fitness_class = FitnessClass.objects.create(
            name="Small Class",
            instructor=self. instructor,
            capacity=2,
            date_time=self.future_date,
            base_price=Decimal("100.00")
        )

    def test_unique_member_class_reservation_constraint(self):
        Reservation.objects.create(
            member=self.user1.member,
            fitness_class=self.fitness_class,
            price_paid=Decimal("100.00")
        )
        with self.assertRaises(IntegrityError):
            Reservation.objects.create(
                member=self.user1.member,
                fitness_class=self.fitness_class,
                price_paid=Decimal("100.00")
            )

    def test_capacity_enforcement_raises_validation_error(self):
        Reservation.objects.create(
            member=self.user1.member,
            fitness_class=self.fitness_class,
            price_paid=Decimal("100.00")
        )
        Reservation.objects.create(
            member=self.user2.member,
            fitness_class=self.fitness_class,
            price_paid=Decimal("100.00")
        )
        with self.assertRaises(ValidationError):
            reservation = Reservation(
                member=self.user3.member,
                fitness_class=self.fitness_class,
                price_paid=Decimal("100.00")
            )
            reservation.full_clean()
            reservation.save()

    def test_capacity_enforcement_allows_booking_when_spots_available(self):
        reservation = Reservation(
            member=self.user1.member,
            fitness_class=self.fitness_class,
            price_paid=Decimal("100.00")
        )
        reservation.full_clean()
        reservation.save()
        self.assertTrue(Reservation.objects.filter(id=reservation.id).exists())

    def test_capacity_enforcement_excludes_self_on_update(self):
        reservation = Reservation.objects.create(
            member=self.user1.member,
            fitness_class=self.fitness_class,
            price_paid=Decimal("100.00")
        )
        Reservation.objects.create(
            member=self.user2.member,
            fitness_class=self.fitness_class,
            price_paid=Decimal("100.00")
        )
        reservation.price_paid = Decimal("90.00")
        reservation.full_clean()
        reservation.save()
        self.assertEqual(reservation.price_paid, Decimal("90.00"))


class ReservationModelAutoCalculationTests(TestCase):

    def setUp(self):
        self.instructor = User.objects.create_user(
            email="instructor@test.com",
            password="testpass123",
            is_instructor=True
        )
        self.user = User.objects. create_user(
            email="member@test.com",
            password="testpass123"
        )
        self.future_date = timezone.now() + timedelta(days=2)
        self.future_date = self.future_date.replace(hour=10, minute=0)
        self.fitness_class = FitnessClass.objects. create(
            name="Test Class",
            instructor=self.instructor,
            capacity=20,
            date_time=self.future_date,
            base_price=Decimal("100.00")
        )

    def test_save_calculates_price_when_price_paid_is_none(self):
        reservation = Reservation(
            member=self.user. member,
            fitness_class=self.fitness_class,
            price_paid=None
        )
        reservation.save()
        self.assertIsNotNone(reservation.price_paid)
        self.assertGreater(reservation.price_paid, Decimal("0.00"))

    def test_save_preserves_explicit_price_paid(self):
        reservation = Reservation(
            member=self.user.member,
            fitness_class=self. fitness_class,
            price_paid=Decimal("75.00")
        )
        reservation.save()
        self.assertEqual(reservation.price_paid, Decimal("75.00"))


class PricingEngineTests(TestCase):

    def setUp(self):
        self.base_price = Decimal("100.00")

    def test_standard_member_no_discount(self):
        price = PricingEngine.calculate_price(
            base_price=self.base_price,
            membership_type="STANDARD",
            occupancy_rate=0.10,
            is_peak_hour=False
        )
        self.assertEqual(price, Decimal("100.00"))

    def test_premium_member_20_percent_discount(self):
        price = PricingEngine. calculate_price(
            base_price=self.base_price,
            membership_type="PREMIUM",
            occupancy_rate=0.10,
            is_peak_hour=False
        )
        self.assertEqual(price, Decimal("80.00"))

    def test_student_member_50_percent_discount(self):
        price = PricingEngine. calculate_price(
            base_price=self.base_price,
            membership_type="STUDENT",
            occupancy_rate=0.10,
            is_peak_hour=False
        )
        self.assertEqual(price, Decimal("50.00"))

    def test_occupancy_below_80_no_surge(self):
        price = PricingEngine.calculate_price(
            base_price=self. base_price,
            membership_type="STANDARD",
            occupancy_rate=0.79,
            is_peak_hour=False
        )
        self.assertEqual(price, Decimal("100.00"))

    def test_occupancy_at_80_triggers_surge(self):
        price = PricingEngine.calculate_price(
            base_price=self.base_price,
            membership_type="STANDARD",
            occupancy_rate=0.80,
            is_peak_hour=False
        )
        self.assertEqual(price, Decimal("150.00"))

    def test_occupancy_above_80_triggers_surge(self):
        price = PricingEngine.calculate_price(
            base_price=self. base_price,
            membership_type="STANDARD",
            occupancy_rate=0.90,
            is_peak_hour=False
        )
        self.assertEqual(price, Decimal("150.00"))

    def test_off_peak_no_surcharge(self):
        price = PricingEngine.calculate_price(
            base_price=self.base_price,
            membership_type="STANDARD",
            occupancy_rate=0.10,
            is_peak_hour=False
        )
        self.assertEqual(price, Decimal("100.00"))

    def test_peak_hour_triggers_surcharge(self):
        price = PricingEngine.calculate_price(
            base_price=self.base_price,
            membership_type="STANDARD",
            occupancy_rate=0.10,
            is_peak_hour=True
        )
        self.assertEqual(price, Decimal("125.00"))

    def test_combined_premium_and_surge(self):
        price = PricingEngine.calculate_price(
            base_price=self.base_price,
            membership_type="PREMIUM",
            occupancy_rate=0.85,
            is_peak_hour=False
        )
        self.assertEqual(price, Decimal("120.00"))

    def test_combined_student_surge_and_peak(self):
        price = PricingEngine.calculate_price(
            base_price=self. base_price,
            membership_type="STUDENT",
            occupancy_rate=0.90,
            is_peak_hour=True
        )
        self.assertEqual(price, Decimal("93.75"))

    def test_price_quantized_to_two_decimals(self):
        price = PricingEngine.calculate_price(
            base_price=Decimal("33.33"),
            membership_type="PREMIUM",
            occupancy_rate=0.10,
            is_peak_hour=False
        )
        self.assertEqual(price, Decimal("26.66"))


class ReservationServiceValidationTests(TestCase):

    @patch("reservations.services.timezone.now")
    def test_validate_future_class_passes(self, mock_now):
        mock_now.return_value = timezone.datetime(2025, 6, 15, 10, 0, 0, tzinfo=timezone.utc)
        class_time = timezone.datetime(2025, 6, 16, 10, 0, 0, tzinfo=timezone.utc)
        is_valid, error = ReservationService.validate_reservation_time(class_time)
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

    @patch("reservations.services.timezone.now")
    def test_validate_past_class_fails(self, mock_now):
        mock_now.return_value = timezone.datetime(2025, 6, 15, 10, 0, 0, tzinfo=timezone.utc)
        class_time = timezone. datetime(2025, 6, 14, 10, 0, 0, tzinfo=timezone.utc)
        is_valid, error = ReservationService.validate_reservation_time(class_time)
        self.assertFalse(is_valid)
        self.assertIn("past", error. lower())

    @patch("reservations.services.timezone.now")
    def test_validate_class_less_than_1_hour_fails(self, mock_now):
        mock_now.return_value = timezone.datetime(2025, 6, 15, 10, 0, 0, tzinfo=timezone.utc)
        class_time = timezone.datetime(2025, 6, 15, 10, 30, 0, tzinfo=timezone.utc)
        is_valid, error = ReservationService.validate_reservation_time(class_time)
        self.assertFalse(is_valid)
        self.assertIn("1 hour", error.lower())

    @patch("reservations.services.timezone.now")
    def test_validate_class_more_than_30_days_fails(self, mock_now):
        mock_now.return_value = timezone.datetime(2025, 6, 15, 10, 0, 0, tzinfo=timezone.utc)
        class_time = timezone.datetime(2025, 7, 20, 10, 0, 0, tzinfo=timezone.utc)
        is_valid, error = ReservationService.validate_reservation_time(class_time)
        self.assertFalse(is_valid)
        self.assertIn("30 days", error.lower())


class ReservationServiceCancellationTests(TestCase):

    @patch("reservations.services.timezone.now")
    def test_cancellation_fee_free_over_24_hours(self, mock_now):
        mock_now.return_value = timezone.datetime(2025, 6, 15, 10, 0, 0, tzinfo=timezone.utc)
        class_time = timezone.datetime(2025, 6, 17, 10, 0, 0, tzinfo=timezone.utc)
        fee = ReservationService.calculate_cancellation_fee(
            original_price=Decimal("100.00"),
            class_datetime=class_time
        )
        self.assertEqual(fee, Decimal("0.00"))

    @patch("reservations.services.timezone.now")
    def test_cancellation_fee_50_percent_12_to_24_hours(self, mock_now):
        mock_now.return_value = timezone.datetime(2025, 6, 15, 10, 0, 0, tzinfo=timezone. utc)
        class_time = timezone.datetime(2025, 6, 15, 28, 0, 0, tzinfo=timezone.utc)
        class_time = timezone.datetime(2025, 6, 16, 4, 0, 0, tzinfo=timezone.utc)
        fee = ReservationService. calculate_cancellation_fee(
            original_price=Decimal("100.00"),
            class_datetime=class_time
        )
        self.assertEqual(fee, Decimal("50.00"))

    @patch("reservations.services.timezone.now")
    def test_cancellation_fee_100_percent_under_12_hours(self, mock_now):
        mock_now.return_value = timezone.datetime(2025, 6, 15, 10, 0, 0, tzinfo=timezone.utc)
        class_time = timezone.datetime(2025, 6, 15, 16, 0, 0, tzinfo=timezone.utc)
        fee = ReservationService.calculate_cancellation_fee(
            original_price=Decimal("100.00"),
            class_datetime=class_time
        )
        self.assertEqual(fee, Decimal("100.00"))

    def test_cancellation_with_custom_time(self):
        class_time = timezone.datetime(2025, 6, 20, 10, 0, 0, tzinfo=timezone.utc)
        cancellation_time = timezone.datetime(2025, 6, 18, 10, 0, 0, tzinfo=timezone.utc)
        fee = ReservationService. calculate_cancellation_fee(
            original_price=Decimal("100.00"),
            class_datetime=class_time,
            cancellation_time=cancellation_time
        )
        self.assertEqual(fee, Decimal("0.00"))


class ReservationServiceConflictTests(TestCase):

    def test_conflicting_reservation_before_6am_fails(self):
        class_time = timezone.datetime(2025, 6, 15, 5, 0, 0, tzinfo=timezone.utc)
        has_conflict, message = ReservationService.check_conflicting_reservations(
            user_id=1,
            class_datetime=class_time
        )
        self.assertTrue(has_conflict)
        self.assertIn("6 AM", message)

    def test_conflicting_reservation_after_10pm_fails(self):
        class_time = timezone.datetime(2025, 6, 15, 22, 0, 0, tzinfo=timezone.utc)
        has_conflict, message = ReservationService.check_conflicting_reservations(
            user_id=1,
            class_datetime=class_time
        )
        self.assertTrue(has_conflict)
        self.assertIn("10 PM", message)

    def test_conflicting_reservation_valid_hours_passes(self):
        class_time = timezone.datetime(2025, 6, 15, 14, 0, 0, tzinfo=timezone.utc)
        has_conflict, message = ReservationService.check_conflicting_reservations(
            user_id=1,
            class_datetime=class_time
        )
        self.assertFalse(has_conflict)
        self.assertEqual(message, "")


class CapacityCalculatorCanBookTests(TestCase):

    def test_can_book_with_available_spots(self):
        result = CapacityCalculator. can_book(current_bookings=5, capacity=20)
        self.assertTrue(result)

    def test_can_book_at_capacity_returns_false(self):
        result = CapacityCalculator.can_book(current_bookings=20, capacity=20)
        self.assertFalse(result)

    def test_can_book_zero_capacity_returns_false(self):
        result = CapacityCalculator.can_book(current_bookings=0, capacity=0)
        self.assertFalse(result)

    def test_can_book_one_spot_remaining(self):
        result = CapacityCalculator.can_book(current_bookings=19, capacity=20)
        self.assertTrue(result)


class CapacityCalculatorOccupancyTests(TestCase):

    def test_occupancy_rate_empty_class(self):
        rate = CapacityCalculator. calculate_occupancy_rate(current_bookings=0, capacity=20)
        self.assertEqual(rate, Decimal("0.00"))

    def test_occupancy_rate_half_full(self):
        rate = CapacityCalculator.calculate_occupancy_rate(current_bookings=10, capacity=20)
        self.assertEqual(rate, Decimal("0.50"))

    def test_occupancy_rate_full_class(self):
        rate = CapacityCalculator.calculate_occupancy_rate(current_bookings=20, capacity=20)
        self.assertEqual(rate, Decimal("1.00"))

    def test_occupancy_rate_zero_capacity_raises_error(self):
        with self.assertRaises(ValueError):
            CapacityCalculator.calculate_occupancy_rate(current_bookings=0, capacity=0)

    def test_occupancy_rate_negative_bookings_raises_error(self):
        with self.assertRaises(ValueError):
            CapacityCalculator.calculate_occupancy_rate(current_bookings=-1, capacity=20)

    def test_occupancy_rate_caps_at_100_percent(self):
        rate = CapacityCalculator.calculate_occupancy_rate(current_bookings=25, capacity=20)
        self.assertEqual(rate, Decimal("1.00"))


class CapacityCalculatorAvailableSpotsTests(TestCase):

    def test_available_spots_calculation(self):
        available = CapacityCalculator.get_available_spots(current_bookings=5, capacity=20)
        self.assertEqual(available, 15)

    def test_available_spots_returns_zero_not_negative(self):
        available = CapacityCalculator.get_available_spots(current_bookings=25, capacity=20)
        self.assertEqual(available, 0)

    def test_available_spots_at_capacity(self):
        available = CapacityCalculator. get_available_spots(current_bookings=20, capacity=20)
        self.assertEqual(available, 0)


class CapacityCalculatorNearlyFullTests(TestCase):

    def test_is_nearly_full_above_threshold(self):
        result = CapacityCalculator. is_nearly_full(current_bookings=18, capacity=20)
        self.assertTrue(result)

    def test_is_nearly_full_below_threshold(self):
        result = CapacityCalculator.is_nearly_full(current_bookings=17, capacity=20)
        self.assertFalse(result)

    def test_is_nearly_full_custom_threshold(self):
        result = CapacityCalculator. is_nearly_full(
            current_bookings=16,
            capacity=20,
            threshold=0.8
        )
        self.assertTrue(result)

    def test_is_nearly_full_zero_capacity(self):
        result = CapacityCalculator. is_nearly_full(current_bookings=0, capacity=0)
        self.assertTrue(result)


class CapacityCalculatorOptimalCapacityTests(TestCase):

    def test_optimal_capacity_room_limiting(self):
        capacity = CapacityCalculator. calculate_optimal_capacity(
            room_size_sqm=20,
            equipment_count=50,
            instructor_capacity=30
        )
        self.assertEqual(capacity, 10)

    def test_optimal_capacity_equipment_limiting(self):
        capacity = CapacityCalculator.calculate_optimal_capacity(
            room_size_sqm=100,
            equipment_count=5,
            instructor_capacity=30
        )
        self.assertEqual(capacity, 5)

    def test_optimal_capacity_instructor_limiting(self):
        capacity = CapacityCalculator. calculate_optimal_capacity(
            room_size_sqm=100,
            equipment_count=50,
            instructor_capacity=8
        )
        self.assertEqual(capacity, 8)

    def test_optimal_capacity_minimum_one(self):
        capacity = CapacityCalculator.calculate_optimal_capacity(
            room_size_sqm=1,
            equipment_count=0,
            instructor_capacity=0
        )
        self.assertEqual(capacity, 1)


class ReservationAPICreateTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.instructor = User.objects.create_user(
            email="instructor@test.com",
            password="testpass123",
            is_instructor=True
        )
        self.user = User.objects.create_user(
            email="member@test.com",
            password="testpass123"
        )
        self.future_date = timezone.now() + timedelta(days=2)
        self.future_date = self.future_date.replace(hour=10, minute=0)
        self.fitness_class = FitnessClass.objects.create(
            name="API Test Class",
            instructor=self.instructor,
            capacity=20,
            date_time=self.future_date,
            base_price=Decimal("100.00")
        )
        self.url = "/api/reservations/"

    def test_post_reservation_returns_201_on_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {"fitness_class_id": self. fitness_class.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_reservation_creates_record_in_database(self):
        self.client.force_authenticate(user=self.user)
        self.client.post(self.url, {"fitness_class_id": self. fitness_class.id})
        self.assertTrue(
            Reservation.objects.filter(
                member=self.user. member,
                fitness_class=self.fitness_class
            ).exists()
        )

    def test_post_reservation_returns_reservation_id(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {"fitness_class_id":  self.fitness_class.id})
        self.assertIn("id", response.data)
        self.assertIsInstance(response.data["id"], int)

    def test_post_reservation_requires_authentication(self):
        response = self.client.post(self.url, {"fitness_class_id": self. fitness_class.id})
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_post_reservation_returns_400_for_missing_fitness_class_id(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self. url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_reservation_returns_400_for_nonexistent_class(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {"fitness_class_id":  99999})
        self.assertEqual(response.status_code, status. HTTP_400_BAD_REQUEST)

    def test_post_reservation_returns_400_when_class_full(self):
        self.fitness_class.capacity = 0
        self.fitness_class. save()
        self.client. force_authenticate(user=self. user)
        response = self. client.post(self.url, {"fitness_class_id": self.fitness_class.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_reservation_returns_400_for_duplicate_booking(self):
        self.client.force_authenticate(user=self.user)
        self.client.post(self.url, {"fitness_class_id": self. fitness_class.id})
        response = self.client.post(self.url, {"fitness_class_id": self.fitness_class.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ReservationAPIDeleteTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.instructor = User.objects.create_user(
            email="instructor@test.com",
            password="testpass123",
            is_instructor=True
        )
        self.user = User.objects.create_user(
            email="member@test.com",
            password="testpass123"
        )
        self.future_date = timezone.now() + timedelta(days=2)
        self.fitness_class = FitnessClass.objects.create(
            name="Delete Test Class",
            instructor=self.instructor,
            capacity=20,
            date_time=self.future_date,
            base_price=Decimal("100.00")
        )
        self.reservation = Reservation.objects.create(
            member=self.user. member,
            fitness_class=self.fitness_class,
            price_paid=Decimal("100.00")
        )

    def test_delete_reservation_returns_204_on_success(self):
        self.client.force_authenticate(user=self.user)
        url = f"/api/reservations/{self.reservation.id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_reservation_removes_record_from_database(self):
        self.client.force_authenticate(user=self.user)
        reservation_id = self.reservation.id
        url = f"/api/reservations/{reservation_id}/"
        self.client.delete(url)
        self.assertFalse(Reservation.objects.filter(id=reservation_id).exists())

    def test_delete_reservation_requires_authentication(self):
        url = f"/api/reservations/{self.reservation.id}/"
        response = self.client.delete(url)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_delete_reservation_returns_404_for_nonexistent_id(self):
        self.client.force_authenticate(user=self.user)
        url = "/api/reservations/99999/"
        response = self.client. delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ReservationIntegrationClassesTests(TestCase):

    def setUp(self):
        self.instructor = User.objects.create_user(
            email="instructor@test.com",
            password="testpass123",
            is_instructor=True
        )
        self.user1 = User.objects.create_user(
            email="member1@test.com",
            password="testpass123"
        )
        self.user2 = User.objects.create_user(
            email="member2@test.com",
            password="testpass123"
        )
        self.future_date = timezone.now() + timedelta(days=2)
        self.future_date = self.future_date.replace(hour=10, minute=0)
        self.fitness_class = FitnessClass.objects.create(
            name="Integration Class",
            instructor=self.instructor,
            capacity=20,
            date_time=self.future_date,
            base_price=Decimal("100.00")
        )

    def test_reservation_uses_class_base_price(self):
        reservation = Reservation(
            member=self.user1. member,
            fitness_class=self.fitness_class,
            price_paid=None
        )
        reservation.save()
        self.assertEqual(reservation.price_paid, Decimal("100.00"))

    def test_multiple_reservations_accumulate_correctly(self):
        Reservation.objects.create(
            member=self.user1.member,
            fitness_class=self.fitness_class,
            price_paid=Decimal("100.00")
        )
        Reservation.objects.create(
            member=self.user2.member,
            fitness_class=self.fitness_class,
            price_paid=Decimal("100.00")
        )
        self.assertEqual(self.fitness_class.reservations.count(), 2)


class ReservationIntegrationMemberTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.instructor = User.objects.create_user(
            email="instructor@test.com",
            password="testpass123",
            is_instructor=True
        )
        self.standard_user = User.objects.create_user(
            email="standard@test.com",
            password="testpass123"
        )
        self.premium_user = User.objects.create_user(
            email="premium@test.com",
            password="testpass123"
        )
        self.premium_user.member.membership_type = "PREMIUM"
        self.premium_user.member.save()
        self.student_user = User.objects.create_user(
            email="student@test.com",
            password="testpass123"
        )
        self.student_user.member.membership_type = "STUDENT"
        self.student_user.member.save()
        self.future_date = timezone.now() + timedelta(days=2)
        self.future_date = self.future_date.replace(hour=10, minute=0)
        self.fitness_class = FitnessClass.objects.create(
            name="Member Test Class",
            instructor=self.instructor,
            capacity=20,
            date_time=self.future_date,
            base_price=Decimal("100.00")
        )

    def test_reservation_created_for_authenticated_user_member(self):
        self.client.force_authenticate(user=self.standard_user)
        self.client.post("/api/reservations/", {"fitness_class_id": self. fitness_class.id})
        reservation = Reservation.objects.get(fitness_class=self.fitness_class)
        self.assertEqual(reservation.member, self.standard_user.member)

    def test_reservation_applies_standard_membership_pricing(self):
        self.client.force_authenticate(user=self.standard_user)
        self.client.post("/api/reservations/", {"fitness_class_id": self.fitness_class. id})
        reservation = Reservation.objects.get(member=self.standard_user.member)
        self.assertEqual(reservation.price_paid, Decimal("100.00"))

    def test_reservation_applies_premium_membership_discount(self):
        self.client.force_authenticate(user=self.premium_user)
        self.client.post("/api/reservations/", {"fitness_class_id": self.fitness_class. id})
        reservation = Reservation.objects.get(member=self.premium_user.member)
        self.assertEqual(reservation.price_paid, Decimal("80.00"))

    def test_reservation_applies_student_membership_discount(self):
        self.client.force_authenticate(user=self.student_user)
        self.client.post("/api/reservations/", {"fitness_class_id": self.fitness_class.id})
        reservation = Reservation.objects.get(member=self.student_user.member)
        self.assertEqual(reservation. price_paid, Decimal("50.00"))

    def test_user_can_have_multiple_reservations_different_classes(self):
        future_date2 = timezone.now() + timedelta(days=3)
        fitness_class2 = FitnessClass.objects.create(
            name="Second Class",
            instructor=self. instructor,
            capacity=20,
            date_time=future_date2,
            base_price=Decimal("100.00")
        )
        Reservation.objects.create(
            member=self.standard_user.member,
            fitness_class=self.fitness_class,
            price_paid=Decimal("100.00")
        )
        Reservation.objects.create(
            member=self.standard_user.member,
            fitness_class=fitness_class2,
            price_paid=Decimal("100.00")
        )
        self.assertEqual(self.standard_user.member.reservations. count(), 2)

    def test_user_cannot_have_duplicate_reservation_same_class(self):
        Reservation.objects.create(
            member=self.standard_user. member,
            fitness_class=self.fitness_class,
            price_paid=Decimal("100.00")
        )
        with self.assertRaises(IntegrityError):
            Reservation.objects.create(
                member=self.standard_user.member,
                fitness_class=self.fitness_class,
                price_paid=Decimal("100.00")
            )

    def test_deleting_user_deletes_member_and_reservations(self):
        reservation = Reservation.objects.create(
            member=self.standard_user.member,
            fitness_class=self.fitness_class,
            price_paid=Decimal("100.00")
        )
        reservation_id = reservation.id
        member_id = self.standard_user.member.id
        self. standard_user.delete()
        self.assertFalse(Reservation.objects.filter(id=reservation_id).exists())
        self.assertFalse(Member.objects.filter(id=member_id).exists())


class ReservationIntegrationPriceTests(TestCase):

    def setUp(self):
        self.instructor = User.objects.create_user(
            email="instructor@test.com",
            password="testpass123",
            is_instructor=True
        )
        self.user = User.objects.create_user(
            email="member@test.com",
            password="testpass123"
        )
        self.future_date = timezone.now() + timedelta(days=2)
        self.future_date = self.future_date.replace(hour=10, minute=0)
        self.fitness_class = FitnessClass.objects.create(
            name="Price Test Class",
            instructor=self.instructor,
            capacity=20,
            date_time=self.future_date,
            base_price=Decimal("100.00")
        )

    def test_reservation_price_frozen_after_class_price_change(self):
        reservation = Reservation.objects.create(
            member=self.user. member,
            fitness_class=self.fitness_class,
            price_paid=Decimal("100.00")
        )
        self.fitness_class.base_price = Decimal("500.00")
        self.fitness_class.save()
        reservation.refresh_from_db()
        self.assertEqual(reservation.price_paid, Decimal("100.00"))


class ReservationIntegrationPeakHourTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.instructor = User.objects.create_user(
            email="instructor@test.com",
            password="testpass123",
            is_instructor=True
        )
        self.user = User.objects. create_user(
            email="member@test.com",
            password="testpass123"
        )

    def test_reservation_applies_peak_hour_surcharge(self):
        peak_date = timezone.now() + timedelta(days=2)
        peak_date = peak_date.replace(hour=19, minute=0)
        peak_class = FitnessClass.objects.create(
            name="Peak Class",
            instructor=self.instructor,
            capacity=20,
            date_time=peak_date,
            base_price=Decimal("100.00")
        )
        self.client.force_authenticate(user=self.user)
        self.client.post("/api/reservations/", {"fitness_class_id": peak_class.id})
        reservation = Reservation.objects.get(member=self.user.member)
        self.assertEqual(reservation.price_paid, Decimal("125.00"))

    def test_reservation_no_surcharge_off_peak(self):
        off_peak_date = timezone.now() + timedelta(days=2)
        off_peak_date = off_peak_date.replace(hour=10, minute=0)
        off_peak_class = FitnessClass.objects.create(
            name="Off Peak Class",
            instructor=self.instructor,
            capacity=20,
            date_time=off_peak_date,
            base_price=Decimal("100.00")
        )
        self.client.force_authenticate(user=self.user)
        self.client.post("/api/reservations/", {"fitness_class_id": off_peak_class. id})
        reservation = Reservation.objects.get(member=self.user.member)
        self.assertEqual(reservation.price_paid, Decimal("100.00"))