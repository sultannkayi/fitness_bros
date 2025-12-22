from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from reservations.models import Reservation
from django.utils import timezone

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        member = user.member_profile

        data = {
            "name": f"{user.first_name} {user.last_name}".strip() or user.email,
            "gender": member.gender or "Other",
            "age": member.age or "?",
            "weight": f"{member.weight} kg" if member.weight else "? kg",
            "height": f"{member.height} cm" if member.height else "? cm",
            "dateOfBirth": member.birth_date.strftime("%d %B %Y") if member.birth_date else "?",
            "membership_type": member.membership_type or "standard"
        }
        return Response(data)

    def patch(self, request):
        user = request.user
        member = user.member_profile

        # İstediğin iş kuralı: Gelecek tarihli aktif rezervasyon varsa değişiklik engelle
        

        now = timezone.now()
        active_reservations = Reservation.objects.filter(
            member=member,
            fitness_class__date_time__gt=now  # Gelecek tarihli dersler
        ).exists()

        if active_reservations:
            return Response(
                {"detail": "Gelecek tarihli aktif rezervasyonlarınız bulunduğu için üyelik paketinizi değiştiremezsiniz. "
                           "Lütfen rezervasyonlarınızı iptal ettikten sonra tekrar deneyin."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Sadece membership_type güncellenmesine izin ver
        new_type = request.data.get("membership_type")
        if not new_type:
            return Response(
                {"detail": "membership_type alanı zorunludur."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Geçerli bir tip mi kontrol et (güvenlik için)
        valid_types = ['student', 'standard', 'premium']
        if new_type not in valid_types:
            return Response(
                {"detail": "Geçersiz üyelik tipi."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Güncelle ve kaydet
        member.membership_type = new_type
        member.save()

        # Güncel veriyi dön (frontend'in yenilemesi için)
        return Response({
            "detail": f"Üyelik paketiniz '{new_type}' olarak başarıyla güncellendi.",
            "membership_type": member.membership_type
        }, status=status.HTTP_200_OK)