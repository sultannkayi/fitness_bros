# payments/services.py
import iyzipay
from django.conf import settings
from decimal import Decimal
import uuid
import logging
import json 

logger = logging.getLogger(__name__)

class IyzicoService:
    @staticmethod
    def get_options():
        # Options sınıfı yoksa manuel dict döndür (iyzipay kabul eder)
        return {
            'api_key': settings.IYZICO_API_KEY,
            'secret_key': settings.IYZICO_SECRET_KEY,
            'base_url': settings.IYZICO_BASE_URL
        }

    @classmethod
    def create_checkout_form(cls, payment_obj):
        """
        Üyelik ödemesi için Iyzico checkout formu başlatır.
        """
        try:
            buyer = {
                'id': str(payment_obj.member.user.id),
                'name': payment_obj.member.user.first_name or 'Kullanıcı',
                'surname': payment_obj.member.user.last_name or 'Soyad',
                'email': payment_obj.member.user.email or 'test@fitnessbros.com',
                'identityNumber': '11111111111',
                'lastLoginDate': '2025-01-01 00:00:00',
                'registrationDate': '2024-01-01 00:00:00',
                'registrationAddress': 'Adres Bilgisi Yok',
                'city': 'Adana',
                'country': 'Turkey',
                'zipCode': '01000',
                'ip': '127.0.0.1'
            }

            address = {
                'contactName': f"{buyer['name']} {buyer['surname']}",
                'city': 'Adana',
                'country': 'Turkey',
                'address': 'Test Adresi',
                'zipCode': '01000'
            }

            basket_item = {
                'id': str(uuid.uuid4()),
                'name': f"Üyelik Yenileme - {payment_obj.get_new_membership_type_display()}",
                'category1': 'Üyelik',
                'itemType': 'VIRTUAL',
                'price': str(payment_obj.amount)
            }

            request = {
                'locale': 'tr',
                'conversationId': str(uuid.uuid4()),
                'price': str(payment_obj.amount),
                'paidPrice': str(payment_obj.amount),
                'paymentGroup': 'PRODUCT',
                'callbackUrl': settings.IYZICO_CALLBACK_URL,
                'enabledInstallments': ['2', '3', '6', '9'],
                'currency': 'TRY',
                'buyer': buyer,
                'billingAddress': address,
                'shippingAddress': address,
                'basketItems': [basket_item]
            }

            checkout_form_init = iyzipay.CheckoutFormInitialize()
            raw_result = checkout_form_init.create(request, cls.get_options())

            logger.info(f"Raw result tipi: {type(raw_result)}")

            # Response'ı doğru parse et
            if hasattr(raw_result, 'read'):  # HTTPResponse ise
                response_body = raw_result.read().decode('utf-8')
                logger.info(f"Iyzico Raw Response Body: {response_body}")
                try:
                    result = json.loads(response_body)  # ← STANDART json.loads
                except Exception as parse_err:
                    logger.error(f"JSON parse hatası: {parse_err}")
                    return {'status': 'error', 'message': 'Yanıt parse edilemedi: ' + str(parse_err)}
            elif isinstance(raw_result, dict):
                result = raw_result
            else:
                logger.error(f"Beklenmeyen response tipi: {type(raw_result)}")
                return {'status': 'error', 'message': f'Beklenmeyen response tipi: {type(raw_result)}'}

            logger.info(f"Parsed Iyzico Yanıtı: {result}")

            if isinstance(result, dict) and result.get('status') == 'success':
                payment_obj.iyzico_conversation_id = result.get('conversationId')

                # Token'ı yakala – Iyzico 3 şekilde gönderebiliyor
                token = result.get('token')
                if not token and 'checkoutFormContent' in result:
                    # checkoutFormContent içinde token olabilir (base64 veya HTML içinde)
                    content = result.get('checkoutFormContent', '')
                    # Basit string arama (gerçekte regex daha iyi olur, ama test için)
                    if 'token' in content:
                        token = content.split('token=')[1].split('"')[0] if 'token=' in content else None

                if token:
                    payment_obj.iyzico_transaction_id = token
                    logger.info(f"Token başarıyla kaydedildi: {token}")
                else:
                    logger.warning("Token yakalanamadı! Full result: " + str(result))

                payment_obj.save(update_fields=['iyzico_conversation_id', 'iyzico_transaction_id'])

                payment_page_url = result.get('paymentPageUrl')
                if not payment_page_url:
                    logger.warning("paymentPageUrl dönmedi!")
                    return {'status': 'error', 'message': 'Ödeme sayfası linki dönmedi'}

                logger.info(f"Başarılı ödeme başlatma - URL: {payment_page_url}, Token: {token}")
                return {
                    'status': 'success',
                    'payment_page_url': payment_page_url,
                    'conversation_id': result.get('conversationId'),
                    'token': token
             }

        except Exception as e:
            logger.exception("Iyzico genel hata")
            return {'status': 'error', 'message': str(e)}