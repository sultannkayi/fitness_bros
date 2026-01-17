import uuid
from decimal import Decimal
from django.conf import settings
from django.contrib.auth import get_user_model
from django.views import View
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
import iyzipay

from memberships.services import PricingEngine
from .models import Payment, PaymentLog
from .utils import get_iyzi_options


User = get_user_model()


class PlansView(APIView):
	"""Return available membership plans and monthly fees."""

	def get(self, request: Request) -> Response:
		plans = {}
		for key, cfg in PricingEngine.MEMBERSHIP_PLANS.items():
			plans[key] = {
				"monthly_fee": str(cfg["monthly_fee"]),
			}
		return Response({"plans": plans})


class InitiatePaymentView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request: Request) -> Response:
		membership_type = (request.data.get("membership_type") or "").lower()
		if membership_type not in PricingEngine.MEMBERSHIP_PLANS:
			return Response({"detail": "Invalid membership_type"}, status=400)

		amount: Decimal = PricingEngine.MEMBERSHIP_PLANS[membership_type]["monthly_fee"]

		conversation_id = str(uuid.uuid4())
		basket_id = f"basket-{conversation_id[:8]}"

		# Create local Payment record first
		payment = Payment.objects.create(
			user=request.user,
			membership_type=membership_type,
			amount=amount,
			conversation_id=conversation_id,
			basket_id=basket_id,
			status="pending",
		)

		PaymentLog.objects.create(payment=payment, event="init:request", payload={"membership_type": membership_type, "amount": str(amount)})

		# Prepare Iyzico Checkout Form Initialize
		opts = get_iyzi_options()
		if not settings.IYZI_CALLBACK_URL:
			return Response({"detail": "IYZI_CALLBACK_URL not configured"}, status=500)

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
			# Minimal required fields for sandbox
			'buyer': {
				'id': str(request.user.id),
				'name': request.user.first_name or 'Name',
				'surname': request.user.last_name or 'Surname',
				'gsmNumber': '+905350000000',
				'email': request.user.email or 'test@example.com',
				'identityNumber': '74300864791',
				'registrationAddress': 'Nidakule Goztepe, Merdivenkoy Mah. Bora Sok. No:1',
				'ip': request.META.get('REMOTE_ADDR', '127.0.0.1'),
				'city': 'Istanbul',
				'country': 'Turkey',
				'zipCode': '34732'
			},
			'shippingAddress': {
				'contactName': 'Jane Doe',
				'city': 'Istanbul',
				'country': 'Turkey',
				'address': 'Nidakule Goztepe, Merdivenkoy Mah. Bora Sok. No:1',
				'zipCode': '34742'
			},
			'billingAddress': {
				'contactName': 'Jane Doe',
				'city': 'Istanbul',
				'country': 'Turkey',
				'address': 'Nidakule Goztepe, Merdivenkoy Mah. Bora Sok. No:1',
				'zipCode': '34742'
			},
			'basketItems': [
				{
					'id': f'{membership_type}-plan',
					'name': f'{membership_type.title()} Membership',
					'category1': 'Membership',
					'itemType': 'VIRTUAL',
					'price': str(amount)
				}
			]
		}

		checkout_form_init = iyzipay.CheckoutFormInitialize().create(request_payload, opts)
		resp = checkout_form_init.read().decode('utf-8')
		# Iyzipay SDK returns a JSON string
		import json
		data = json.loads(resp)
		PaymentLog.objects.create(payment=payment, event="init:response", payload=data)

		# Capture token if provided and return checkout form content/url
		token = data.get('token')
		payment.token = token or ''
		payment.raw_response = data
		payment.save(update_fields=["token", "raw_response", "updated_at"])

		return Response({
			"conversation_id": conversation_id,
			"token": token,
			"checkout_form_content": data.get('checkoutFormContent'),
			"payment_page_url": data.get('paymentPageUrl'),
			"status": data.get('status'),
		})


@method_decorator(csrf_exempt, name='dispatch')
class PaymentCallbackView(View):
	"""Iyzico posts back here with a token after user completes payment UI."""

	def post(self, request, *args, **kwargs):
		token = request.POST.get('token') or request.body.decode('utf-8')
		if not token:
			return HttpResponseBadRequest("Missing token")

		opts = get_iyzi_options()
		request_payload = {'locale': 'tr', 'token': token}
		result = iyzipay.CheckoutForm().retrieve(request_payload, opts)
		resp = result.read().decode('utf-8')
		import json
		data = json.loads(resp)

		# Fetch payment by token if exists, else try conversationId
		payment = Payment.objects.filter(token=token).order_by('-created_at').first()
		if not payment and data.get('conversationId'):
			payment = Payment.objects.filter(conversation_id=data['conversationId']).order_by('-created_at').first()

		if not payment:
			# No matching payment; log and return
			return JsonResponse({"detail": "payment not found", "iyzico": data}, status=404)

		PaymentLog.objects.create(payment=payment, event="callback", payload=data)

		status = (data.get('paymentStatus') or '').lower()
		if status == 'success':
			payment.status = 'success'
			payment.iyzico_payment_id = data.get('paymentId', '')
			payment.raw_response = data
			payment.save(update_fields=["status", "iyzico_payment_id", "raw_response", "updated_at"])

			# Activate/assign membership type to the user
			try:
				member_profile = payment.user.member_profile
				if member_profile.membership_type != payment.membership_type:
					member_profile.membership_type = payment.membership_type
					member_profile.save(update_fields=["membership_type"])
			except Exception:
				# If no profile or other issue, just continue
				pass

			return JsonResponse({"status": "ok", "payment": {
				"id": payment.id,
				"status": payment.status,
				"membership_type": payment.membership_type,
			}})
		else:
			payment.status = 'failed'
			payment.raw_response = data
			payment.save(update_fields=["status", "raw_response", "updated_at"])
			return JsonResponse({"status": "failed", "iyzico": data}, status=400)


class PaymentStatusView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request: Request, conversation_id: str) -> Response:
		payment = Payment.objects.filter(conversation_id=conversation_id, user=request.user).first()
		if not payment:
			return Response({"detail": "Not found"}, status=404)
		return Response({
			"id": payment.id,
			"status": payment.status,
			"membership_type": payment.membership_type,
			"amount": str(payment.amount),
			"currency": payment.currency,
			"created_at": payment.created_at,
		})

