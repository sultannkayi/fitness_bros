"""
Unit tests for Memberships Service Layer with TDD and Mocking.
Tests PricingService with various scenarios including edge cases.
"""
import pytest
from decimal import Decimal
from unittest.mock import patch, MagicMock
from django.test import TestCase
from memberships.services import PricingService


class PricingServiceTests(TestCase):
    """
    TDD Unit tests for PricingService.
    Tests pricing logic in isolation using mocks.
    """
    
    def test_calculate_standard_membership_one_month(self):
        """Happy path: Standard membership for 1 month, no discounts."""
        price = PricingService.calculate_membership_price('STANDARD', 1)
        self.assertEqual(price, Decimal('100.00'))
    
    def test_calculate_premium_membership_one_month(self):
        """Happy path: Premium membership for 1 month."""
        price = PricingService.calculate_membership_price('PREMIUM', 1)
        self.assertEqual(price, Decimal('200.00'))
    
    def test_calculate_student_membership_one_month(self):
        """Happy path: Student membership for 1 month."""
        price = PricingService.calculate_membership_price('STUDENT', 1)
        self.assertEqual(price, Decimal('75.00'))
    
    def test_calculate_membership_three_months_with_discount(self):
        """Edge case: 3-month membership gets 5% discount."""
        price = PricingService.calculate_membership_price('STANDARD', 3)
        # 100 * 3 = 300, minus 5% = 285
        self.assertEqual(price, Decimal('285.00'))
    
    def test_calculate_membership_six_months_with_discount(self):
        """Edge case: 6-month membership gets 10% discount."""
        price = PricingService.calculate_membership_price('STANDARD', 6)
        # 100 * 6 = 600, minus 10% = 540
        self.assertEqual(price, Decimal('540.00'))
    
    def test_calculate_membership_twelve_months_with_discount(self):
        """Edge case: 12-month membership gets 20% discount."""
        price = PricingService.calculate_membership_price('STANDARD', 12)
        # 100 * 12 = 1200, minus 20% = 960
        self.assertEqual(price, Decimal('960.00'))
    
    def test_calculate_membership_with_promo_code(self):
        """Happy path: Membership with valid promo code."""
        price = PricingService.calculate_membership_price('STANDARD', 1, 'WELCOME10')
        # 100 minus 10% = 90
        self.assertEqual(price, Decimal('90.00'))
    
    def test_calculate_membership_with_combined_discounts(self):
        """Complex scenario: Duration discount + promo code."""
        price = PricingService.calculate_membership_price('STANDARD', 6, 'WELCOME10')
        # 100 * 6 = 600, minus 10% duration = 540, minus 10% promo = 486
        self.assertEqual(price, Decimal('486.00'))
    
    def test_calculate_membership_with_invalid_promo_code(self):
        """Edge case: Invalid promo code should not give discount."""
        price = PricingService.calculate_membership_price('STANDARD', 1, 'INVALID')
        self.assertEqual(price, Decimal('100.00'))
    
    def test_calculate_membership_with_case_insensitive_promo(self):
        """Edge case: Promo codes should be case-insensitive."""
        price = PricingService.calculate_membership_price('STANDARD', 1, 'welcome10')
        self.assertEqual(price, Decimal('90.00'))
    
    def test_invalid_membership_type_raises_error(self):
        """Error scenario: Invalid membership type should raise ValueError."""
        with self.assertRaises(ValueError) as context:
            PricingService.calculate_membership_price('INVALID', 1)
        self.assertIn('Invalid membership type', str(context.exception))
    
    def test_invalid_duration_raises_error(self):
        """Error scenario: Invalid duration should raise ValueError."""
        with self.assertRaises(ValueError) as context:
            PricingService.calculate_membership_price('STANDARD', 5)
        self.assertIn('Invalid duration', str(context.exception))
    
    def test_upgrade_cost_standard_to_premium(self):
        """Happy path: Calculate upgrade cost from STANDARD to PREMIUM."""
        cost = PricingService.calculate_upgrade_cost('STANDARD', 'PREMIUM', 15)
        # (200-100)/30 * 15 = 3.33 * 15 = 50.00
        self.assertEqual(cost, Decimal('50.00'))
    
    def test_upgrade_cost_student_to_premium(self):
        """Happy path: Calculate upgrade cost from STUDENT to PREMIUM."""
        cost = PricingService.calculate_upgrade_cost('STUDENT', 'PREMIUM', 30)
        # (200-75)/30 * 30 = 125.00
        self.assertEqual(cost, Decimal('125.00'))
    
    def test_upgrade_cost_with_zero_days_remaining(self):
        """Edge case: Zero days remaining should be zero cost."""
        cost = PricingService.calculate_upgrade_cost('STANDARD', 'PREMIUM', 0)
        self.assertEqual(cost, Decimal('0.00'))
    
    def test_downgrade_raises_error(self):
        """Error scenario: Downgrade should raise ValueError."""
        with self.assertRaises(ValueError) as context:
            PricingService.calculate_upgrade_cost('PREMIUM', 'STANDARD', 15)
        self.assertIn('Cannot downgrade', str(context.exception))
    
    def test_same_level_upgrade_raises_error(self):
        """Error scenario: Same level 'upgrade' should raise ValueError."""
        with self.assertRaises(ValueError) as context:
            PricingService.calculate_upgrade_cost('STANDARD', 'STANDARD', 15)
        self.assertIn('Cannot downgrade', str(context.exception))
    
    def test_get_membership_value_standard(self):
        """Happy path: Get base price for STANDARD."""
        value = PricingService.get_membership_value('STANDARD')
        self.assertEqual(value, Decimal('100.00'))
    
    def test_get_membership_value_invalid_type(self):
        """Error scenario: Invalid type should raise ValueError."""
        with self.assertRaises(ValueError):
            PricingService.get_membership_value('INVALID')
    
    @patch('memberships.services.PricingService._get_promo_discount')
    def test_promo_code_with_mocked_discount(self, mock_get_promo):
        """Mocking: Test promo code logic with mocked discount function."""
        # Mock promo discount to return 30%
        mock_get_promo.return_value = Decimal('0.30')
        
        price = PricingService.calculate_membership_price('STANDARD', 1, 'TESTCODE')
        
        # 100 minus 30% = 70
        self.assertEqual(price, Decimal('70.00'))
        mock_get_promo.assert_called_once_with('TESTCODE')
    
    def test_premium_twelve_months_with_promo_complex(self):
        """Complex scenario: Maximum discounts combined."""
        price = PricingService.calculate_membership_price('PREMIUM', 12, 'SUMMER20')
        # 200 * 12 = 2400, minus 20% duration = 1920, minus 20% promo = 1536
        self.assertEqual(price, Decimal('1536.00'))
    
    def test_student_membership_already_discounted(self):
        """Edge case: Student membership with additional duration discount."""
        price = PricingService.calculate_membership_price('STUDENT', 12)
        # 75 * 12 = 900, minus 20% = 720
        self.assertEqual(price, Decimal('720.00'))


class PricingServiceIntegrationTests(TestCase):
    """
    Integration tests for PricingService.
    Tests interaction with other components.
    """
    
    def test_realistic_user_journey_new_member(self):
        """Integration: New user signs up for 6-month STANDARD with WELCOME10."""
        price = PricingService.calculate_membership_price('STANDARD', 6, 'WELCOME10')
        self.assertEqual(price, Decimal('486.00'))
        
        # Verify it's affordable (business rule: must be < 1000)
        self.assertLess(price, Decimal('1000.00'))
    
    def test_realistic_user_journey_upgrade(self):
        """Integration: User upgrades from STANDARD to PREMIUM mid-cycle."""
        # User has 20 days left on STANDARD
        upgrade_cost = PricingService.calculate_upgrade_cost('STANDARD', 'PREMIUM', 20)
        
        # Should be reasonable cost
        self.assertGreater(upgrade_cost, Decimal('0.00'))
        self.assertLess(upgrade_cost, Decimal('100.00'))
    
    @patch('memberships.services.timezone')
    def test_pricing_with_mocked_timezone(self, mock_timezone):
        """Mocking: Test pricing doesn't depend on current time."""
        # Mock timezone to ensure test consistency
        mock_now = MagicMock()
        mock_timezone.now.return_value = mock_now
        
        # Pricing should work regardless of timezone mock
        price = PricingService.calculate_membership_price('STANDARD', 1)
        self.assertEqual(price, Decimal('100.00'))
