from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import timedelta
from decimal import Decimal
from .models import Reservation
from memberships.models import Member
from classes.models import FitnessClass


class ReservationModelTest(TestCase):
    """Test cases for the Reservation model."""
    
    def setUp(self):
        self.member = Member.objects.create(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            membership_type='basic'
        )
        self.fitness_class = FitnessClass.objects.create(
            name='Morning Yoga',
            class_type='yoga',
            instructor='Jane Smith',
            schedule=timezone.now() + timedelta(days=1),
            capacity=2,
            price=Decimal('15.00')
        )
    
    def test_reservation_creation(self):
        """Test that a reservation can be created."""
        reservation = Reservation.objects.create(
            member=self.member,
            fitness_class=self.fitness_class,
            status='confirmed'
        )
        self.assertEqual(reservation.member, self.member)
        self.assertEqual(reservation.fitness_class, self.fitness_class)
        self.assertEqual(reservation.status, 'confirmed')
    
    def test_reservation_str(self):
        """Test the string representation of Reservation."""
        reservation = Reservation.objects.create(
            member=self.member,
            fitness_class=self.fitness_class
        )
        expected = f"John Doe - Morning Yoga"
        self.assertEqual(str(reservation), expected)
    
    def test_capacity_check(self):
        """Test that capacity check prevents overbooking."""
        member2 = Member.objects.create(
            first_name='Jane',
            last_name='Smith',
            email='jane@example.com'
        )
        member3 = Member.objects.create(
            first_name='Bob',
            last_name='Wilson',
            email='bob@example.com'
        )
        
        # First two reservations should work (capacity is 2)
        Reservation.objects.create(
            member=self.member,
            fitness_class=self.fitness_class,
            status='confirmed'
        )
        Reservation.objects.create(
            member=member2,
            fitness_class=self.fitness_class,
            status='confirmed'
        )
        
        # Third reservation should fail
        with self.assertRaises(ValidationError) as context:
            Reservation.objects.create(
                member=member3,
                fitness_class=self.fitness_class,
                status='confirmed'
            )
        self.assertIn('fitness_class', context.exception.message_dict)
    
    def test_available_spots_decreases(self):
        """Test that available spots decreases with reservations."""
        self.assertEqual(self.fitness_class.available_spots, 2)
        
        Reservation.objects.create(
            member=self.member,
            fitness_class=self.fitness_class,
            status='confirmed'
        )
        self.assertEqual(self.fitness_class.available_spots, 1)
    
    def test_cancelled_reservations_dont_count_towards_capacity(self):
        """Test that cancelled reservations don't count towards capacity."""
        member2 = Member.objects.create(
            first_name='Jane',
            last_name='Smith',
            email='jane@example.com'
        )
        member3 = Member.objects.create(
            first_name='Bob',
            last_name='Wilson',
            email='bob@example.com'
        )
        
        # Create and cancel first reservation
        reservation1 = Reservation.objects.create(
            member=self.member,
            fitness_class=self.fitness_class,
            status='cancelled'
        )
        
        # These should both work since cancelled doesn't count
        Reservation.objects.create(
            member=member2,
            fitness_class=self.fitness_class,
            status='confirmed'
        )
        Reservation.objects.create(
            member=member3,
            fitness_class=self.fitness_class,
            status='confirmed'
        )
        
        self.assertEqual(self.fitness_class.available_spots, 0)
    
    def test_inactive_member_cannot_reserve(self):
        """Test that inactive members cannot make reservations."""
        inactive_member = Member.objects.create(
            first_name='Inactive',
            last_name='User',
            email='inactive@example.com',
            is_active=False
        )
        
        with self.assertRaises(ValidationError) as context:
            Reservation.objects.create(
                member=inactive_member,
                fitness_class=self.fitness_class,
                status='confirmed'
            )
        self.assertIn('member', context.exception.message_dict)
    
    def test_unique_member_class_constraint(self):
        """Test that a member cannot make duplicate reservations."""
        Reservation.objects.create(
            member=self.member,
            fitness_class=self.fitness_class
        )
        
        # ValidationError will be raised due to unique_together constraint
        with self.assertRaises(ValidationError):
            Reservation.objects.create(
                member=self.member,
                fitness_class=self.fitness_class
            )


class ReservationAPITest(APITestCase):
    """Test cases for the Reservation API endpoints."""
    
    def setUp(self):
        self.member = Member.objects.create(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            membership_type='basic'
        )
        self.member2 = Member.objects.create(
            first_name='Jane',
            last_name='Smith',
            email='jane@example.com',
            membership_type='premium'
        )
        self.fitness_class = FitnessClass.objects.create(
            name='Morning Yoga',
            class_type='yoga',
            instructor='Jane Smith',
            schedule=timezone.now() + timedelta(days=1),
            capacity=2,
            price=Decimal('15.00')
        )
        self.reservation = Reservation.objects.create(
            member=self.member,
            fitness_class=self.fitness_class,
            status='confirmed'
        )
        self.list_url = reverse('reservation-list')
        self.detail_url = reverse('reservation-detail', kwargs={'pk': self.reservation.pk})
    
    def test_list_reservations(self):
        """Test listing all reservations."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_reservation(self):
        """Test creating a new reservation."""
        data = {
            'member': self.member2.pk,
            'fitness_class': self.fitness_class.pk,
            'status': 'confirmed'
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reservation.objects.count(), 2)
    
    def test_create_reservation_capacity_exceeded(self):
        """Test that creating a reservation fails when class is full."""
        # First fill the class (capacity 2, one already reserved)
        Reservation.objects.create(
            member=self.member2,
            fitness_class=self.fitness_class,
            status='confirmed'
        )
        
        # Try to add a third
        member3 = Member.objects.create(
            first_name='Bob',
            last_name='Wilson',
            email='bob@example.com'
        )
        data = {
            'member': member3.pk,
            'fitness_class': self.fitness_class.pk,
            'status': 'confirmed'
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('fitness_class', response.data)
    
    def test_retrieve_reservation(self):
        """Test retrieving a specific reservation."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['member'], self.member.pk)
    
    def test_cancel_reservation(self):
        """Test cancelling a reservation via the cancel endpoint."""
        cancel_url = reverse('reservation-cancel', kwargs={'pk': self.reservation.pk})
        response = self.client.post(cancel_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.reservation.refresh_from_db()
        self.assertEqual(self.reservation.status, 'cancelled')
    
    def test_cancel_already_cancelled(self):
        """Test that cancelling an already cancelled reservation returns error."""
        self.reservation.status = 'cancelled'
        self.reservation.save()
        
        cancel_url = reverse('reservation-cancel', kwargs={'pk': self.reservation.pk})
        response = self.client.post(cancel_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_confirmed_reservations_endpoint(self):
        """Test the confirmed reservations endpoint."""
        Reservation.objects.create(
            member=self.member2,
            fitness_class=self.fitness_class,
            status='cancelled'
        )
        url = reverse('reservation-confirmed')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_delete_reservation(self):
        """Test deleting a reservation."""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Reservation.objects.count(), 0)


class CapacityIntegrationTest(APITestCase):
    """Integration tests for capacity checking across the system."""
    
    def setUp(self):
        self.fitness_class = FitnessClass.objects.create(
            name='Small Class',
            class_type='yoga',
            instructor='Test Instructor',
            schedule=timezone.now() + timedelta(days=1),
            capacity=3
        )
    
    def test_capacity_tracking_through_api(self):
        """Test that capacity is properly tracked through API operations."""
        # Create 3 members
        members = []
        for i in range(4):
            member = Member.objects.create(
                first_name=f'Member{i}',
                last_name='Test',
                email=f'member{i}@test.com'
            )
            members.append(member)
        
        # Check initial availability
        response = self.client.get(
            reverse('fitnessclass-detail', kwargs={'pk': self.fitness_class.pk})
        )
        self.assertEqual(response.data['available_spots'], 3)
        self.assertFalse(response.data['is_full'])
        
        # Make 3 reservations
        list_url = reverse('reservation-list')
        for i in range(3):
            data = {
                'member': members[i].pk,
                'fitness_class': self.fitness_class.pk,
                'status': 'confirmed'
            }
            response = self.client.post(list_url, data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check class is now full
        response = self.client.get(
            reverse('fitnessclass-detail', kwargs={'pk': self.fitness_class.pk})
        )
        self.assertEqual(response.data['available_spots'], 0)
        self.assertTrue(response.data['is_full'])
        
        # Try to make 4th reservation - should fail
        data = {
            'member': members[3].pk,
            'fitness_class': self.fitness_class.pk,
            'status': 'confirmed'
        }
        response = self.client.post(list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
