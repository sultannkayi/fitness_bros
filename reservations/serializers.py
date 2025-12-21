from rest_framework import serializers
from . models import Reservation
from classes.models import FitnessClass
from . services import PricingEngine


class ReservationCreateSerializer(serializers. Serializer):
    fitness_class_id = serializers.IntegerField()

    def validate_fitness_class_id(self, value):
        try:
            fitness_class = FitnessClass.objects.get(id=value)
        except FitnessClass.DoesNotExist:
            raise serializers.ValidationError("Fitness class not found")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        member = user.member

        fitness_class = FitnessClass.objects.get(
            id=validated_data['fitness_class_id']
        )

        total = fitness_class.capacity
        booked = fitness_class.reservations.count()
        occupancy_rate = booked / total if total > 0 else 1

        hour = fitness_class.date_time.hour
        is_peak = 18 <= hour <= 22

        price = PricingEngine.calculate_price(
            base_price=fitness_class.base_price,
            membership_type=member.membership_type,
            occupancy_rate=occupancy_rate,
            is_peak_hour=is_peak
        )

        reservation = Reservation.objects.create(
            member=member,
            fitness_class=fitness_class,
            price_paid=price
        )

        return reservation