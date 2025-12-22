"""
Memberships Service Layer
Business logic for pricing, membership management, and discounts.
"""
from decimal import Decimal
from typing import Optional


class PricingService:
    """
    Service for calculating membership prices with various discount strategies.
    Handles membership type discounts, duration-based discounts, and promotional codes.
    """
    
    # Membership type pricing (monthly base prices)
    BASE_PRICES = {
        'STANDARD': Decimal('100.00'),
        'PREMIUM': Decimal('200.00'),
        'STUDENT': Decimal('75.00'),
    }
    
    # Duration discount rates
    DURATION_DISCOUNTS = {
        1: Decimal('0.00'),    # 1 month: no discount
        3: Decimal('0.05'),    # 3 months: 5% discount
        6: Decimal('0.10'),    # 6 months: 10% discount
        12: Decimal('0.20'),   # 12 months: 20% discount
    }
    
    @classmethod
    def calculate_membership_price(
        cls, 
        membership_type: str, 
        duration_months: int,
        promo_code: Optional[str] = None
    ) -> Decimal:
        """
        Calculate total membership price based on type, duration, and promo code.
        
        Args:
            membership_type: Type of membership (STANDARD, PREMIUM, STUDENT)
            duration_months: Duration in months (1, 3, 6, or 12)
            promo_code: Optional promotional code for additional discount
            
        Returns:
            Final price as Decimal
            
        Raises:
            ValueError: If membership_type is invalid or duration not supported
        """
        # Validate membership type
        if membership_type not in cls.BASE_PRICES:
            raise ValueError(f"Invalid membership type: {membership_type}")
        
        # Validate duration
        if duration_months not in cls.DURATION_DISCOUNTS:
            raise ValueError(f"Invalid duration: {duration_months}. Must be 1, 3, 6, or 12 months.")
        
        # Get base price
        base_price = cls.BASE_PRICES[membership_type]
        
        # Calculate total before discount
        total = base_price * duration_months
        
        # Apply duration discount
        duration_discount = cls.DURATION_DISCOUNTS[duration_months]
        total = total * (Decimal('1.00') - duration_discount)
        
        # Apply promo code discount if provided
        if promo_code:
            promo_discount = cls._get_promo_discount(promo_code)
            total = total * (Decimal('1.00') - promo_discount)
        
        return total.quantize(Decimal('0.01'))
    
    @staticmethod
    def _get_promo_discount(promo_code: str) -> Decimal:
        """
        Get discount rate for promotional code.
        
        Args:
            promo_code: Promotional code
            
        Returns:
            Discount rate (e.g., 0.15 for 15% discount)
        """
        # Simple promo code logic (in real app, this would query database)
        promo_codes = {
            'WELCOME10': Decimal('0.10'),  # 10% discount
            'SUMMER20': Decimal('0.20'),   # 20% discount
            'NEWYEAR': Decimal('0.15'),    # 15% discount
        }
        return promo_codes.get(promo_code.upper(), Decimal('0.00'))
    
    @classmethod
    def calculate_upgrade_cost(
        cls,
        current_type: str,
        new_type: str,
        remaining_days: int
    ) -> Decimal:
        """
        Calculate prorated cost for upgrading membership.
        
        Args:
            current_type: Current membership type
            new_type: Desired membership type
            remaining_days: Days remaining in current membership
            
        Returns:
            Prorated upgrade cost
            
        Raises:
            ValueError: If downgrade attempted, invalid types, or negative days
        """
        if current_type not in cls.BASE_PRICES or new_type not in cls.BASE_PRICES:
            raise ValueError("Invalid membership type")
        
        # Validate remaining days
        if remaining_days < 0:
            raise ValueError("Remaining days cannot be negative")
        
        current_price = cls.BASE_PRICES[current_type]
        new_price = cls.BASE_PRICES[new_type]
        
        # Check if it's actually an upgrade
        if new_price <= current_price:
            raise ValueError("Cannot downgrade or same level membership")
        
        # Calculate prorated difference
        daily_current = current_price / 30
        daily_new = new_price / 30
        daily_diff = daily_new - daily_current
        
        upgrade_cost = daily_diff * remaining_days
        
        return upgrade_cost.quantize(Decimal('0.01'))
    
    @classmethod
    def get_membership_value(cls, membership_type: str) -> Decimal:
        """
        Get monthly base price for membership type.
        
        Args:
            membership_type: Type of membership
            
        Returns:
            Monthly base price
            
        Raises:
            ValueError: If membership type is invalid
        """
        if membership_type not in cls.BASE_PRICES:
            raise ValueError(f"Invalid membership type: {membership_type}")
        return cls.BASE_PRICES[membership_type]
