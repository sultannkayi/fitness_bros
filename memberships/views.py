from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from reservations.models import Reservation
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAdminUser
from .models import Member


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
    
@api_view(['GET'])
@permission_classes([IsAdminUser])
def all_members_admin_view(request):
    """
    Sadece staff (admin) kullanıcılar tüm üyeleri görebilir.
    """
    if not request.user.is_staff:
        return Response(
            {"detail": "Bu işlem için admin yetkisi gereklidir."},
            status=status.HTTP_403_FORBIDDEN
        )

    members = Member.objects.select_related('user').all().order_by('user__email')
    data = []
    for member in members:
        user = member.user
        full_name = f"{user.first_name} {user.last_name}".strip()
        if not full_name:
            full_name = user.email

        data.append({
            "id": member.id,
            "user_id": user.id,
            "email": user.email,
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "full_name": full_name,
            "membership_type": dict(Member.MEMBERSHIP_CHOICES).get(member.membership_type, member.membership_type),
            "gender": member.gender or "Belirtilmemiş",
            "birth_date": member.birth_date.isoformat() if member.birth_date else None,
            "height": str(member.height) + " cm" if member.height else None,
            "weight": str(member.weight) + " kg" if member.weight else None,
            "is_active": user.is_active,
        })

    return Response(data)