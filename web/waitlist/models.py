from django.db import models
from django.db.models.functions import Lower


WAITLIST_SOURCE_HOMEPAGE = "homepage"
WAITLIST_SOURCE_PAGE = "waitlist_page"
WAITLIST_SOURCE_UNKNOWN = "unknown"
WAITLIST_SOURCE_CHOICES = (
    (WAITLIST_SOURCE_HOMEPAGE, "Homepage"),
    (WAITLIST_SOURCE_PAGE, "Waitlist page"),
    (WAITLIST_SOURCE_UNKNOWN, "Unknown"),
)


class WaitlistSignup(models.Model):
    email = models.EmailField()
    first_name = models.CharField(max_length=100, blank=True)
    source = models.CharField(
        max_length=20,
        choices=WAITLIST_SOURCE_CHOICES,
        default=WAITLIST_SOURCE_UNKNOWN,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower("email"),
                name="waitlistsignup_email_ci_unique",
            ),
        ]

    def save(self, *args, **kwargs):
        self.email = self.email.strip().lower()
        self.first_name = self.first_name.strip()
        if self.source not in {
            WAITLIST_SOURCE_HOMEPAGE,
            WAITLIST_SOURCE_PAGE,
            WAITLIST_SOURCE_UNKNOWN,
        }:
            self.source = WAITLIST_SOURCE_UNKNOWN
        super().save(*args, **kwargs)

    def __str__(self):
        if self.first_name:
            return f"{self.first_name} - {self.email}"
        return self.email
