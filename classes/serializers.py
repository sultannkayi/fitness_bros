from rest_framework import serializers
from .models import FitnessClass

class FitnessClassSerializer(serializers.ModelSerializer):
    instructor_name = serializers.SerializerMethodField()
    available_spots = serializers.SerializerMethodField()
    
    class Meta:
        model = FitnessClass
        fields = ['id', 'name', 'instructor_name', 'capacity', 'date_time', 'base_price', 'is_active', 'available_spots']
    
    def get_instructor_name(self, obj):
        if obj.instructor.first_name:
            return f"{obj.instructor.first_name} {obj.instructor.last_name}".strip()
        return obj.instructor.email
    
    def get_available_spots(self, obj):
        reserved_count = obj.reservations.count()
        return obj.capacity - reserved_count