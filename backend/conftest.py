# Test configuration for pytest-django
import os
import django
from django.conf import settings

# Django ayarlarını pytest için yapılandır
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

def pytest_configure():
    """pytest başlatıldığında Django'yu configure et"""
    django.setup()