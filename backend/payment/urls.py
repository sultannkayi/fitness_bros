from django.urls import path
from .views import InitiatePaymentView, PaymentCallbackView, PaymentStatusView, PlansView

urlpatterns = [
    path('plans/', PlansView.as_view(), name='payment-plans'),
    path('init/', InitiatePaymentView.as_view(), name='payment-init'),
    path('callback/', PaymentCallbackView.as_view(), name='payment-callback'),
    path('status/<str:conversation_id>/', PaymentStatusView.as_view(), name='payment-status'),
]
