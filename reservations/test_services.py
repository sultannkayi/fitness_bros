from decimal import Decimal
from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from . services import PricingEngine, ReservationService, CapacityCalculator


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
            base_price=self. base_price,
            membership_type="STUDENT",
            occupancy_rate=0.90,
            is_peak_hour=True
        )
        self.assertEqual(price, Decimal("93.75"))


class ReservationServiceValidationTests(TestCase):

    @patch("reservations.services.timezone. now")
    def test_validate_future_reservation(self, mock_now):
        mock_now.return_value = timezone.datetime(2025, 6, 15, 10, 0, 0, tzinfo=timezone.utc)
        class_time = timezone.datetime(2025, 6, 16, 10, 0, 0, tzinfo=timezone.utc)
        is_valid, error = ReservationService.validate_reservation_time(class_time)
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

    @patch("reservations.services.timezone.now")
    def test_validate_past_reservation_fails(self, mock_now):
        mock_now.return_value = timezone.datetime(2025, 6, 15, 10, 0, 0, tzinfo=timezone.utc)
        class_time = timezone.datetime(2025, 6, 14, 10, 0, 0, tzinfo=timezone.utc)
        is_valid, error = ReservationService.validate_reservation_time(class_time)
        self.assertFalse(is_valid)
        self.assertIn("past", error. lower())

    @patch("reservations.services.timezone.now")
    def test_validate_too_soon_reservation_fails(self, mock_now):
        mock_now.return_value = timezone.datetime(2025, 6, 15, 10, 0, 0, tzinfo=timezone. utc)
        class_time = timezone.datetime(2025, 6, 15, 10, 30, 0, tzinfo=timezone.utc)
        is_valid, error = ReservationService.validate_reservation_time(class_time)
        self.assertFalse(is_valid)
        self.assertIn("1 hour", error.lower())

    @patch("reservations.services.timezone.now")
    def test_validate_too_far_future_fails(self, mock_now):
        mock_now.return_value = timezone.datetime(2025, 6, 15, 10, 0, 0, tzinfo=timezone.utc)
        class_time = timezone.datetime(2025, 7, 20, 10, 0, 0, tzinfo=timezone.utc)
        is_valid, error = ReservationService.validate_reservation_time(class_time)
        self.assertFalse(is_valid)
        self.assertIn("30 days", error.lower())


class ReservationServiceCancellationTests(TestCase):

    @patch("reservations.services.timezone.now")
    def test_cancellation_free_window(self, mock_now):
        mock_now.return_value = timezone.datetime(2025, 6, 15, 10, 0, 0, tzinfo=timezone.utc)
        class_time = timezone.datetime(2025, 6, 17, 10, 0, 0, tzinfo=timezone.utc)
        fee = ReservationService.calculate_cancellation_fee(
            original_price=Decimal("100.00"),
            class_datetime=class_time
        )
        self.assertEqual(fee, Decimal("0.00"))

    @patch("reservations.services.timezone.now")
    def test_cancellation_partial_refund_window(self, mock_now):
        mock_now.return_value = timezone.datetime(2025, 6, 15, 10, 0, 0, tzinfo=timezone.utc)
        class_time = timezone. datetime(2025, 6, 16, 4, 0, 0, tzinfo=timezone.utc)
        fee = ReservationService. calculate_cancellation_fee(
            original_price=Decimal("100.00"),
            class_datetime=class_time
        )
        self.assertEqual(fee, Decimal("50.00"))

    @patch("reservations.services.timezone.now")
    def test_cancellation_no_refund_window(self, mock_now):
        mock_now.return_value = timezone. datetime(2025, 6, 15, 10, 0, 0, tzinfo=timezone.utc)
        class_time = timezone.datetime(2025, 6, 15, 16, 0, 0, tzinfo=timezone.utc)
        fee = ReservationService. calculate_cancellation_fee(
            original_price=Decimal("100.00"),
            class_datetime=class_time
        )
        self.assertEqual(fee, Decimal("100.00"))

    def test_cancellation_with_custom_time(self):
        class_time = timezone.datetime(2025, 6, 20, 10, 0, 0, tzinfo=timezone.utc)
        cancellation_time = timezone.datetime(2025, 6, 18, 10, 0, 0, tzinfo=timezone.utc)
        fee = ReservationService.calculate_cancellation_fee(
            original_price=Decimal("100.00"),
            class_datetime=class_time,
            cancellation_time=cancellation_time
        )
        self.assertEqual(fee, Decimal("0.00"))


class ReservationServiceConflictTests(TestCase):

    def test_check_conflicting_reservations_valid_time(self):
        class_time = timezone.datetime(2025, 6, 15, 14, 0, 0, tzinfo=timezone.utc)
        has_conflict, message = ReservationService.check_conflicting_reservations(
            user_id=1,
            class_datetime=class_time
        )
        self.assertFalse(has_conflict)
        self.assertEqual(message, "")

    def test_check_conflicting_reservations_too_early(self):
        class_time = timezone.datetime(2025, 6, 15, 5, 0, 0, tzinfo=timezone.utc)
        has_conflict, message = ReservationService.check_conflicting_reservations(
            user_id=1,
            class_datetime=class_time
        )
        self.assertTrue(has_conflict)
        self.assertIn("6 AM", message)

    def test_check_conflicting_reservations_too_late(self):
        class_time = timezone.datetime(2025, 6, 15, 22, 0, 0, tzinfo=timezone.utc)
        has_conflict, message = ReservationService.check_conflicting_reservations(
            user_id=1,
            class_datetime=class_time
        )
"""
Unit tests for Reservations Service Layer with TDD and Mocking.
Tests ReservationService and CapacityCalculator with various scenarios.
"""
import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, Mock
from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError

from reservations.services import PricingEngine, ReservationService, CapacityCalculator


class PricingEngineTests(TestCase):
    """Unit tests for PricingEngine with TDD approach."""
    
    def setUp(self):
        self.base_price = Decimal('100.00')
    
    def test_standard_member_low_occupancy_off_peak(self):
        """Happy path: Standard member, low occupancy, off-peak."""
        price = PricingEngine.calculate_price(
            self.base_price, 'STANDARD', 0.10, False
        )
        self.assertEqual(price, Decimal('100.00'))
    
    def test_premium_member_discount(self):
        """Happy path: Premium member gets 20% discount."""
        price = PricingEngine.calculate_price(
            self.base_price, 'PREMIUM', 0.10, False
        )
        self.assertEqual(price, Decimal('80.00'))
    
    def test_student_member_discount(self):
        """Happy path: Student member gets 50% discount."""
        price = PricingEngine.calculate_price(
            self.base_price, 'STUDENT', 0.10, False
        )
        self.assertEqual(price, Decimal('50.00'))
    
    def test_surge_pricing_high_occupancy(self):
        """Edge case: High occupancy (>80%) triggers surge pricing."""
        price = PricingEngine.calculate_price(
            self.base_price, 'STANDARD', 0.85, False
        )
        # 100 * 1.5 = 150
        self.assertEqual(price, Decimal('150.00'))
    
    def test_peak_hour_surcharge(self):
        """Edge case: Peak hour adds 25% surcharge."""
        price = PricingEngine.calculate_price(
            self.base_price, 'STANDARD', 0.50, True
        )
        # 100 * 1.25 = 125
        self.assertEqual(price, Decimal('125.00'))
    
    def test_combined_premium_discount_and_surge(self):
        """Complex: Premium discount + surge pricing."""
        price = PricingEngine.calculate_price(
            self.base_price, 'PREMIUM', 0.90, False
        )
        # 100 * 0.8 = 80, then 80 * 1.5 = 120
        self.assertEqual(price, Decimal('120.00'))
    
    def test_all_modifiers_combined(self):
        """Complex: Student + surge + peak hour."""
        price = PricingEngine.calculate_price(
            self.base_price, 'STUDENT', 0.85, True
        )
        # 100 * 0.5 = 50, * 1.5 = 75, * 1.25 = 93.75
        self.assertEqual(price, Decimal('93.75'))


class ReservationServiceTests(TestCase):
    """Unit tests for ReservationService with mocking."""
    
    @patch('reservations.services.timezone.now')
    def test_validate_future_reservation(self, mock_now):
        """Happy path: Future reservation is valid."""
        mock_now.return_value = datetime(2025, 12, 15, 10, 0, 0)
        
        future_time = datetime(2025, 12, 16, 14, 0, 0)
        is_valid, message = ReservationService.validate_reservation_time(future_time)
        
        self.assertTrue(is_valid)
        self.assertEqual(message, "")
    
    @patch('reservations.services.timezone.now')
    def test_validate_past_reservation_fails(self, mock_now):
        """Error scenario: Past reservation should fail."""
        mock_now.return_value = datetime(2025, 12, 15, 10, 0, 0)
        
        past_time = datetime(2025, 12, 14, 9, 0, 0)
        is_valid, message = ReservationService.validate_reservation_time(past_time)
        
        self.assertFalse(is_valid)
        self.assertIn("past", message.lower())
    
    @patch('reservations.services.timezone.now')
    def test_validate_too_soon_reservation_fails(self, mock_now):
        """Error scenario: Less than 1 hour advance should fail."""
        mock_now.return_value = datetime(2025, 12, 15, 10, 0, 0)
        
        too_soon = datetime(2025, 12, 15, 10, 30, 0)  # Only 30 mins advance
        is_valid, message = ReservationService.validate_reservation_time(too_soon)
        
        self.assertFalse(is_valid)
        self.assertIn("1 hour", message)
    
    @patch('reservations.services.timezone.now')
    def test_validate_too_far_future_fails(self, mock_now):
        """Error scenario: More than 30 days advance should fail."""
        mock_now.return_value = datetime(2025, 12, 15, 10, 0, 0)
        
        too_far = datetime(2026, 2, 1, 10, 0, 0)  # 48 days ahead
        is_valid, message = ReservationService.validate_reservation_time(too_far)
        
        self.assertFalse(is_valid)
        self.assertIn("30 days", message)
    
    @patch('reservations.services.timezone.now')
    def test_cancellation_free_window(self, mock_now):
        """Happy path: Free cancellation >24h before."""
        mock_now.return_value = datetime(2025, 12, 15, 10, 0, 0)
        class_time = datetime(2025, 12, 17, 10, 0, 0)  # 48 hours ahead
        
        fee = ReservationService.calculate_cancellation_fee(
            Decimal('100.00'), class_time
        )
        
        self.assertEqual(fee, Decimal('0.00'))
    
    @patch('reservations.services.timezone.now')
    def test_cancellation_partial_refund_window(self, mock_now):
        """Edge case: 50% fee for 12-24h window."""
        mock_now.return_value = datetime(2025, 12, 15, 10, 0, 0)
        class_time = datetime(2025, 12, 15, 22, 0, 0)  # 12 hours ahead
        
        fee = ReservationService.calculate_cancellation_fee(
            Decimal('100.00'), class_time
        )
        
        self.assertEqual(fee, Decimal('50.00'))
    
    @patch('reservations.services.timezone.now')
    def test_cancellation_no_refund_window(self, mock_now):
        """Error scenario: Full charge <12h before."""
        mock_now.return_value = datetime(2025, 12, 15, 10, 0, 0)
        class_time = datetime(2025, 12, 15, 15, 0, 0)  # 5 hours ahead
        
        fee = ReservationService.calculate_cancellation_fee(
            Decimal('100.00'), class_time
        )
        
        self.assertEqual(fee, Decimal('100.00'))
    
    def test_cancellation_with_custom_time(self):
        """Mocking: Custom cancellation time."""
        class_time = datetime(2025, 12, 20, 10, 0, 0)
        cancel_time = datetime(2025, 12, 18, 10, 0, 0)  # 48h before
        
        fee = ReservationService.calculate_cancellation_fee(
            Decimal('150.00'), class_time, cancel_time
        )
        
        self.assertEqual(fee, Decimal('0.00'))
    
    def test_check_conflicting_reservations_valid_time(self):
        """Happy path: Normal business hours."""
        class_time = datetime(2025, 12, 15, 14, 0, 0)  # 2 PM
        
        has_conflict, message = ReservationService.check_conflicting_reservations(
            user_id=1, class_datetime=class_time
        )
        
        self.assertFalse(has_conflict)
    
    def test_check_conflicting_reservations_too_early(self):
        """Error scenario: Class before 6 AM."""
        class_time = datetime(2025, 12, 15, 5, 0, 0)  # 5 AM
        
        has_conflict, message = ReservationService.check_conflicting_reservations(
            user_id=1, class_datetime=class_time
        )
        
        self.assertTrue(has_conflict)
        self.assertIn("6 AM", message)
    
    def test_check_conflicting_reservations_too_late(self):
        """Error scenario: Class after 10 PM."""
        class_time = datetime(2025, 12, 15, 22, 30, 0)  # 10:30 PM
        
        has_conflict, message = ReservationService.check_conflicting_reservations(
            user_id=1, class_datetime=class_time
        )
        
        self.assertTrue(has_conflict)
        self.assertIn("10 PM", message)


class CapacityCalculatorBookingTests(TestCase):

    def test_can_book_with_available_capacity(self):
        result = CapacityCalculator. can_book(current_bookings=5, capacity=20)
        self.assertTrue(result)

    def test_can_book_at_full_capacity(self):
        result = CapacityCalculator. can_book(current_bookings=20, capacity=20)
        self.assertFalse(result)

    def test_can_book_with_zero_capacity(self):
        result = CapacityCalculator. can_book(current_bookings=0, capacity=0)
        self.assertFalse(result)

    def test_can_book_one_spot_remaining(self):
        result = CapacityCalculator.can_book(current_bookings=19, capacity=20)
        self.assertTrue(result)


class CapacityCalculatorOccupancyTests(TestCase):

    def test_calculate_occupancy_rate_empty(self):
        rate = CapacityCalculator. calculate_occupancy_rate(current_bookings=0, capacity=20)
        self.assertEqual(rate, Decimal("0.00"))

    def test_calculate_occupancy_rate_full(self):
        rate = CapacityCalculator.calculate_occupancy_rate(current_bookings=20, capacity=20)
        self.assertEqual(rate, Decimal("1.00"))

    def test_calculate_occupancy_rate_half(self):
        rate = CapacityCalculator.calculate_occupancy_rate(current_bookings=10, capacity=20)
        self.assertEqual(rate, Decimal("0.50"))

    def test_calculate_occupancy_rate_zero_capacity_error(self):
        with self. assertRaises(ValueError):
            CapacityCalculator.calculate_occupancy_rate(current_bookings=0, capacity=0)

    def test_calculate_occupancy_rate_negative_bookings_error(self):
        with self.assertRaises(ValueError):
            CapacityCalculator. calculate_occupancy_rate(current_bookings=-1, capacity=20)


class CapacityCalculatorAvailableTests(TestCase):

    def test_get_available_spots_plenty_room(self):
        available = CapacityCalculator. get_available_spots(current_bookings=5, capacity=20)
        self.assertEqual(available, 15)

    def test_get_available_spots_none_remaining(self):
        available = CapacityCalculator.get_available_spots(current_bookings=20, capacity=20)
        self.assertEqual(available, 0)

    def test_get_available_spots_negative_returns_zero(self):
        available = CapacityCalculator.get_available_spots(current_bookings=25, capacity=20)
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


class CapacityCalculatorOptimalTests(TestCase):

    def test_calculate_optimal_capacity_room_limiting(self):
        capacity = CapacityCalculator. calculate_optimal_capacity(
            room_size_sqm=20,
            equipment_count=50,
            instructor_capacity=30
        )
        self.assertEqual(capacity, 10)

    def test_calculate_optimal_capacity_equipment_limiting(self):
        capacity = CapacityCalculator. calculate_optimal_capacity(
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
class CapacityCalculatorTests(TestCase):
    """Unit tests for CapacityCalculator."""
    
    def test_can_book_with_available_capacity(self):
        """Happy path: Booking allowed when space available."""
        result = CapacityCalculator.can_book(current_bookings=5, capacity=10)
        self.assertTrue(result)
    
    def test_can_book_at_full_capacity(self):
        """Edge case: No booking when at capacity."""
        result = CapacityCalculator.can_book(current_bookings=10, capacity=10)
        self.assertFalse(result)
    
    def test_can_book_with_zero_capacity(self):
        """Error scenario: Zero capacity always returns False."""
        result = CapacityCalculator.can_book(current_bookings=0, capacity=0)
        self.assertFalse(result)
    
    def test_can_book_one_spot_remaining(self):
        """Edge case: Last spot available."""
        result = CapacityCalculator.can_book(current_bookings=9, capacity=10)
        self.assertTrue(result)
    
    def test_calculate_occupancy_rate_empty(self):
        """Happy path: 0% occupancy."""
        rate = CapacityCalculator.calculate_occupancy_rate(0, 10)
        self.assertEqual(rate, Decimal('0.00'))
    
    def test_calculate_occupancy_rate_full(self):
        """Edge case: 100% occupancy."""
        rate = CapacityCalculator.calculate_occupancy_rate(10, 10)
        self.assertEqual(rate, Decimal('1.00'))
    
    def test_calculate_occupancy_rate_half(self):
        """Happy path: 50% occupancy."""
        rate = CapacityCalculator.calculate_occupancy_rate(5, 10)
        self.assertEqual(rate, Decimal('0.50'))
    
    def test_calculate_occupancy_rate_zero_capacity_error(self):
        """Error scenario: Zero capacity raises ValueError."""
        with self.assertRaises(ValueError) as context:
            CapacityCalculator.calculate_occupancy_rate(5, 0)
        self.assertIn("positive", str(context.exception).lower())
    
    def test_calculate_occupancy_rate_negative_bookings_error(self):
        """Error scenario: Negative bookings raises ValueError."""
        with self.assertRaises(ValueError) as context:
            CapacityCalculator.calculate_occupancy_rate(-1, 10)
        self.assertIn("negative", str(context.exception).lower())
    
    def test_get_available_spots_plenty_room(self):
        """Happy path: Many spots available."""
        spots = CapacityCalculator.get_available_spots(3, 10)
        self.assertEqual(spots, 7)
    
    def test_get_available_spots_none_remaining(self):
        """Edge case: No spots remaining."""
        spots = CapacityCalculator.get_available_spots(10, 10)
        self.assertEqual(spots, 0)
    
    def test_get_available_spots_negative_returns_zero(self):
        """Edge case: Over capacity returns 0 (shouldn't happen but safe)."""
        spots = CapacityCalculator.get_available_spots(12, 10)
        self.assertEqual(spots, 0)
    
    def test_is_nearly_full_above_threshold(self):
        """Happy path: Class is nearly full."""
        result = CapacityCalculator.is_nearly_full(9, 10, threshold=0.9)
        self.assertTrue(result)
    
    def test_is_nearly_full_below_threshold(self):
        """Happy path: Class is not nearly full."""
        result = CapacityCalculator.is_nearly_full(5, 10, threshold=0.9)
        self.assertFalse(result)
    
    def test_is_nearly_full_custom_threshold(self):
        """Edge case: Custom threshold."""
        result = CapacityCalculator.is_nearly_full(7, 10, threshold=0.6)
        self.assertTrue(result)
    
    def test_calculate_optimal_capacity_room_limiting(self):
        """Happy path: Room size is limiting factor."""
        capacity = CapacityCalculator.calculate_optimal_capacity(
            room_size_sqm=50,  # 25 people
            equipment_count=30,
            instructor_capacity=40
        )
        self.assertEqual(capacity, 25)
    
    def test_calculate_optimal_capacity_equipment_limiting(self):
        """Edge case: Equipment is limiting factor."""
        capacity = CapacityCalculator.calculate_optimal_capacity(
            room_size_sqm=100,  # 50 people
            equipment_count=10,  # Only 10 equipment
            instructor_capacity=40
        )
        self.assertEqual(capacity, 10)
    
    def test_calculate_optimal_capacity_instructor_limiting(self):
        """Edge case: Instructor capacity is limiting factor."""
        capacity = CapacityCalculator.calculate_optimal_capacity(
            room_size_sqm=100,  # 50 people
            equipment_count=30,
            instructor_capacity=15  # Instructor can handle max 15
        )
        self.assertEqual(capacity, 15)
    
    def test_calculate_optimal_capacity_minimum_one(self):
        """Edge case: Always return at least 1."""
        capacity = CapacityCalculator.calculate_optimal_capacity(
            room_size_sqm=1,  # Tiny room
            equipment_count=0,
            instructor_capacity=0
        )
        self.assertEqual(capacity, 1)


class ReservationServiceIntegrationTests(TestCase):

    @patch("reservations.services.timezone.now")
    def test_complete_reservation_flow_success(self, mock_now):
        mock_now.return_value = timezone.datetime(2025, 6, 15, 10, 0, 0, tzinfo=timezone.utc)
        class_time = timezone.datetime(2025, 6, 16, 14, 0, 0, tzinfo=timezone.utc)
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
        mock_now.return_value = timezone.datetime(2025, 6, 15, 10, 0, 0, tzinfo=timezone.utc)
        class_time = timezone.datetime(2025, 6, 17, 14, 0, 0, tzinfo=timezone.utc)
        fee = ReservationService.calculate_cancellation_fee(
            original_price=Decimal("100.00"),
            class_datetime=class_time
        )
        self.assertEqual(fee, Decimal("0.00"))
    """Integration tests with mocking for ReservationService."""
    
    @patch('reservations.services.timezone.now')
    def test_complete_reservation_flow_success(self, mock_now):
        """Integration: Complete successful reservation flow."""
        mock_now.return_value = datetime(2025, 12, 15, 10, 0, 0)
        
        # Step 1: Validate reservation time
        class_time = datetime(2025, 12, 20, 18, 0, 0)
        is_valid, _ = ReservationService.validate_reservation_time(class_time)
        self.assertTrue(is_valid)
        
        # Step 2: Check capacity
        can_book = CapacityCalculator.can_book(5, 10)
        self.assertTrue(can_book)
        
        # Step 3: Calculate price
        occupancy = CapacityCalculator.calculate_occupancy_rate(5, 10)
        price = PricingEngine.calculate_price(
            Decimal('100.00'), 'PREMIUM', occupancy, True
        )
        
        # Premium (80) * peak (1.25) = 100
        self.assertEqual(price, Decimal('100.00'))
    
    @patch('reservations.services.timezone.now')
    def test_complete_cancellation_flow(self, mock_now):
        """Integration: Complete cancellation flow."""
        mock_now.return_value = datetime(2025, 12, 15, 10, 0, 0)
        
        # Original reservation
        class_time = datetime(2025, 12, 20, 18, 0, 0)
        original_price = Decimal('100.00')
        
        # Cancel 3 days before (free cancellation)
        fee = ReservationService.calculate_cancellation_fee(
            original_price, class_time
        )
        
        self.assertEqual(fee, Decimal('0.00'))
        
        # Free up capacity
        new_spots = CapacityCalculator.get_available_spots(4, 10)
        self.assertEqual(new_spots, 6)
