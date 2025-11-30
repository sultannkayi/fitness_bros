from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Reservation
from .serializers import ReservationSerializer, ReservationListSerializer


class ReservationViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing Reservation instances."""
    
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['member__first_name', 'member__last_name', 'fitness_class__name']
    ordering_fields = ['reserved_at', 'status']
    ordering = ['-reserved_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ReservationListSerializer
        return ReservationSerializer
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a reservation."""
        reservation = self.get_object()
        if reservation.status == 'cancelled':
            return Response(
                {'error': 'Reservation is already cancelled.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        reservation.status = 'cancelled'
        reservation.save()
        serializer = self.get_serializer(reservation)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def confirmed(self, request):
        """Return only confirmed reservations."""
        confirmed = self.queryset.filter(status='confirmed')
        page = self.paginate_queryset(confirmed)
        if page is not None:
            serializer = ReservationListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ReservationListSerializer(confirmed, many=True)
        return Response(serializer.data)
