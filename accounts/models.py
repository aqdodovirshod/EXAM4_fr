from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('seeker', 'Seeker'),
        ('employer', 'Employer'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='seeker')
    company = models.ForeignKey("api.Company", on_delete=models.SET_NULL, null=True, blank=True, related_name="employees")
