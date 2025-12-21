"""
Reservations Service Layer
Business logic for reservation management, pricing, and capacity control.
"""
from decimal import Decimal
from typing import Optional, Tuple
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError


class PricingEngine:
    """
    Dynamic pricing engine for fitness class reservations.
    Calculates prices based on membership type, occupancy, and time of day.
    """

    @staticmethod
    def calculate_price(base_price, membership_type, occupancy_rate, is_peak_hour):
        """
        Calculate dynamic price for a class reservation.
        
        Args:
            base_price: Base price of the class
            membership_type: User's membership type (STANDARD, PREMIUM, STUDENT)
            occupancy_rate: Current occupancy rate (0.0 to 1.0)
            is_peak_hour: Whether it's peak hour (6-8am, 5-8pm)
            
        Returns:
            Final price as Decimal
        """
        price = Decimal(base_price)

        # 1️⃣ Üyelik indirimi
        if membership_type == 'PREMIUM':
            price *= Decimal('0.80')
        elif membership_type == 'STUDENT':
            price *= Decimal('0.50')

        # 2️⃣ Surge Pricing (%80 üzeri doluluk)
        if occupancy_rate >= 0.80:
            price *= Decimal('1.50')

        # 3️⃣ Peak hour
        if is_peak_hour:
            price *= Decimal('1.25')

        return price.quantize(Decimal('0.01'))


class ReservationService:
    """
    Service for managing class reservations.
    Handles reservation validation, cancellation, and business rules.
    """
    
    # Cancellation policy (hours before class)
    FREE_CANCELLATION_WINDOW = 24  # Free cancellation if >24h before
    PARTIAL_REFUND_WINDOW = 12     # 50% refund if 12-24h before
    NO_REFUND_WINDOW = 12          # No refund if <12h before
    
    @classmethod
    def validate_reservation_time(cls, class_datetime: datetime) -> Tuple[bool, str]:
        """
        Validate if a class can be reserved based on timing rules.
        
        Args:
            class_datetime: DateTime of the fitness class
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        now = timezone.now()
        
        # Rule 1: Cannot reserve past classes
        if class_datetime <= now:
            return False, "Cannot reserve classes in the past"
        
        # Rule 2: Must reserve at least 1 hour in advance
        min_advance_time = now + timedelta(hours=1)
        if class_datetime < min_advance_time:
            return False, "Reservations must be made at least 1 hour in advance"
        
        # Rule 3: Cannot reserve more than 30 days in advance
        max_advance_time = now + timedelta(days=30)
        if class_datetime > max_advance_time:
            return False, "Cannot reserve classes more than 30 days in advance"
        
        return True, ""
    
    @classmethod
    def calculate_cancellation_fee(
        cls,
        original_price: Decimal,
        class_datetime: datetime,
        cancellation_time: Optional[datetime] = None
    ) -> Decimal:
        """
        Calculate cancellation fee based on timing.
        
        Args:
            original_price: Original reservation price
            class_datetime: DateTime of the fitness class
            cancellation_time: Time of cancellation (defaults to now)
            
        Returns:
            Cancellation fee amount
        """
        if cancellation_time is None:
            cancellation_time = timezone.now()
        
        hours_before = (class_datetime - cancellation_time).total_seconds() / 3600
        
        # Free cancellation window
        if hours_before >= cls.FREE_CANCELLATION_WINDOW:
            return Decimal('0.00')
        
        # Partial refund window (charge 50%)
        elif hours_before >= cls.PARTIAL_REFUND_WINDOW:
            return (original_price * Decimal('0.50')).quantize(Decimal('0.01'))
        
        # No refund window (charge 100%)
        else:
            return original_price.quantize(Decimal('0.01'))
    
    @classmethod
    def check_conflicting_reservations(
        cls,
        user_id: int,
        class_datetime: datetime,
        class_duration_minutes: int = 60
    ) -> Tuple[bool, str]:
        """
        Check if user has conflicting reservations at the same time.
        
        Args:
            user_id: User's ID
            class_datetime: DateTime of the new class
            class_duration_minutes: Duration of the class
            
        Returns:
            Tuple of (has_conflict, conflict_message)
        """
        # This would query database in real implementation
        # For now, returning basic validation
        
        # Check if class is during reasonable hours (6am - 10pm)
        hour = class_datetime.hour
        if hour < 6 or hour >= 22:
            return True, "Classes are only available between 6 AM and 10 PM"
        
        return False, ""


class CapacityCalculator:
    """
    Service for calculating and managing class capacity.
    Handles capacity checks, utilization rates, and booking limits.
    """
    
    @staticmethod
    def can_book(current_bookings: int, capacity: int) -> bool:
        """
        Check if a class can accept more bookings.
        
        Args:
            current_bookings: Current number of bookings
            capacity: Maximum capacity
            
        Returns:
            True if booking is allowed, False otherwise
        """
        if capacity <= 0:
            return False
        return current_bookings < capacity
    
    @staticmethod
    def calculate_occupancy_rate(current_bookings: int, capacity: int) -> Decimal:
        """
        Calculate occupancy rate as a percentage.
        
        Args:
            current_bookings: Current number of bookings
            capacity: Maximum capacity
            
        Returns:
            Occupancy rate (0.0 to 1.0)
            
        Raises:
            ValueError: If capacity is zero or negative
        """
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        
        if current_bookings < 0:
            raise ValueError("Current bookings cannot be negative")
        
        rate = Decimal(current_bookings) / Decimal(capacity)
        return min(rate, Decimal('1.00'))  # Cap at 100%
    
    @staticmethod
    def get_available_spots(current_bookings: int, capacity: int) -> int:
        """
        Get number of available spots remaining.
        
        Args:
            current_bookings: Current number of bookings
            capacity: Maximum capacity
            
        Returns:
            Number of available spots (minimum 0)
        """
        available = capacity - current_bookings
        return max(0, available)
    
    @staticmethod
    def is_nearly_full(current_bookings: int, capacity: int, threshold: float = 0.9) -> bool:
        """
        Check if class is nearly full (above threshold).
        
        Args:
            current_bookings: Current number of bookings
            capacity: Maximum capacity
            threshold: Threshold for "nearly full" (default 90%)
            
        Returns:
            True if occupancy is above threshold
        """
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
        """
        Calculate optimal class capacity based on room and resources.
        
        Args:
            room_size_sqm: Room size in square meters
            equipment_count: Number of equipment pieces available
            instructor_capacity: Maximum students instructor can handle
            
        Returns:
            Optimal capacity (minimum of all constraints)
        """
        # 2 sqm per person (social distancing + movement space)
        space_capacity = room_size_sqm // 2
        
        # Equipment is limiting factor if applicable
        equipment_capacity = equipment_count if equipment_count > 0 else 999
        
        # Instructor capacity
        instructor_limit = instructor_capacity if instructor_capacity > 0 else 999
        
        # Return minimum of all constraints
        optimal = min(space_capacity, equipment_capacity, instructor_limit)
        
        return max(1, optimal)  # Ensure at least 1 person capacity
