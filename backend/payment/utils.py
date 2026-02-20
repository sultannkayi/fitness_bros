from dataclasses import dataclass
from django.conf import settings
import iyzipay # type: ignore


@dataclass
class IyziOptions:
    api_key: str
    secret_key: str
    base_url: str


def get_iyzi_options():
    return {
        'api_key': settings.IYZI_API_KEY,
        'secret_key': settings.IYZI_SECRET_KEY,
        'base_url': settings.IYZI_BASE_URL,  
    }