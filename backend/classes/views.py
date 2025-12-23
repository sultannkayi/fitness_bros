from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import FitnessClass
from .serializers import FitnessClassSerializer

class FitnessClassListView(generics.ListAPIView):
    queryset = FitnessClass.objects.filter(is_active=True).order_by('date_time')
    serializer_class = FitnessClassSerializer
    permission_classes = [AllowAny]
