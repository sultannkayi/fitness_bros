from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Member
from .serializers import MemberSerializer, MemberListSerializer


class MemberViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing Member instances."""
    
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'email']
    ordering_fields = ['last_name', 'first_name', 'joined_date', 'membership_type']
    ordering = ['last_name', 'first_name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return MemberListSerializer
        return MemberSerializer
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Return only active members."""
        active_members = self.queryset.filter(is_active=True)
        page = self.paginate_queryset(active_members)
        if page is not None:
            serializer = MemberListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = MemberListSerializer(active_members, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def reservations(self, request, pk=None):
        """Return reservations for a specific member."""
        member = self.get_object()
        from reservations.serializers import ReservationListSerializer
        reservations = member.reservations.all()
        serializer = ReservationListSerializer(reservations, many=True)
        return Response(serializer.data)
