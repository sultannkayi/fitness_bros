from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Reservation
from .serializers import ReservationCreateSerializer
from django.core.exceptions import ValidationError

class ReservationListCreateView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReservationCreateSerializer

    def post(self, request):
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request}
        )

        serializer.is_valid(raise_exception=True)

        try:
            reservation = serializer.save()
        except ValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"id": reservation.id},
            status=status.HTTP_201_CREATED
        )


class ReservationDetailView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Reservation.objects.all()
