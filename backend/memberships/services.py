from decimal import Decimal
from typing import Dict, Any
from datetime import datetime

class PricingEngine:
    """
    Yeni üyelik planlarına göre dinamik fiyat hesaplama.
    """

    # Üyelik planları sabit tanımlı (ileride veritabanına taşınabilir)
    MEMBERSHIP_PLANS = {
        'student': {
            'monthly_fee': Decimal('500'),
            'price_multiplier': Decimal('0.8'),      # Derslerin %80'i ödenir
            'peak_hour_multiplier': Decimal('1.2'),  # Akşam saatlerinde +%20
            'surge_pricing_apply': True,            # Doluluktan etkilenir
            'cancellation_refund_rate': Decimal('0.5'),  # İptalde %50 iade
            'cancellation_min_hours': 24,
        },
        'standard': {
            'monthly_fee': Decimal('1000'),
            'price_multiplier': Decimal('1.0'),      # Tam fiyat
            'peak_hour_multiplier': Decimal('1.5'),  # Akşam saatlerinde +%50
            'surge_pricing_apply': True,
            'cancellation_refund_rate': Decimal('0.0'),  # İptalde iade yok
            'cancellation_min_hours': 12,
        },
        'premium': {
            'monthly_fee': Decimal('2500'),
            'price_multiplier': Decimal('0.0'),      # Dersler ücretsiz
            'peak_hour_multiplier': Decimal('1.0'),  # Saat fark etmez
            'surge_pricing_apply': False,            # Doluluk etkilemez
            'cancellation_refund_rate': Decimal('1.0'),  # Tam iade
            'cancellation_min_hours': 2,
        }
    }

    PEAK_HOURS_START = 18
    PEAK_HOURS_END = 22
    SURGE_THRESHOLD = Decimal('0.8')  # %80 doluluk üstü surge

    @classmethod
    def get_plan_config(cls, membership_type: str) -> Dict[str, Any]:
        """Üyelik tipine göre konfigürasyon dön"""
        plan_id = membership_type.lower()
        plan = cls.MEMBERSHIP_PLANS.get(plan_id)
        if not plan:
            # Fallback olarak standard dönülebilir veya hata fırlatılabilir
            raise ValueError(f"Geçersiz üyelik tipi: {membership_type}")
        return plan

    @classmethod
    def calculate_class_price(
        cls,
        base_price: Decimal,
        membership_type: str,
        class_datetime: datetime,
        current_occupancy_rate: Decimal  # 0.0 - 1.0 arası
    ) -> Decimal:
        """
        Ders fiyatını dinamik olarak hesapla.
        """
        # Decimal dönüşüm garantisi
        if not isinstance(base_price, Decimal):
            base_price = Decimal(str(base_price))
        
        if not isinstance(current_occupancy_rate, Decimal):
            current_occupancy_rate = Decimal(str(current_occupancy_rate))

        plan = cls.get_plan_config(membership_type)

        # 1. Temel çarpan (Premium ücretsiz ise burada 0 döner)
        price = base_price * plan['price_multiplier']

        if plan['price_multiplier'] == Decimal('0'):
            return Decimal('0.00')

        # 2. Peak hour çarpanı
        hour = class_datetime.hour
        is_peak = cls.PEAK_HOURS_START <= hour <= cls.PEAK_HOURS_END
        
        if is_peak:
            price = price * plan['peak_hour_multiplier']

        # 3. Surge pricing (doluluk yüksekse)
        if plan['surge_pricing_apply'] and current_occupancy_rate > cls.SURGE_THRESHOLD:
            # Örnek: %80 üstü her %10 için +%10 fiyat artışı
            excess = current_occupancy_rate - cls.SURGE_THRESHOLD
            # (0.1 / 0.1) * 0.1 mantığıyla artış katsayısı
            surge_multiplier = Decimal('1.0') + (excess / Decimal('0.1')) * Decimal('0.1')
            price = price * surge_multiplier

        return price.quantize(Decimal('0.01'))

    @classmethod
    def calculate_refund_amount(
        cls,
        original_price: Decimal,
        membership_type: str,
        hours_before_class: int
    ) -> Decimal:
        """İptal iade miktarını hesapla."""
        plan = cls.get_plan_config(membership_type)

        if hours_before_class < plan['cancellation_min_hours']:
            return Decimal('0.00')  # Geç iptal, iade yok

        return (original_price * plan['cancellation_refund_rate']).quantize(Decimal('0.01'))