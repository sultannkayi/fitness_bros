from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Reservation
from .serializers import ReservationSerializer, ReservationCreateSerializer  # ← İKİSİNİ DE IMPORT ET
from django.db import IntegrityError

class ReservationListCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reservations = Reservation.objects.filter(member=request.user.member_profile).order_by('-created_at')
        serializer = ReservationSerializer(reservations, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ReservationCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                reservation = serializer.save()
                # Oluşturulan rezervasyonu detaylı serializer ile dön
                detail_serializer = ReservationSerializer(reservation)
                return Response(detail_serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response(
                    {"detail": "Bu derse zaten rezervasyon yapmışsınız."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReservationDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            reservation = Reservation.objects.get(pk=pk, member=request.user.member_profile)
            reservation.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Reservation.DoesNotExist:
            return Response({"detail": "Rezervasyon bulunamadı veya size ait değil."}, status=status.HTTP_404_NOT_FOUND)