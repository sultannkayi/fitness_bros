from decimal import Decimal

class PricingEngine:

    @staticmethod
    def calculate_price(base_price, membership_type, occupancy_rate, is_peak_hour):
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

        return price.quantize(Decimal('0.00'))
