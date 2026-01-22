# payments/views.py
from django.shortcuts import redirect
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal
from django.conf import settings
from .models import MembershipPayment
from .services import IyzicoService
from memberships.models import Member
import logging

logger = logging.getLogger(__name__)


class InitiateMembershipPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        membership_type = request.data.get('membership_type')

        if membership_type not in dict(Member.MEMBERSHIP_CHOICES):
            return Response(
                {'error': 'Geçersiz üyelik tipi'},
                status=status.HTTP_400_BAD_REQUEST
            )

        member = request.user.member_profile
        amount = settings.MEMBERSHIP_PRICES.get(membership_type, Decimal('0.00'))

        if amount <= 0:
            return Response(
                {'error': 'Bu plan için ödeme gerekmiyor'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1️⃣ Payment kaydı oluştur (TOKEN YOK)
        payment = MembershipPayment.objects.create(
            member=member,
            new_membership_type=membership_type,
            amount=amount,
            status='pending'
        )

        # 2️⃣ Iyzico initialize
        result = IyzicoService.create_checkout_form(payment)

        if result['status'] != 'success':
            payment.status = 'failed'
            payment.save(update_fields=['status'])
            return Response(
                {'error': result.get('message', 'Ödeme başlatılamadı')},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                'status': 'success',
                'payment_page_url': result['payment_page_url']
            },
            status=status.HTTP_200_OK
        )


@method_decorator(csrf_exempt, name='dispatch')
class PaymentCallbackView(View):
    def post(self, request, *args, **kwargs):
        logger.info("=== IYZICO CALLBACK GELDİ ===")
        logger.info(f"POST BODY: {request.POST}")

        token = request.POST.get('token')
        status_val = request.POST.get('status')

        if not token:
            logger.error("Callback token içermiyor!")
            return JsonResponse({'error': 'Token yok'}, status=400)

        # 1️⃣ Token ile ödeme ara
        payment = MembershipPayment.objects.filter(
            iyzico_transaction_id=token
        ).first()

        # 2️⃣ Token ilk kez geliyorsa bağla
        if not payment:
            payment = MembershipPayment.objects.filter(
                status='pending'
            ).order_by('-created_at').first()

            if not payment:
                logger.error("Pending ödeme bulunamadı")
                return JsonResponse({'error': 'Ödeme bulunamadı'}, status=404)

            payment.iyzico_transaction_id = token
            payment.save(update_fields=['iyzico_transaction_id'])
            logger.info(f"Token payment’a bağlandı: {token}")

        # 3️⃣ Sonuç işle
        if status_val == 'success':
            payment.status = 'success'
            payment.save(update_fields=['status'])

            member = payment.member
            member.membership_type = payment.new_membership_type
            member.save(update_fields=['membership_type'])

            logger.info("Ödeme başarılı, üyelik güncellendi")
            return redirect('/profile/?payment=success')

        payment.status = 'failed'
        payment.save(update_fields=['status'])
        logger.warning("Ödeme başarısız")
        return redirect('/profile/?payment=failed')
