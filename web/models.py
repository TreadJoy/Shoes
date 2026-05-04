from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

# AbstractUser allows our user class to inherit Django's user fields (Username, password, first name, last name, etc.)
# while using its authentication system in addition to our own fieldsclass User(AbstractUser):

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.FloatField()