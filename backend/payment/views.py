import uuid
import json
from decimal import Decimal
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
import iyzipay # type: ignore

from memberships.services import PricingEngine
from .models import Payment, PaymentLog
from .utils import get_iyzi_options

User = get_user_model()

logger = logging.getLogger(__name__)


class PlansView(APIView):
    """Kullanılabilir üyelik planlarını ve aylık ücretlerini döndürür."""

    def get(self, request: Request) -> Response:
        logger.info("PlansView çağrıldı - Kullanıcı: %s", request.user)
        plans = {}
        for key, cfg in PricingEngine.MEMBERSHIP_PLANS.items():
            plans[key] = {
                "monthly_fee": str(cfg["monthly_fee"]),
            }
        logger.debug("Dönen planlar: %s", plans)
        return Response({"plans": plans})


class InitiatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        logger.info("InitiatePaymentView çağrıldı - Kullanıcı ID: %s, Email: %s", 
                    request.user.id, request.user.email)
        logger.debug("Gelen veri: %s", request.data)

        membership_type = (request.data.get("membership_type") or "").lower()
        logger.debug("Alınan membership_type: %s", membership_type)

        if membership_type not in PricingEngine.MEMBERSHIP_PLANS:
            logger.warning("Geçersiz üyelik tipi: %s", membership_type)
            return Response({"detail": "Geçersiz üyelik tipi"}, status=400)

        amount: Decimal = PricingEngine.MEMBERSHIP_PLANS[membership_type]["monthly_fee"]
        logger.info("Hesaplanan tutar: %s TRY", amount)

        conversation_id = str(uuid.uuid4())
        basket_id = f"basket-{conversation_id[:8]}"
        logger.debug("conversation_id: %s, basket_id: %s", conversation_id, basket_id)

        try:
            logger.info("Payment modeli oluşturuluyor...")
            payment = Payment.objects.create(
                user=request.user,
                membership_type=membership_type,
                amount=amount,
                conversation_id=conversation_id,
                basket_id=basket_id,
                status="pending",
            )
            logger.info("Payment başarıyla oluşturuldu - ID: %s", payment.id)
        except Exception as e:
            logger.exception("Payment oluşturma hatası: %s", str(e))
            return Response({
                "detail": "Ödeme kaydı veritabanına yazılamadı",
                "error": str(e)
            }, status=500)

        try:
            PaymentLog.objects.create(
                payment=payment,
                event="init:request",
                payload={"membership_type": membership_type, "amount": str(amount)}
            )
            logger.debug("init:request logu kaydedildi")
        except Exception as e:
            logger.warning("PaymentLog kaydedilemedi: %s", str(e))

        opts = get_iyzi_options()
        logger.debug("Iyzico options alındı: %s", {k: v[:10] + '...' if v else None for k, v in opts.items() if k in ['api_key', 'secret_key']})

        if not settings.IYZI_CALLBACK_URL:
            logger.error("IYZI_CALLBACK_URL ayarlanmamış")
            return Response({"detail": "IYZI_CALLBACK_URL ayarlanmamış"}, status=500)

        request_payload = {
            'locale': 'tr',
            'conversationId': conversation_id,
            'price': str(amount),
            'paidPrice': str(amount),
            'currency': 'TRY',
            'basketId': basket_id,
            'paymentGroup': 'PRODUCT',
            'callbackUrl': settings.IYZI_CALLBACK_URL,
            'enabledInstallments': [2, 3, 6, 9],
            'buyer': {
                'id': str(request.user.id),
                'name': request.user.first_name or 'İsim',
                'surname': request.user.last_name or 'Soyisim',
                'gsmNumber': getattr(request.user, 'profile', None).phone if hasattr(request.user, 'profile') else '+905xxxxxxxxx',
                'email': request.user.email or 'test@ornek.com',
                'identityNumber': '11111111111',
                'registrationAddress': 'Kullanıcı adresi',
                'ip': request.META.get('REMOTE_ADDR', '127.0.0.1'),
                'city': 'Adana',
                'country': 'Turkey',
                'zipCode': '01000'
            },
            'shippingAddress': {
                'contactName': f"{request.user.first_name or 'İsim'} {request.user.last_name or 'Soyisim'}",
                'city': 'Adana',
                'country': 'Turkey',
                'address': 'Teslimat adresi',
                'zipCode': '01000'
            },
            'billingAddress': {
                'contactName': f"{request.user.first_name or 'İsim'} {request.user.last_name or 'Soyisim'}",
                'city': 'Adana',
                'country': 'Turkey',
                'address': 'Fatura adresi',
                'zipCode': '01000'
            },
            'basketItems': [
                {
                    'id': f'{membership_type}-plan',
                    'name': f'{membership_type.title()} Üyelik',
                    'category1': 'Üyelik',
                    'itemType': 'VIRTUAL',
                    'price': str(amount)
                }
            ]
        }
        logger.debug("iyzico request_payload hazırlandı")

        try:
            logger.info("iyzico CheckoutFormInitialize çağrılıyor...")
            checkout_form_init = iyzipay.CheckoutFormInitialize().create(request_payload, opts)
            data = json.load(checkout_form_init)
            logger.info("iyzico cevabı alındı - status: %s", data.get('status'))

            PaymentLog.objects.create(
                payment=payment,
                event="init:response",
                payload=data
            )
            logger.debug("init:response logu kaydedildi")

            if data.get('status') != 'success':
                logger.error("iyzico başarısız: %s - %s", data.get('errorCode'), data.get('errorMessage'))
                return Response({
                    "detail": "Iyzico ödeme başlatma başarısız",
                    "error_message": data.get('errorMessage'),
                    "error_code": data.get('errorCode'),
                    "iyzico_response": data
                }, status=400)

            token = data.get('token', '')
            payment.token = token
            payment.raw_response = data
            payment.save(update_fields=["token", "raw_response", "updated_at"])
            logger.info("Payment token ve raw_response güncellendi")

            return Response({
                "conversation_id": conversation_id,
                "token": token,
                "checkout_form_content": data.get('checkoutFormContent'),
                "payment_page_url": data.get('paymentPageUrl'),
                "status": data.get('status'),
            })

        except Exception as e:
            logger.exception("iyzico çağrısı veya işleme hatası: %s", str(e))
            PaymentLog.objects.create(
                payment=payment,
                event="init:error",
                payload={"error": str(e)}
            )
            return Response({
                "detail": "Ödeme başlatılırken hata oluştu",
                "error": str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class PaymentCallbackView(View):
    """Iyzico ödeme tamamlandıktan sonra token ile buraya POST atar."""

    def post(self, request, *args, **kwargs):
        logger.info("PaymentCallbackView çağrıldı - Method: POST")
        logger.debug("Gelen POST body: %s", request.body)

        token = request.POST.get('token')
        if not token and request.body:
            try:
                body = json.loads(request.body)
                token = body.get('token')
                logger.debug("JSON body'den token alındı: %s", token)
            except json.JSONDecodeError:
                logger.warning("JSON parse edilemedi")

        if not token:
            logger.error("Token eksik")
            return HttpResponseBadRequest("Token eksik")

        opts = get_iyzi_options()
        logger.debug("Callback için opts alındı")

        request_payload = {'locale': 'tr', 'token': token}

        try:
            logger.info("iyzico CheckoutForm retrieve çağrılıyor...")
            result = iyzipay.CheckoutForm().retrieve(request_payload, opts)
            data = json.load(result)
            logger.info("iyzico callback cevabı alındı - status: %s", data.get('paymentStatus'))

            payment = Payment.objects.filter(token=token).order_by('-created_at').first()
            if not payment and data.get('conversationId'):
                payment = Payment.objects.filter(conversation_id=data['conversationId']).order_by('-created_at').first()

            if not payment:
                logger.warning("Eşleşen ödeme bulunamadı - conversationId: %s", data.get('conversationId'))
                return HttpResponseRedirect("/profile/?payment=failed&reason=no_payment_found")

            PaymentLog.objects.create(payment=payment, event="callback:received", payload=data)
            logger.debug("callback:received logu kaydedildi")

            status = data.get('paymentStatus', '').lower()

            if status == 'success':
                logger.info("Ödeme başarılı - Güncelleme başlıyor")
                payment.status = 'success'
                payment.iyzico_payment_id = data.get('paymentId', '')
                payment.raw_response = data
                payment.save(update_fields=["status", "iyzico_payment_id", "raw_response", "updated_at"])

                try:
                    profile = payment.user.member_profile
                    logger.debug("member_profile bulundu")
                    if profile.membership_type != payment.membership_type:
                        profile.membership_type = payment.membership_type
                        profile.save(update_fields=["membership_type"])
                        logger.info("Üyelik tipi güncellendi: %s", payment.membership_type)
                except AttributeError:
                    logger.warning("member_profile attribute'u yok")
                    PaymentLog.objects.create(
                        payment=payment,
                        event="membership:update_failed",
                        payload={"error": "member_profile bulunamadı veya attribute yok"}
                    )
                except Exception as exc:
                    logger.exception("Üyelik güncelleme hatası: %s", str(exc))
                    PaymentLog.objects.create(
                        payment=payment,
                        event="membership:update_error",
                        payload={"error": str(exc)}
                    )

                # BAŞARILI → PROFILE SAYFASINA YÖNLENDİR
                return HttpResponseRedirect("/profile/?payment=success")

            else:
                logger.warning("Ödeme başarısız - status: %s", status)
                payment.status = 'failed'
                payment.raw_response = data
                payment.save(update_fields=["status", "raw_response", "updated_at"])

                # BAŞARISIZ → PROFILE SAYFASINA YÖNLENDİR
                return HttpResponseRedirect("/profile/?payment=failed")

        except Exception as e:
            logger.exception("Callback işleme hatası: %s", str(e))
            return HttpResponseRedirect("/profile/?payment=failed")


class PaymentStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, conversation_id: str) -> Response:
        logger.info("PaymentStatusView çağrıldı - conversation_id: %s, user: %s", conversation_id, request.user)
        
        payment = Payment.objects.filter(
            conversation_id=conversation_id,
            user=request.user
        ).first()

        if not payment:
            logger.warning("Ödeme bulunamadı - conversation_id: %s", conversation_id)
            return Response({"detail": "Ödeme bulunamadı"}, status=404)

        logger.debug("Ödeme bulundu - status: %s", payment.status)
        return Response({
            "id": payment.id,
            "status": payment.status,
            "membership_type": payment.membership_type,
            "amount": str(payment.amount),
            "currency": payment.currency,
            "created_at": payment.created_at.isoformat(),
            "updated_at": payment.updated_at.isoformat(),
        })