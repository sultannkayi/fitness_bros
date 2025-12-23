from rest_framework import serializers
from .models import Reservation
from classes.models import FitnessClass
from decimal import Decimal
from memberships.services import PricingEngine
from django.utils import timezone  # ← YENİ EKLE


# Rezervasyon oluşturma için (POST)
class ReservationCreateSerializer(serializers.Serializer):
    fitness_class_id = serializers.IntegerField()

    def validate_fitness_class_id(self, value):
        try:
            fitness_class = FitnessClass.objects.get(id=value)
        except FitnessClass.DoesNotExist:
            raise serializers.ValidationError("Belirtilen ders bulunamadı.")
        
        booked = fitness_class.reservations.count()
        if booked >= fitness_class.capacity:
            raise serializers.ValidationError("Bu dersin kontenjanı dolu.")
        
        return value

    # Yeni eklenen genel validation metodu — rezervasyon sayısı sınırı burada kontrol ediliyor
    def validate(self, data):
        user = self.context['request'].user
        member = user.member_profile

        # Üyelik tipine göre maksimum gelecek tarihli rezervasyon sınırı
        limits = {
            'student': 3,
            'standard': 5,
            'premium': 10,
        }
        max_limit = limits.get(member.membership_type, 5)  # Bilinmeyen tipte standard varsay

        # Sadece gelecek tarihli rezervasyonları say
        now = timezone.now()
        current_future_count = Reservation.objects.filter(
            member=member,
            fitness_class__date_time__gt=now
        ).count()

        if current_future_count >= max_limit:
            raise serializers.ValidationError(
                f"{member.get_membership_type_display()} paketiniz ile maksimum {max_limit} adet gelecek tarihli rezervasyon yapabilirsiniz. "
                f"Mevcut gelecek rezervasyon sayınız: {current_future_count}. "
                "Yeni rezervasyon yapabilmek için mevcut rezervasyonlarınızdan birini iptal edebilirsiniz."
            )

        return data

    def create(self, validated_data):
        user = self.context['request'].user
        member = user.member_profile
        fitness_class = FitnessClass.objects.get(id=validated_data['fitness_class_id'])

        # Doluluk oranı hesapla (henüz yeni rezervasyon eklenmediği için count doğru)
        booked = fitness_class.reservations.count()
        total = fitness_class.capacity
        occupancy_rate = Decimal(booked) / Decimal(total) if total > 0 else Decimal('0')

        # Fiyat hesaplama — PricingEngine doğru şekilde kullanılıyor
        price = PricingEngine.calculate_class_price(
            base_price=fitness_class.base_price,
            membership_type=member.membership_type or 'standard',
            class_datetime=fitness_class.date_time,
            current_occupancy_rate=occupancy_rate
        )

        reservation = Reservation.objects.create(
            member=member,
            fitness_class=fitness_class,
            price_paid=price
        )

        return reservation


# Rezervasyon listeleme için (GET) — değişmedi
class ReservationSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source='fitness_class.name', read_only=True)
    instructor = serializers.CharField(source='fitness_class.instructor_name', read_only=True)
    day = serializers.DateTimeField(source='fitness_class.date_time', format='%d %B %Y', read_only=True)
    time = serializers.DateTimeField(source='fitness_class.date_time', format='%H:%M', read_only=True)
    status = serializers.CharField(default='Onaylandı', read_only=True)

    class Meta:
        model = Reservation
        fields = ['id', 'class_name', 'instructor', 'day', 'time', 'status', 'price_paid']