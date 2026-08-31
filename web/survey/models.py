from django.conf import settings
from django.db import models


class SurveyResponse(models.Model):
    STYLE_CHOICES = [("athletic", "Athletic"), ("casual", "Casual"), ("streetwear", "Streetwear"), ("formal", "Formal"), ("outdoor", "Outdoor")]
    COMFORT_CHOICES = [("very_important", "Very Important"), ("somewhat_important", "Somewhat Important"), ("neutral", "Neutral"), ("not_important", "Not Important")]
    PRICE_CHOICES = [("under_50", "Under $50"), ("50_100", "$50 - $100"), ("100_150", "$100 - $150"), ("150_plus", "$150+")]

    style_preference = models.CharField(max_length=50, choices=STYLE_CHOICES)
    comfort_importance = models.CharField(max_length=50, choices=COMFORT_CHOICES)
    price_range = models.CharField(max_length=50, choices=PRICE_CHOICES)
    favorite_brand = models.CharField(max_length=100, blank=True)
    additional_feedback = models.TextField(blank=True, max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = [("export_surveyresponse", "Can export anonymous survey responses")]

    def __str__(self):
        return f"Anonymous survey response from {self.created_at:%Y-%m-%d}"


class SurveyExportEvent(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="survey_export_events")
    purpose = models.CharField(max_length=50, default="product_research_analysis")
    row_count = models.PositiveIntegerField()
    file_sha256 = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
