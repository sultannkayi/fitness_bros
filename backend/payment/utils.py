from dataclasses import dataclass
from django.conf import settings
import iyzipay


@dataclass
class IyziOptions:
    api_key: str
    secret_key: str
    base_url: str


def get_iyzi_options() -> iyzipay.Options:
    opts = iyzipay.Options()
    opts.api_key = settings.IYZI_API_KEY
    opts.secret_key = settings.IYZI_SECRET_KEY
    opts.base_url = settings.IYZI_BASE_URL
    return opts
