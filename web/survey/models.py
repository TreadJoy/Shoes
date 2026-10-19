from django.conf import settings
from django.db import models


LEGACY_RESPONSE_VERSION = 1
CURRENT_RESPONSE_VERSION = 2

LEGACY_STYLE_CHOICES = (
    ("athletic", "Athletic"),
    ("casual", "Casual"),
    ("streetwear", "Streetwear"),
    ("formal", "Formal"),
    ("outdoor", "Outdoor"),
)

VISUAL_DIRECTION_CHOICES = (
    ("night_grid", "Night Grid"),
    ("relief_contour", "Relief Contour"),
    ("evergreen_route", "Evergreen Route"),
    ("relief_noir", "Relief / Noir"),
    ("forest_noir", "Forest / Noir"),
    ("relief_joyfront", "Relief Joyfront"),
)

COMFORT_CHOICES = (
    ("very_important", "Very Important"),
    ("somewhat_important", "Somewhat Important"),
    ("neutral", "Neutral"),
    ("not_important", "Not Important"),
)

LEGACY_PRICE_CHOICES = (
    ("under_50", "Legacy: Under $50"),
    ("50_100", "Legacy: $50–$100"),
    ("100_150", "Legacy: $100–$150"),
    ("150_plus", "Legacy: $150+"),
)

CURRENT_PRICE_CHOICES = (
    ("under_90", "Under $90"),
    ("90_99", "$90–$99"),
    ("100_109", "$100–$109"),
    ("110_120", "$110–$120"),
    ("121_150", "$121–$150"),
    ("over_150", "Over $150"),
)


class SurveyResponse(models.Model):
    LEGACY_VERSION = LEGACY_RESPONSE_VERSION
    CURRENT_VERSION = CURRENT_RESPONSE_VERSION
    LEGACY_STYLE_CHOICES = LEGACY_STYLE_CHOICES
    VISUAL_DIRECTION_CHOICES = VISUAL_DIRECTION_CHOICES
    COMFORT_CHOICES = COMFORT_CHOICES
    LEGACY_PRICE_CHOICES = LEGACY_PRICE_CHOICES
    CURRENT_PRICE_CHOICES = CURRENT_PRICE_CHOICES
    PRICE_CHOICES = LEGACY_PRICE_CHOICES + CURRENT_PRICE_CHOICES

    response_version = models.PositiveSmallIntegerField(
        default=CURRENT_RESPONSE_VERSION,
        choices=(
            (LEGACY_RESPONSE_VERSION, "Legacy general-style survey"),
            (CURRENT_RESPONSE_VERSION, "Heritage Court visual-direction survey"),
        ),
        db_comment="Identifies the question and choice set used for this anonymous response.",
    )
    general_style_preference = models.CharField(
        max_length=50,
        choices=LEGACY_STYLE_CHOICES,
        blank=True,
        default="",
        db_comment="Legacy V1 broad footwear style choice; blank for V2 responses.",
    )
    visual_direction_preference = models.CharField(
        max_length=50,
        choices=VISUAL_DIRECTION_CHOICES,
        blank=True,
        default="",
        db_comment="V2 Heritage Court visual direction; blank for legacy responses.",
    )
    comfort_importance = models.CharField(max_length=50, choices=COMFORT_CHOICES)
    price_range = models.CharField(
        max_length=50,
        choices=PRICE_CHOICES,
        db_comment="Price choice interpreted according to response_version.",
    )
    favorite_brand = models.CharField(max_length=100, blank=True)
    additional_feedback = models.TextField(blank=True, max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = [("export_surveyresponse", "Can export anonymous survey responses")]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(
                        response_version=LEGACY_RESPONSE_VERSION,
                        general_style_preference__in=[
                            value for value, _label in LEGACY_STYLE_CHOICES
                        ],
                        visual_direction_preference="",
                    )
                    | models.Q(
                        response_version=CURRENT_RESPONSE_VERSION,
                        general_style_preference="",
                        visual_direction_preference__in=[
                            value for value, _label in VISUAL_DIRECTION_CHOICES
                        ],
                    )
                ),
                name="survey_response_versioned_preference_valid",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        response_version=LEGACY_RESPONSE_VERSION,
                        price_range__in=[
                            value for value, _label in LEGACY_PRICE_CHOICES
                        ],
                    )
                    | models.Q(
                        response_version=CURRENT_RESPONSE_VERSION,
                        price_range__in=[
                            value for value, _label in CURRENT_PRICE_CHOICES
                        ],
                    )
                ),
                name="survey_response_versioned_price_valid",
            ),
        ]

    def __str__(self):
        return f"Anonymous survey response from {self.created_at:%Y-%m-%d}"


class SurveyExportEvent(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="survey_export_events")
    purpose = models.CharField(max_length=50, default="product_research_analysis")
    row_count = models.PositiveIntegerField()
    file_sha256 = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
