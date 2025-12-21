from decimal import Decimal
from unittest.mock import patch
from django.test import TestCase
from memberships.services import PricingService


class PricingServiceTests(TestCase):

    def test_calculate_standard_membership_one_month(self):
        price = PricingService.calculate_membership_price('STANDARD', 1)
        self.assertEqual(price, Decimal('100.00'))

    def test_calculate_premium_membership_one_month(self):
        price = PricingService.calculate_membership_price('PREMIUM', 1)
        self.assertEqual(price, Decimal('200.00'))

    def test_calculate_student_membership_one_month(self):
        price = PricingService.calculate_membership_price('STUDENT', 1)
        self.assertEqual(price, Decimal('75.00'))

    def test_calculate_membership_three_months_with_discount(self):
        price = PricingService. calculate_membership_price('STANDARD', 3)
        self.assertEqual(price, Decimal('285.00'))

    def test_calculate_membership_six_months_with_discount(self):
        price = PricingService.calculate_membership_price('STANDARD', 6)
        self.assertEqual(price, Decimal('540.00'))

    def test_calculate_membership_twelve_months_with_discount(self):
        price = PricingService.calculate_membership_price('STANDARD', 12)
        self.assertEqual(price, Decimal('960.00'))

    def test_calculate_membership_with_promo_code(self):
        price = PricingService.calculate_membership_price('STANDARD', 1, 'WELCOME10')
        self.assertEqual(price, Decimal('90.00'))

    def test_calculate_membership_with_combined_discounts(self):
        price = PricingService. calculate_membership_price('STANDARD', 6, 'WELCOME10')
        self.assertEqual(price, Decimal('486.00'))

    def test_calculate_membership_with_invalid_promo_code(self):
        price = PricingService.calculate_membership_price('STANDARD', 1, 'INVALID')
        self.assertEqual(price, Decimal('100.00'))

    def test_calculate_membership_with_case_insensitive_promo(self):
        price = PricingService.calculate_membership_price('STANDARD', 1, 'welcome10')
        self.assertEqual(price, Decimal('90.00'))

    def test_invalid_membership_type_raises_error(self):
        with self. assertRaises(ValueError) as context:
            PricingService. calculate_membership_price('INVALID', 1)
        self.assertIn('Invalid membership type', str(context.exception))

    def test_invalid_duration_raises_error(self):
        with self.assertRaises(ValueError) as context:
            PricingService.calculate_membership_price('STANDARD', 5)
        self.assertIn('Invalid duration', str(context.exception))

    def test_upgrade_cost_standard_to_premium(self):
        cost = PricingService.calculate_upgrade_cost('STANDARD', 'PREMIUM', 15)
        self.assertEqual(cost, Decimal('50.00'))

    def test_upgrade_cost_student_to_premium(self):
        cost = PricingService. calculate_upgrade_cost('STUDENT', 'PREMIUM', 30)
        self.assertEqual(cost, Decimal('125.00'))

    def test_upgrade_cost_with_zero_days_remaining(self):
        cost = PricingService.calculate_upgrade_cost('STANDARD', 'PREMIUM', 0)
        self.assertEqual(cost, Decimal('0.00'))

    def test_downgrade_raises_error(self):
        with self.assertRaises(ValueError) as context:
            PricingService.calculate_upgrade_cost('PREMIUM', 'STANDARD', 15)
        self.assertIn('Cannot downgrade', str(context.exception))

    def test_same_level_upgrade_raises_error(self):
        with self.assertRaises(ValueError) as context:
            PricingService.calculate_upgrade_cost('STANDARD', 'STANDARD', 15)
        self.assertIn('Cannot downgrade', str(context.exception))

    def test_get_membership_value_standard(self):
        value = PricingService.get_membership_value('STANDARD')
        self.assertEqual(value, Decimal('100.00'))

    def test_get_membership_value_invalid_type(self):
        with self.assertRaises(ValueError):
            PricingService.get_membership_value('INVALID')

    @patch('memberships.services.PricingService._get_promo_discount')
    def test_promo_code_with_mocked_discount(self, mock_get_promo):
        mock_get_promo.return_value = Decimal('0.30')
        price = PricingService.calculate_membership_price('STANDARD', 1, 'TESTCODE')
        self.assertEqual(price, Decimal('70.00'))
        mock_get_promo. assert_called_once_with('TESTCODE')

    def test_premium_twelve_months_with_promo_complex(self):
        price = PricingService.calculate_membership_price('PREMIUM', 12, 'SUMMER20')
        self.assertEqual(price, Decimal('1536.00'))

    def test_student_membership_already_discounted(self):
        price = PricingService.calculate_membership_price('STUDENT', 12)
        self.assertEqual(price, Decimal('720.00'))


class PricingServiceIntegrationTests(TestCase):

    def test_realistic_user_journey_new_member(self):
        price = PricingService.calculate_membership_price('STANDARD', 6, 'WELCOME10')
        self.assertEqual(price, Decimal('486.00'))
        self.assertLess(price, Decimal('1000.00'))

    def test_realistic_user_journey_upgrade(self):
        upgrade_cost = PricingService.calculate_upgrade_cost('STANDARD', 'PREMIUM', 20)
        self.assertGreater(upgrade_cost, Decimal('0.00'))
        self.assertLess(upgrade_cost, Decimal('100.00'))

    def test_pricing_consistency(self):
        price1 = PricingService.calculate_membership_price('STANDARD', 1)
        price2 = PricingService.calculate_membership_price('STANDARD', 1)
        self.assertEqual(price1, price2)
        self.assertEqual(price1, Decimal('100.00'))