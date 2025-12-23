from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.db import IntegrityError
from decimal import Decimal
from datetime import timedelta

from rest_framework.test import APIClient
from rest_framework import status

from classes.models import FitnessClass
from .models import Reservation

User = get_user_model()

class ReservationModelTests(TestCase):
    def setUp(self):
        self.instructor = User.objects.create_user(email='inst@test.com', password='pass')
        self.user = User.objects.create_user(email='member@test.com', password='pass')
        self.member = self.user.member_profile

        self.future_off_peak = timezone.now() + timedelta(days=3)
        self.future_off_peak = self.future_off_peak.replace(hour=10, minute=0)

        self.future_peak = timezone.now() + timedelta(days=4)
        self.future_peak = self.future_peak.replace(hour=19, minute=0)

        self.class_off_peak = FitnessClass.objects.create(
            name='Off Peak Class',
            instructor=self.instructor,
            capacity=10,
            date_time=self.future_off_peak,
            base_price=Decimal('200.00')
        )

        self.class_peak = FitnessClass.objects.create(
            name='Peak Class',
            instructor=self.instructor,
            capacity=10,
            date_time=self.future_peak,
            base_price=Decimal('200.00')
        )

    def test_reservation_creation_basic(self):
        reservation = Reservation.objects.create(
            member=self.member,
            fitness_class=self.class_off_peak,
            price_paid=Decimal('200.00')
        )
        self.assertEqual(reservation.member, self.member)
        self.assertEqual(reservation.fitness_class, self.class_off_peak)
        self.assertEqual(reservation.price_paid, Decimal('200.00'))
        self.assertIsNotNone(reservation.created_at)

    def test_unique_constraint_prevents_duplicate(self):
        Reservation.objects.create(
            member=self.member,
            fitness_class=self.class_off_peak,
            price_paid=Decimal('200.00')
        )
        with self.assertRaises(IntegrityError):
            Reservation.objects.create(
                member=self.member,
                fitness_class=self.class_off_peak,
                price_paid=Decimal('200.00')
            )

    def test_capacity_validation_blocks_overbooking(self):
        for i in range(10):
            u = User.objects.create_user(email=f'fill{i}@test.com', password='pass')
            Reservation.objects.create(
                member=u.member_profile,
                fitness_class=self.class_off_peak,
                price_paid=Decimal('200.00')
            )

        new_user = User.objects.create_user(email='over@test.com', password='pass')
        reservation = Reservation(
            member=new_user.member_profile,
            fitness_class=self.class_off_peak,
            price_paid=Decimal('200.00')
        )
        with self.assertRaises(Exception):  
            reservation.full_clean()

    def test_price_auto_calculation_standard_off_peak(self):
        reservation = Reservation(
            member=self.member,
            fitness_class=self.class_off_peak,
            price_paid=None
        )
        reservation.save()
        self.assertEqual(reservation.price_paid, Decimal('200.00'))

    def test_price_auto_calculation_student_peak_with_surge(self):
        self.member.membership_type = 'student'
        self.member.save()

        for i in range(8):
            u = User.objects.create_user(email=f'surge{i}@test.com', password='pass')
            Reservation.objects.create(
                member=u.member_profile,
                fitness_class=self.class_peak,
                price_paid=Decimal('200.00')
            )

        reservation = Reservation(
            member=self.member,
            fitness_class=self.class_peak,
            price_paid=None
        )
        reservation.save()
        self.assertEqual(reservation.price_paid, Decimal('192.00'))

    def test_price_auto_calculation_premium_free(self):
        self.member.membership_type = 'premium'
        self.member.save()

        reservation = Reservation(
            member=self.member,
            fitness_class=self.class_peak,
            price_paid=None
        )
        reservation.save()
        self.assertEqual(reservation.price_paid, Decimal('0.00'))

    def test_explicit_price_preserved(self):
        reservation = Reservation(
            member=self.member,
            fitness_class=self.class_off_peak,
            price_paid=Decimal('150.00')
        )
        reservation.save()
        self.assertEqual(reservation.price_paid, Decimal('150.00'))

    def test_cascade_delete_member_removes_reservation(self):
        reservation = Reservation.objects.create(
            member=self.member,
            fitness_class=self.class_off_peak,
            price_paid=Decimal('200.00')
        )
        res_id = reservation.id
        self.user.delete()
        with self.assertRaises(Reservation.DoesNotExist):
            Reservation.objects.get(id=res_id)

    def test_cascade_delete_class_removes_reservation(self):
        reservation = Reservation.objects.create(
            member=self.member,
            fitness_class=self.class_off_peak,
            price_paid=Decimal('200.00')
        )
        res_id = reservation.id
        self.class_off_peak.delete()
        with self.assertRaises(Reservation.DoesNotExist):
            Reservation.objects.get(id=res_id)


class ReservationMembershipLimitTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.instructor = User.objects.create_user(email='inst@test.com', password='pass')

        base_time = timezone.now() + timedelta(days=5)
        self.classes = []
        for i in range(15):
            cls = FitnessClass.objects.create(
                name=f'Class {i}',
                instructor=self.instructor,
                capacity=10,
                date_time=base_time + timedelta(days=i),
                base_price=Decimal('100.00')
            )
            self.classes.append(cls)

    def _create_user_and_auth(self, membership_type):
        user = User.objects.create_user(email=f'{membership_type}@test.com', password='pass')
        user.member_profile.membership_type = membership_type
        user.member_profile.save()
        self.client.force_authenticate(user=user)
        return user

    def test_student_max_3_future_reservations(self):
        self._create_user_and_auth('student')
        for i in range(3):
            response = self.client.post(reverse('reservation-list-create'), {'fitness_class_id': self.classes[i].id})
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(reverse('reservation-list-create'), {'fitness_class_id': self.classes[3].id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_standard_max_5_future_reservations(self):
        self._create_user_and_auth('standard')
        for i in range(5):
            response = self.client.post(reverse('reservation-list-create'), {'fitness_class_id': self.classes[i].id})
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(reverse('reservation-list-create'), {'fitness_class_id': self.classes[5].id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_premium_max_10_future_reservations(self):
        self._create_user_and_auth('premium')
        for i in range(10):
            response = self.client.post(reverse('reservation-list-create'), {'fitness_class_id': self.classes[i].id})
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(reverse('reservation-list-create'), {'fitness_class_id': self.classes[10].id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ReservationAPIListCreateTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('reservation-list-create')

        self.instructor = User.objects.create_user(email='inst@test.com', password='pass')
        self.user = User.objects.create_user(email='apiuser@test.com', password='pass')

        self.class1 = FitnessClass.objects.create(
            name='API Class',
            instructor=self.instructor,
            capacity=5,
            date_time=timezone.now() + timedelta(days=3),
            base_price=Decimal('150.00')
        )

    def test_unauthenticated_denied(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.post(self.url, {'fitness_class_id': self.class1.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_returns_only_own_reservations(self):
        other_user = User.objects.create_user(email='other@test.com', password='pass')
        Reservation.objects.create(member=other_user.member_profile, fitness_class=self.class1, price_paid=Decimal('150.00'))
        Reservation.objects.create(member=self.user.member_profile, fitness_class=self.class1, price_paid=Decimal('150.00'))

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_post_creates_with_correct_price(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {'fitness_class_id': self.class1.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        reservation = Reservation.objects.get(member=self.user.member_profile)
        self.assertEqual(reservation.price_paid, Decimal('150.00'))

    def test_post_duplicate_returns_400(self):
        self.client.force_authenticate(user=self.user)
        self.client.post(self.url, {'fitness_class_id': self.class1.id})
        response = self.client.post(self.url, {'fitness_class_id': self.class1.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_full_class_returns_400(self):
        for i in range(5):
            u = User.objects.create_user(email=f'full{i}@test.com', password='pass')
            Reservation.objects.create(member=u.member_profile, fitness_class=self.class1, price_paid=Decimal('150.00'))

        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {'fitness_class_id': self.class1.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_invalid_class_id_returns_400(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {'fitness_class_id': 99999})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_missing_field_returns_400(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ReservationAPIDeleteTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.instructor = User.objects.create_user(email='inst@test.com', password='pass')
        self.user = User.objects.create_user(email='deluser@test.com', password='pass')

        self.class1 = FitnessClass.objects.create(
            name='Delete Class',
            instructor=self.instructor,
            capacity=10,
            date_time=timezone.now() + timedelta(days=3),
            base_price=Decimal('100.00')
        )

        self.reservation = Reservation.objects.create(
            member=self.user.member_profile,
            fitness_class=self.class1,
            price_paid=Decimal('100.00')
        )

    def test_delete_success(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('reservation-detail', kwargs={'pk': self.reservation.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Reservation.DoesNotExist):
            Reservation.objects.get(id=self.reservation.id)

    def test_delete_other_user_forbidden(self):
        other_user = User.objects.create_user(email='other@test.com', password='pass')
        self.client.force_authenticate(user=other_user)
        url = reverse('reservation-detail', kwargs={'pk': self.reservation.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_nonexistent_404(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('reservation-detail', kwargs={'pk': 99999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_unauthenticated_denied(self):
        url = reverse('reservation-detail', kwargs={'pk': self.reservation.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ReservationEdgeCaseTests(TestCase):
    def setUp(self):
        self.instructor = User.objects.create_user(email='edgeinst@test.com', password='pass')

    def test_reservation_with_zero_price_premium(self):
        user = User.objects.create_user(email='premium@test.com', password='pass')
        user.member_profile.membership_type = 'premium'
        user.member_profile.save()

        cls = FitnessClass.objects.create(
            name='Premium Free',
            instructor=self.instructor,
            capacity=10,
            date_time=timezone.now() + timedelta(days=1),
            base_price=Decimal('500.00')
        )

        reservation = Reservation.objects.create(
            member=user.member_profile,
            fitness_class=cls,
            price_paid=None
        )
        self.assertEqual(reservation.price_paid, Decimal('0.00'))

    def test_reservation_price_not_negative(self):
        user = User.objects.create_user(email='highsurge@test.com', password='pass')
        cls = FitnessClass.objects.create(
            name='High Surge',
            instructor=self.instructor,
            capacity=10,
            date_time=timezone.now().replace(hour=10),
            base_price=Decimal('1.00')
        )

        for i in range(9):
            u = User.objects.create_user(email=f'fill{i}@test.com', password='pass')
            Reservation.objects.create(member=u.member_profile, fitness_class=cls, price_paid=Decimal('1.00'))

        reservation = Reservation(
            member=user.member_profile,
            fitness_class=cls,
            price_paid=None
        )
        reservation.save()
        self.assertGreaterEqual(reservation.price_paid, Decimal('0.00'))