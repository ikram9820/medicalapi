from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
  COURTESY_MR = 'MR'
  COURTESY_MS = 'MS'

  COURTESY_CHOICES = [
        (COURTESY_MR,'Mr'),
        (COURTESY_MS,'Ms'),

    ]
  courtesy = models.CharField(
         max_length=2, choices=COURTESY_CHOICES, default=COURTESY_MR)
  email = models.EmailField(unique=True)