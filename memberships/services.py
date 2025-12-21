from decimal import Decimal
from typing import Optional


class PricingService:

    BASE_PRICES = {
        'STANDARD':  Decimal('100.00'),
        'PREMIUM':  Decimal('200.00'),
        'STUDENT': Decimal('75.00'),
    }

    DURATION_DISCOUNTS = {
        1: Decimal('0.00'),
        3: Decimal('0.05'),
        6: Decimal('0.10'),
        12: Decimal('0.20'),
    }

    @classmethod
    def calculate_membership_price(
        cls,
        membership_type: str,
        duration_months: int,
        promo_code: Optional[str] = None
    ) -> Decimal:
        if membership_type not in cls.BASE_PRICES:
            raise ValueError(f"Invalid membership type: {membership_type}")

        if duration_months not in cls.DURATION_DISCOUNTS:
            raise ValueError(f"Invalid duration: {duration_months}.  Must be 1, 3, 6, or 12 months.")

        base_price = cls. BASE_PRICES[membership_type]

        total = base_price * duration_months

        duration_discount = cls.DURATION_DISCOUNTS[duration_months]
        total = total * (Decimal('1.00') - duration_discount)

        if promo_code:
            promo_discount = cls._get_promo_discount(promo_code)
            total = total * (Decimal('1.00') - promo_discount)

        return total. quantize(Decimal('0.01'))

    @staticmethod
    def _get_promo_discount(promo_code: str) -> Decimal:
        promo_codes = {
            'WELCOME10': Decimal('0.10'),
            'SUMMER20': Decimal('0.20'),
            'NEWYEAR':  Decimal('0.15'),
        }
        return promo_codes.get(promo_code. upper(), Decimal('0.00'))

    @classmethod
    def calculate_upgrade_cost(
        cls,
        current_type: str,
        new_type: str,
        remaining_days: int
    ) -> Decimal:
        if current_type not in cls.BASE_PRICES or new_type not in cls.BASE_PRICES:
            raise ValueError("Invalid membership type")

        if remaining_days < 0:
            raise ValueError("Remaining days cannot be negative")

        current_price = cls.BASE_PRICES[current_type]
        new_price = cls.BASE_PRICES[new_type]

        if new_price <= current_price:
            raise ValueError("Cannot downgrade or same level membership")

        daily_current = current_price / 30
        daily_new = new_price / 30
        daily_diff = daily_new - daily_current

        upgrade_cost = daily_diff * remaining_days

        return upgrade_cost.quantize(Decimal('0.01'))

    @classmethod
    def get_membership_value(cls, membership_type: str) -> Decimal:
        if membership_type not in cls.BASE_PRICES:
            raise ValueError(f"Invalid membership type: {membership_type}")
        return cls.BASE_PRICES[membership_type]