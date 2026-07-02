from django.conf import settings
from django.db import models

class SurveyResponse(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="survey_responses",
    )

    session_key = models.CharField(
        max_length=40,
        blank=True,
        db_index=True,
    )

    STYLE_CHOICES = [
        ("athletic", "Athletic"),
        ("casual", "Casual"),
        ("streetwear", "Streetwear"),
        ("formal", "Formal"),
        ("outdoor", "Outdoor"),
    ]

    COMFORT_CHOICES = [
        ("very_important", "Very Important"),
        ("somewhat_important", "Somewhat Important"),
        ("neutral", "Neutral"),
        ("not_important", "Not Important"),
    ]

    PRICE_CHOICES = [
        ("under_50", "Under $50"),
        ("50_100", "$50 - $100"),
        ("100_150", "$100 - $150"),
        ("150_plus", "$150+"),
    ]

    style_preference = models.CharField(max_length=50, choices=STYLE_CHOICES)
    comfort_importance = models.CharField(max_length=50, choices=COMFORT_CHOICES)
    price_range = models.CharField(max_length=50, choices=PRICE_CHOICES)
    favorite_brand = models.CharField(max_length=100, blank=True)
    additional_feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        if self.user:
            return f"Survey response from {self.user}"
        return f"Survey Response #{self.pk}"