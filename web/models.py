from django.db import models

# Create your models here.

class Question(models.Model):
    answer = models.CharField(max_length = 100)
