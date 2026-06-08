from django.db import models


class WaitlistSignup(models.Model):
    objects = None
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    source = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.first_name:
            return f"{self.first_name} - {self.email}"
        return self.email