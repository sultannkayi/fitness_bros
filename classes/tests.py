from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import timedelta
from decimal import Decimal
from .models import FitnessClass


class FitnessClassModelTest(TestCase):
    """Test cases for the FitnessClass model."""
    
    def setUp(self):
        self.fitness_class = FitnessClass.objects.create(
            name='Morning Yoga',
            class_type='yoga',
            description='A refreshing morning yoga session',
            instructor='Jane Smith',
            schedule=timezone.now() + timedelta(days=1),
            duration_minutes=60,
            capacity=20,
            price=Decimal('15.00')
        )
    
    def test_fitness_class_creation(self):
        """Test that a fitness class can be created."""
        self.assertEqual(self.fitness_class.name, 'Morning Yoga')
        self.assertEqual(self.fitness_class.class_type, 'yoga')
        self.assertEqual(self.fitness_class.capacity, 20)
        self.assertTrue(self.fitness_class.is_active)
    
    def test_available_spots(self):
        """Test the available_spots property with no reservations."""
        self.assertEqual(self.fitness_class.available_spots, 20)
    
    def test_is_full(self):
        """Test the is_full property with no reservations."""
        self.assertFalse(self.fitness_class.is_full)
    
    def test_fitness_class_str(self):
        """Test the string representation of FitnessClass."""
        expected = f"Morning Yoga - {self.fitness_class.schedule.strftime('%Y-%m-%d %H:%M')}"
        self.assertEqual(str(self.fitness_class), expected)
    
    def test_fitness_class_ordering(self):
        """Test that fitness classes are ordered by schedule."""
        later_class = FitnessClass.objects.create(
            name='Evening HIIT',
            class_type='hiit',
            instructor='John Doe',
            schedule=timezone.now() + timedelta(days=2),
            capacity=15
        )
        classes = list(FitnessClass.objects.all())
        self.assertEqual(classes[0].name, 'Morning Yoga')
        self.assertEqual(classes[1].name, 'Evening HIIT')


class FitnessClassAPITest(APITestCase):
    """Test cases for the FitnessClass API endpoints."""
    
    def setUp(self):
        self.fitness_class = FitnessClass.objects.create(
            name='Morning Yoga',
            class_type='yoga',
            description='A refreshing morning yoga session',
            instructor='Jane Smith',
            schedule=timezone.now() + timedelta(days=1),
            duration_minutes=60,
            capacity=20,
            price=Decimal('15.00')
        )
        self.list_url = reverse('fitnessclass-list')
        self.detail_url = reverse('fitnessclass-detail', kwargs={'pk': self.fitness_class.pk})
    
    def test_list_fitness_classes(self):
        """Test listing all fitness classes."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_fitness_class(self):
        """Test creating a new fitness class."""
        data = {
            'name': 'Evening Pilates',
            'class_type': 'pilates',
            'description': 'Relaxing pilates session',
            'instructor': 'Sarah Johnson',
            'schedule': (timezone.now() + timedelta(days=3)).isoformat(),
            'duration_minutes': 45,
            'capacity': 15,
            'price': '20.00'
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FitnessClass.objects.count(), 2)
    
    def test_retrieve_fitness_class(self):
        """Test retrieving a specific fitness class."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Morning Yoga')
        self.assertEqual(response.data['available_spots'], 20)
        self.assertFalse(response.data['is_full'])
    
    def test_update_fitness_class(self):
        """Test updating a fitness class."""
        data = {
            'name': 'Morning Power Yoga',
            'class_type': 'yoga',
            'instructor': 'Jane Smith',
            'schedule': self.fitness_class.schedule.isoformat(),
            'capacity': 25
        }
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.fitness_class.refresh_from_db()
        self.assertEqual(self.fitness_class.name, 'Morning Power Yoga')
        self.assertEqual(self.fitness_class.capacity, 25)
    
    def test_delete_fitness_class(self):
        """Test deleting a fitness class."""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(FitnessClass.objects.count(), 0)
    
    def test_search_fitness_classes(self):
        """Test searching fitness classes."""
        FitnessClass.objects.create(
            name='Spinning Class',
            class_type='spinning',
            instructor='Mike Brown',
            schedule=timezone.now() + timedelta(days=2),
            capacity=10
        )
        url = f"{self.list_url}?search=Yoga"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Morning Yoga')
