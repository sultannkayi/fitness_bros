from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Reservation
from memberships.serializers import MemberListSerializer
from classes.serializers import FitnessClassListSerializer


class ReservationSerializer(serializers.ModelSerializer):
    """Serializer for the Reservation model."""
    
    member_details = MemberListSerializer(source='member', read_only=True)
    fitness_class_details = FitnessClassListSerializer(source='fitness_class', read_only=True)
    
    class Meta:
        model = Reservation
        fields = [
            'id', 'member', 'fitness_class', 'member_details',
            'fitness_class_details', 'status', 'reserved_at',
            'updated_at', 'notes'
        ]
        read_only_fields = ['id', 'reserved_at', 'updated_at']
    
    def validate(self, attrs):
        """Validate reservation data including capacity check."""
        instance = Reservation(**attrs)
        if self.instance:
            instance.pk = self.instance.pk
        
        try:
            instance.clean()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        
        return attrs


class ReservationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing reservations."""
    
    member_name = serializers.CharField(source='member.full_name', read_only=True)
    class_name = serializers.CharField(source='fitness_class.name', read_only=True)
    class_schedule = serializers.DateTimeField(source='fitness_class.schedule', read_only=True)
    
    class Meta:
        model = Reservation
        fields = [
            'id', 'member_name', 'class_name', 'class_schedule',
            'status', 'reserved_at'
        ]
