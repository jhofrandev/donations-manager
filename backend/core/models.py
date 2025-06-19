from django.db import models
from django.contrib.auth.models import User

class Role(models.Model):
    ADMIN = 'admin'
    BENEFICIARY = 'beneficiary'
    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (BENEFICIARY, 'Beneficiary'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

class Campaign(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

class Beneficiary(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='beneficiaries')

class Task(models.Model):
    description = models.CharField(max_length=255)
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.CASCADE, related_name='tasks')
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='tasks')
    status = models.CharField(max_length=50, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)

    class Meta:
        ordering = ['beneficiary', 'due_date']
