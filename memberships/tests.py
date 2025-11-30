from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Member


class MemberModelTest(TestCase):
    """Test cases for the Member model."""
    
    def setUp(self):
        self.member = Member.objects.create(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            phone='555-1234',
            membership_type='basic'
        )
    
    def test_member_creation(self):
        """Test that a member can be created."""
        self.assertEqual(self.member.first_name, 'John')
        self.assertEqual(self.member.last_name, 'Doe')
        self.assertEqual(self.member.email, 'john.doe@example.com')
        self.assertTrue(self.member.is_active)
    
    def test_member_full_name(self):
        """Test the full_name property."""
        self.assertEqual(self.member.full_name, 'John Doe')
    
    def test_member_str(self):
        """Test the string representation of Member."""
        self.assertEqual(str(self.member), 'John Doe')
    
    def test_member_ordering(self):
        """Test that members are ordered by last name, then first name."""
        Member.objects.create(
            first_name='Alice',
            last_name='Smith',
            email='alice@example.com'
        )
        Member.objects.create(
            first_name='Bob',
            last_name='Anderson',
            email='bob@example.com'
        )
        members = list(Member.objects.all())
        self.assertEqual(members[0].last_name, 'Anderson')
        self.assertEqual(members[1].last_name, 'Doe')
        self.assertEqual(members[2].last_name, 'Smith')


class MemberAPITest(APITestCase):
    """Test cases for the Member API endpoints."""
    
    def setUp(self):
        self.member = Member.objects.create(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            phone='555-1234',
            membership_type='basic'
        )
        self.list_url = reverse('member-list')
        self.detail_url = reverse('member-detail', kwargs={'pk': self.member.pk})
    
    def test_list_members(self):
        """Test listing all members."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_member(self):
        """Test creating a new member."""
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane.smith@example.com',
            'phone': '555-5678',
            'membership_type': 'premium'
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Member.objects.count(), 2)
        self.assertEqual(response.data['full_name'], 'Jane Smith')
    
    def test_retrieve_member(self):
        """Test retrieving a specific member."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'john.doe@example.com')
    
    def test_update_member(self):
        """Test updating a member."""
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.updated@example.com',
            'membership_type': 'premium'
        }
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.member.refresh_from_db()
        self.assertEqual(self.member.email, 'john.updated@example.com')
    
    def test_delete_member(self):
        """Test deleting a member."""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Member.objects.count(), 0)
    
    def test_active_members_endpoint(self):
        """Test the active members endpoint."""
        Member.objects.create(
            first_name='Inactive',
            last_name='User',
            email='inactive@example.com',
            is_active=False
        )
        url = reverse('member-active')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_unique_email_constraint(self):
        """Test that duplicate emails are rejected."""
        data = {
            'first_name': 'Another',
            'last_name': 'Person',
            'email': 'john.doe@example.com',
            'membership_type': 'basic'
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_search_members(self):
        """Test searching members."""
        Member.objects.create(
            first_name='Alice',
            last_name='Wonder',
            email='alice@example.com'
        )
        url = f"{self.list_url}?search=Alice"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['full_name'], 'Alice Wonder')
