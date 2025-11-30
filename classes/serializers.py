from rest_framework import serializers
from .models import FitnessClass


class FitnessClassSerializer(serializers.ModelSerializer):
    """Serializer for the FitnessClass model."""
    
    available_spots = serializers.ReadOnlyField()
    is_full = serializers.ReadOnlyField()
    
    class Meta:
        model = FitnessClass
        fields = [
            'id', 'name', 'class_type', 'description', 'instructor',
            'schedule', 'duration_minutes', 'capacity', 'price',
            'available_spots', 'is_full', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class FitnessClassListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing fitness classes."""
    
    available_spots = serializers.ReadOnlyField()
    is_full = serializers.ReadOnlyField()
    
    class Meta:
        model = FitnessClass
        fields = [
            'id', 'name', 'class_type', 'instructor', 'schedule',
            'duration_minutes', 'available_spots', 'is_full', 'price'
        ]
