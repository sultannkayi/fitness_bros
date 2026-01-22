# payments/urls.py
from django.urls import path
from .views import InitiateMembershipPaymentView, PaymentCallbackView

urlpatterns = [
    path('initiate-membership/', InitiateMembershipPaymentView.as_view(), name='initiate-membership-payment'),
    path('callback/', PaymentCallbackView.as_view(), name='payment-callback'),
]