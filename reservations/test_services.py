from decimal import Decimal
from datetime import timedelta, datetime, timezone as dt_timezone
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from .services import PricingEngine, ReservationService, CapacityCalculator


class PricingEngineUnitTests(TestCase):

    def setUp(self):
        self.base_price = Decimal("100.00")

    def test_standard_member_low_occupancy_off_peak(self):
        price = PricingEngine.calculate_price(
            base_price=self.base_price,
            membership_type="STANDARD",
            occupancy_rate=0.10,
            is_peak_hour=False
        )
        self.assertEqual(price, Decimal("100.00"))

    def test_premium_member_discount(self):
        price = PricingEngine.calculate_price(
            base_price=self.base_price,
            membership_type="PREMIUM",
            occupancy_rate=0.10,
            is_peak_hour=False
        )
        self.assertEqual(price, Decimal("80.00"))

    def test_student_member_discount(self):
        price = PricingEngine.calculate_price(
            base_price=self.base_price,
            membership_type="STUDENT",
            occupancy_rate=0.10,
            is_peak_hour=False
        )
        self.assertEqual(price, Decimal("50.00"))

    def test_surge_pricing_high_occupancy(self):
        price = PricingEngine.calculate_price(
            base_price=self.base_price,
            membership_type="STANDARD",
            occupancy_rate=0.85,
            is_peak_hour=False
        )
        self.assertEqual(price, Decimal("150.00"))

    def test_peak_hour_surcharge(self):
        price = PricingEngine.calculate_price(
            base_price=self.base_price,
            membership_type="STANDARD",
            occupancy_rate=0.10,
            is_peak_hour=True
        )
        self.assertEqual(price, Decimal("125.00"))

    def test_combined_premium_discount_and_surge(self):
        price = PricingEngine.calculate_price(
            base_price=self.base_price,
            membership_type="PREMIUM",
            occupancy_rate=0.85,
            is_peak_hour=False
        )
        self.assertEqual(price, Decimal("120.00"))

    def test_all_modifiers_combined(self):
        price = PricingEngine.calculate_price(
            base_price=self.base_price,
            membership_type="STUDENT",
            occupancy_rate=0.90,
            is_peak_hour=True
        )
        self.assertEqual(price, Decimal("93.75"))


class ReservationServiceValidationTests(TestCase):

    @patch("reservations.services.timezone.now")
    def test_validate_future_reservation(self, mock_now):
        mock_now.return_value = datetime(2025, 6, 15, 10, 0, 0, tzinfo=dt_timezone.utc)
        class_time = datetime(2025, 6, 16, 10, 0, 0, tzinfo=dt_timezone.utc)
        is_valid, error = ReservationService.validate_reservation_time(class_time)
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

    @patch("reservations.services.timezone.now")
    def test_validate_past_reservation_fails(self, mock_now):
        mock_now.return_value = datetime(2025, 6, 15, 10, 0, 0, tzinfo=dt_timezone.utc)
        class_time = datetime(2025, 6, 14, 10, 0, 0, tzinfo=dt_timezone.utc)
        is_valid, error = ReservationService.validate_reservation_time(class_time)
        self.assertFalse(is_valid)
        self.assertIn("past", error.lower())

    @patch("reservations.services.timezone.now")
    def test_validate_too_soon_reservation_fails(self, mock_now):
        mock_now.return_value = datetime(2025, 6, 15, 10, 0, 0, tzinfo=dt_timezone.utc)
        class_time = datetime(2025, 6, 15, 10, 30, 0, tzinfo=dt_timezone.utc)
        is_valid, error = ReservationService.validate_reservation_time(class_time)
        self.assertFalse(is_valid)
        self.assertIn("1 hour", error.lower())

    @patch("reservations.services.timezone.now")
    def test_validate_too_far_future_fails(self, mock_now):
        mock_now.return_value = datetime(2025, 6, 15, 10, 0, 0, tzinfo=dt_timezone.utc)
        class_time = datetime(2025, 7, 20, 10, 0, 0, tzinfo=dt_timezone.utc)
        is_valid, error = ReservationService.validate_reservation_time(class_time)
        self.assertFalse(is_valid)
        self.assertIn("30 days", error.lower())


class ReservationServiceCancellationTests(TestCase):

    @patch("reservations.services.timezone.now")
    def test_cancellation_free_window(self, mock_now):
        mock_now.return_value = datetime(2025, 6, 15, 10, 0, 0, tzinfo=dt_timezone.utc)
        class_time = datetime(2025, 6, 17, 10, 0, 0, tzinfo=dt_timezone.utc)
        fee = ReservationService.calculate_cancellation_fee(
            original_price=Decimal("100.00"),
            class_datetime=class_time
        )
        self.assertEqual(fee, Decimal("0.00"))

    @patch("reservations.services.timezone.now")
    def test_cancellation_partial_refund_window(self, mock_now):
        mock_now.return_value = datetime(2025, 6, 15, 10, 0, 0, tzinfo=dt_timezone.utc)
        class_time = datetime(2025, 6, 16, 4, 0, 0, tzinfo=dt_timezone.utc)
        fee = ReservationService.calculate_cancellation_fee(
            original_price=Decimal("100.00"),
            class_datetime=class_time
        )
        self.assertEqual(fee, Decimal("50.00"))

    @patch("reservations.services.timezone.now")
    def test_cancellation_no_refund_window(self, mock_now):
        mock_now.return_value = datetime(2025, 6, 15, 10, 0, 0, tzinfo=dt_timezone.utc)
        class_time = datetime(2025, 6, 15, 16, 0, 0, tzinfo=dt_timezone.utc)
        fee = ReservationService.calculate_cancellation_fee(
            original_price=Decimal("100.00"),
            class_datetime=class_time
        )
        self.assertEqual(fee, Decimal("100.00"))

    def test_cancellation_with_custom_time(self):
        class_time = datetime(2025, 6, 20, 10, 0, 0, tzinfo=dt_timezone.utc)
        cancellation_time = datetime(2025, 6, 18, 10, 0, 0, tzinfo=dt_timezone.utc)
        fee = ReservationService.calculate_cancellation_fee(
            original_price=Decimal("100.00"),
            class_datetime=class_time,
            cancellation_time=cancellation_time
        )
        self.assertEqual(fee, Decimal("0.00"))


class ReservationServiceConflictTests(TestCase):

    def test_check_conflicting_reservations_valid_time(self):
        class_time = datetime(2025, 6, 15, 14, 0, 0, tzinfo=dt_timezone.utc)
        has_conflict, message = ReservationService.check_conflicting_reservations(
            user_id=1,
            class_datetime=class_time
        )
        self.assertFalse(has_conflict)
        self.assertEqual(message, "")

    def test_check_conflicting_reservations_too_early(self):
        class_time = datetime(2025, 6, 15, 5, 0, 0, tzinfo=dt_timezone.utc)
        has_conflict, message = ReservationService.check_conflicting_reservations(
            user_id=1,
            class_datetime=class_time
        )
        self.assertTrue(has_conflict)
        self.assertIn("6 AM", message)

    def test_check_conflicting_reservations_too_late(self):
        class_time = datetime(2025, 6, 15, 22, 0, 0, tzinfo=dt_timezone.utc)
        has_conflict, message = ReservationService.check_conflicting_reservations(
            user_id=1,
            class_datetime=class_time
        )
        self.assertTrue(has_conflict)
        self.assertIn("10 PM", message)


class CapacityCalculatorBookingTests(TestCase):

    def test_can_book_with_available_capacity(self):
        result = CapacityCalculator.can_book(current_bookings=5, capacity=20)
        self.assertTrue(result)

    def test_can_book_at_full_capacity(self):
        result = CapacityCalculator.can_book(current_bookings=20, capacity=20)
        self.assertFalse(result)

    def test_can_book_with_zero_capacity(self):
        result = CapacityCalculator.can_book(current_bookings=0, capacity=0)
        self.assertFalse(result)

    def test_can_book_one_spot_remaining(self):
        result = CapacityCalculator.can_book(current_bookings=19, capacity=20)
        self.assertTrue(result)


class CapacityCalculatorOccupancyTests(TestCase):

    def test_calculate_occupancy_rate_empty(self):
        rate = CapacityCalculator.calculate_occupancy_rate(current_bookings=0, capacity=20)
        self.assertEqual(rate, Decimal("0.00"))

    def test_calculate_occupancy_rate_full(self):
        rate = CapacityCalculator.calculate_occupancy_rate(current_bookings=20, capacity=20)
        self.assertEqual(rate, Decimal("1.00"))

    def test_calculate_occupancy_rate_half(self):
        rate = CapacityCalculator.calculate_occupancy_rate(current_bookings=10, capacity=20)
        self.assertEqual(rate, Decimal("0.50"))

    def test_calculate_occupancy_rate_zero_capacity_error(self):
        with self.assertRaises(ValueError):
            CapacityCalculator.calculate_occupancy_rate(current_bookings=0, capacity=0)

    def test_calculate_occupancy_rate_negative_bookings_error(self):
        with self.assertRaises(ValueError):
            CapacityCalculator.calculate_occupancy_rate(current_bookings=-1, capacity=20)


class CapacityCalculatorAvailableTests(TestCase):

    def test_get_available_spots_plenty_room(self):
        available = CapacityCalculator.get_available_spots(current_bookings=5, capacity=20)
        self.assertEqual(available, 15)

    def test_get_available_spots_none_remaining(self):
        available = CapacityCalculator.get_available_spots(current_bookings=20, capacity=20)
        self.assertEqual(available, 0)

    def test_get_available_spots_negative_returns_zero(self):
        available = CapacityCalculator.get_available_spots(current_bookings=25, capacity=20)
        self.assertEqual(available, 0)


class CapacityCalculatorNearlyFullTests(TestCase):

    def test_is_nearly_full_above_threshold(self):
        result = CapacityCalculator.is_nearly_full(current_bookings=18, capacity=20)
        self.assertTrue(result)

    def test_is_nearly_full_below_threshold(self):
        result = CapacityCalculator.is_nearly_full(current_bookings=17, capacity=20)
        self.assertFalse(result)

    def test_is_nearly_full_custom_threshold(self):
        result = CapacityCalculator.is_nearly_full(
            current_bookings=16,
            capacity=20,
            threshold=0.8
        )
        self.assertTrue(result)


class CapacityCalculatorOptimalTests(TestCase):

    def test_calculate_optimal_capacity_room_limiting(self):
        capacity = CapacityCalculator.calculate_optimal_capacity(
            room_size_sqm=20,
            equipment_count=50,
            instructor_capacity=30
        )
        self.assertEqual(capacity, 10)

    def test_calculate_optimal_capacity_equipment_limiting(self):
        capacity = CapacityCalculator.calculate_optimal_capacity(
            room_size_sqm=100,
            equipment_count=5,
            instructor_capacity=30
        )
        self.assertEqual(capacity, 5)

    def test_calculate_optimal_capacity_instructor_limiting(self):
        capacity = CapacityCalculator.calculate_optimal_capacity(
            room_size_sqm=100,
            equipment_count=50,
            instructor_capacity=8
        )
        self.assertEqual(capacity, 8)

    def test_calculate_optimal_capacity_minimum_one(self):
        capacity = CapacityCalculator.calculate_optimal_capacity(
            room_size_sqm=1,
            equipment_count=0,
            instructor_capacity=0
        )
        self.assertEqual(capacity, 1)


class ReservationServiceIntegrationTests(TestCase):

    @patch("reservations.services.timezone.now")
    def test_complete_reservation_flow_success(self, mock_now):
        mock_now.return_value = datetime(2025, 6, 15, 10, 0, 0, tzinfo=dt_timezone.utc)
        class_time = datetime(2025, 6, 16, 14, 0, 0, tzinfo=dt_timezone.utc)
        is_valid, error = ReservationService.validate_reservation_time(class_time)
        self.assertTrue(is_valid)
        has_conflict, conflict_msg = ReservationService.check_conflicting_reservations(
            user_id=1,
            class_datetime=class_time
        )
        self.assertFalse(has_conflict)
        can_book = CapacityCalculator.can_book(current_bookings=5, capacity=20)
        self.assertTrue(can_book)
        price = PricingEngine.calculate_price(
            base_price=Decimal("100.00"),
            membership_type="STANDARD",
            occupancy_rate=0.25,
            is_peak_hour=False
        )
        self.assertEqual(price, Decimal("100.00"))

    @patch("reservations.services.timezone.now")
    def test_complete_cancellation_flow(self, mock_now):
        mock_now.return_value = datetime(2025, 6, 15, 10, 0, 0, tzinfo=dt_timezone.utc)
        class_time = datetime(2025, 6, 17, 14, 0, 0, tzinfo=dt_timezone.utc)
        fee = ReservationService.calculate_cancellation_fee(
            original_price=Decimal("100.00"),
            class_datetime=class_time
        )
        self.assertEqual(fee, Decimal("0.00"))
