from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Campaign, Beneficiary, Task, Role
from rest_framework_simplejwt.tokens import RefreshToken

class UserRegistrationTest(APITestCase):
    def test_register_user(self):
        url = reverse('register')
        data = {'username': 'testuser', 'password': 'testpass123', 'email': 'test@example.com'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['message'], 'User registered successfully.')

class JWTAuthTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='jwtuser', password='jwtpass', email='jwt@example.com')
        Role.objects.create(user=self.user, role='admin')

    def test_jwt_login(self):
        url = reverse('token_obtain_pair')
        data = {'username': 'jwtuser', 'password': 'jwtpass'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

class CampaignCRUDTest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin', password='adminpass')
        Role.objects.create(user=self.admin, role='admin')
        self.client.force_authenticate(user=self.admin)

    def test_create_campaign(self):
        url = reverse('campaign-list')
        data = {'name': 'Test Campaign', 'description': 'Desc', 'start_date': '2025-01-01', 'end_date': '2025-12-31', 'is_active': True}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_list_campaigns(self):
        Campaign.objects.create(name='C1', description='D', start_date='2025-01-01', end_date='2025-12-31', is_active=True)
        url = reverse('campaign-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data), 1)

class BeneficiaryCRUDTest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='adminb', password='adminpassb')
        Role.objects.create(user=self.admin, role='admin')
        self.client.force_authenticate(user=self.admin)
        self.campaign = Campaign.objects.create(name='C2', description='D2', start_date='2025-01-01', end_date='2025-12-31', is_active=True)
        self.user_b = User.objects.create_user(username='benef', password='benefpass')

    def test_create_beneficiary(self):
        url = reverse('beneficiary-list')
        data = {'user': self.user_b.id, 'name': 'B1', 'email': 'b1@example.com', 'campaign': self.campaign.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)

class TaskCRUDTest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admint', password='adminpasst')
        Role.objects.create(user=self.admin, role='admin')
        self.client.force_authenticate(user=self.admin)
        self.campaign = Campaign.objects.create(name='C3', description='D3', start_date='2025-01-01', end_date='2025-12-31', is_active=True)
        self.user_b = User.objects.create_user(username='benef2', password='benefpass2')
        self.beneficiary = Beneficiary.objects.create(user=self.user_b, name='B2', email='b2@example.com', campaign=self.campaign)

    def test_create_task(self):
        url = reverse('task-list')
        data = {'description': 'T1', 'beneficiary': self.beneficiary.id, 'campaign': self.campaign.id, 'status': 'pending'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_task_ordering(self):
        Task.objects.create(description='T1', beneficiary=self.beneficiary, campaign=self.campaign, due_date='2025-06-01')
        Task.objects.create(description='T2', beneficiary=self.beneficiary, campaign=self.campaign, due_date='2025-05-01')
        url = reverse('task-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        due_dates = [task['due_date'] for task in response.data]
        self.assertEqual(due_dates, sorted(due_dates))

class PermissionsTest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='adminp', password='adminpassp')
        self.benef_user = User.objects.create_user(username='benefp', password='benefpassp')
        Role.objects.create(user=self.admin, role='admin')
        Role.objects.create(user=self.benef_user, role='beneficiary')
        self.campaign = Campaign.objects.create(name='C4', description='D4', start_date='2025-01-01', end_date='2025-12-31', is_active=True)
        self.beneficiary = Beneficiary.objects.create(user=self.benef_user, name='B3', email='b3@example.com', campaign=self.campaign)

    def test_admin_can_create_campaign(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('campaign-list')
        data = {'name': 'C5', 'description': 'D5', 'start_date': '2025-01-01', 'end_date': '2025-12-31', 'is_active': True}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_beneficiary_cannot_create_campaign(self):
        self.client.force_authenticate(user=self.benef_user)
        url = reverse('campaign-list')
        data = {'name': 'C6', 'description': 'D6', 'start_date': '2025-01-01', 'end_date': '2025-12-31', 'is_active': True}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_beneficiary_can_list_tasks(self):
        self.client.force_authenticate(user=self.benef_user)
        url = reverse('task-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
