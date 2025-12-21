from decimal import Decimal
from typing import Optional, Tuple
from datetime import datetime, timedelta
from django.utils import timezone


class PricingEngine:

    @staticmethod
    def calculate_price(base_price, membership_type, occupancy_rate, is_peak_hour):
        price = Decimal(base_price)

        if membership_type == 'PREMIUM':
            price *= Decimal('0.80')
        elif membership_type == 'STUDENT':
            price *= Decimal('0.50')

        if occupancy_rate >= 0.80:
            price *= Decimal('1.50')

        if is_peak_hour:
            price *= Decimal('1.25')

        return price. quantize(Decimal('0.01'))


class ReservationService:

    FREE_CANCELLATION_WINDOW = 24
    PARTIAL_REFUND_WINDOW = 12
    NO_REFUND_WINDOW = 12

    @classmethod
    def validate_reservation_time(cls, class_datetime:  datetime) -> Tuple[bool, str]:
        now = timezone.now()

        if class_datetime <= now:
            return False, "Cannot reserve classes in the past"

        min_advance_time = now + timedelta(hours=1)
        if class_datetime < min_advance_time:
            return False, "Reservations must be made at least 1 hour in advance"

        max_advance_time = now + timedelta(days=30)
        if class_datetime > max_advance_time:
            return False, "Cannot reserve classes more than 30 days in advance"

        return True, ""

    @classmethod
    def calculate_cancellation_fee(
        cls,
        original_price: Decimal,
        class_datetime: datetime,
        cancellation_time:  Optional[datetime] = None
    ) -> Decimal:
        if cancellation_time is None:
            cancellation_time = timezone.now()

        hours_before = (class_datetime - cancellation_time).total_seconds() / 3600

        if hours_before >= cls.FREE_CANCELLATION_WINDOW:
            return Decimal('0.00')

        elif hours_before >= cls.PARTIAL_REFUND_WINDOW:
            return (original_price * Decimal('0.50')).quantize(Decimal('0.01'))

        else:
            return original_price. quantize(Decimal('0.01'))

    @classmethod
    def check_conflicting_reservations(
        cls,
        user_id: int,
        class_datetime: datetime,
        class_duration_minutes: int = 60
    ) -> Tuple[bool, str]:
        hour = class_datetime.hour
        if hour < 6 or hour >= 22:
            return True, "Classes are only available between 6 AM and 10 PM"

        return False, ""


class CapacityCalculator:

    @staticmethod
    def can_book(current_bookings: int, capacity: int) -> bool:
        if capacity <= 0:
            return False
        return current_bookings < capacity

    @staticmethod
    def calculate_occupancy_rate(current_bookings: int, capacity: int) -> Decimal:
        if capacity <= 0:
            raise ValueError("Capacity must be positive")

        if current_bookings < 0:
            raise ValueError("Current bookings cannot be negative")

        rate = Decimal(current_bookings) / Decimal(capacity)
        return min(rate, Decimal('1.00'))

    @staticmethod
    def get_available_spots(current_bookings: int, capacity: int) -> int:
        available = capacity - current_bookings
        return max(0, available)

    @staticmethod
    def is_nearly_full(current_bookings: int, capacity: int, threshold: float = 0.9) -> bool:
        if capacity <= 0:
            return True

        occupancy = current_bookings / capacity
        return occupancy >= threshold

    @classmethod
    def calculate_optimal_capacity(
        cls,
        room_size_sqm: int,
        equipment_count: int,
        instructor_capacity: int
    ) -> int:
        space_capacity = room_size_sqm // 2

        equipment_capacity = equipment_count if equipment_count > 0 else 999

        instructor_limit = instructor_capacity if instructor_capacity > 0 else 999

        optimal = min(space_capacity, equipment_capacity, instructor_limit)

        return max(1, optimal)