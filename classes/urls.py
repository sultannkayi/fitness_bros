# classes/urls.py
from django.urls import path
from .views import FitnessClassListView

urlpatterns = [
    path('', FitnessClassListView.as_view(), name='fitness-class-list'),
    # İsteğe bağlı: slash'sız erişim için de ekleyebilirsin ama gerek yok
]