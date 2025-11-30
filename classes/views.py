from django.db import models
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import FitnessClass
from .serializers import FitnessClassSerializer, FitnessClassListSerializer


class FitnessClassViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing FitnessClass instances."""
    
    queryset = FitnessClass.objects.all()
    serializer_class = FitnessClassSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'instructor', 'class_type']
    ordering_fields = ['schedule', 'name', 'price', 'capacity']
    ordering = ['schedule']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return FitnessClassListSerializer
        return FitnessClassSerializer
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Return only classes with available spots."""
        from django.db.models import Count, Q
        
        available_classes = self.queryset.filter(is_active=True).annotate(
            confirmed_reservations=Count(
                'reservations',
                filter=Q(reservations__status='confirmed')
            )
        ).filter(confirmed_reservations__lt=models.F('capacity'))
        
        page = self.paginate_queryset(available_classes)
        if page is not None:
            serializer = FitnessClassListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = FitnessClassListSerializer(available_classes, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def reservations(self, request, pk=None):
        """Return reservations for a specific fitness class."""
        fitness_class = self.get_object()
        from reservations.serializers import ReservationListSerializer
        reservations = fitness_class.reservations.filter(status='confirmed')
        serializer = ReservationListSerializer(reservations, many=True)
        return Response(serializer.data)
