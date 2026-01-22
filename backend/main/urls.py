from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authorization.urls')),
    path('api/reservations/', include('reservations.urls')),
    path('api/classes/', include('classes.urls')),
    path('api/memberships/', include('memberships.urls')),
<<<<<<< Updated upstream
    path('api/payment/', include('payment.urls')),
=======
    path('api/payments/', include('payments.urls')),
>>>>>>> Stashed changes
]
