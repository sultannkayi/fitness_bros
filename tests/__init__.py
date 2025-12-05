import pytest
from django.test import TestCase

class BasicTestCase(TestCase):
    """Basic test to ensure Django setup is working"""
    
    def test_django_setup(self):
        """Test that Django is properly configured"""
        assert True
    
    def test_apps_loaded(self):
        """Test that our apps are loaded"""
        from django.apps import apps
        assert apps.is_installed('classes')
        assert apps.is_installed('bookings')