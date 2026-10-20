from django.conf import settings
from django.db import models


LEGACY_RESPONSE_VERSION = 1
V2_RESPONSE_VERSION = 2
V3_RESPONSE_VERSION = 3
CURRENT_RESPONSE_VERSION = V3_RESPONSE_VERSION

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

V2_PRICE_CHOICES = (
    ("under_90", "Under $90"),
    ("90_99", "$90–$99"),
    ("100_109", "$100–$109"),
    ("110_120", "$110–$120"),
    ("121_150", "$121–$150"),
    ("over_150", "Over $150"),
)

V3_PRICE_CHOICES = (
    ("under_60", "Under $60"),
    ("60_80", "$60–$80"),
    ("80_100", "$80–$100"),
    ("100_125", "$100–$125"),
    ("125_plus", "$125+"),
)

RECRUITMENT_SOURCE_CHOICES = (
    ("direct", "Direct"),
    ("social_media", "Social Media"),
    ("other", "Other"),
)

APPEAL_CHOICES = (
    ("very_appealing", "Very Appealing"),
    ("somewhat_appealing", "Somewhat Appealing"),
    ("neutral", "Neutral"),
    ("somewhat_unappealing", "Somewhat Unappealing"),
    ("very_unappealing", "Very Unappealing"),
)

MODULARITY_VALUE_CHOICES = (
    ("very_interesting", "Very Interesting"),
    ("somewhat_interesting", "Somewhat Interesting"),
    ("neutral", "Neutral"),
    ("somewhat_uninteresting", "Somewhat Uninteresting"),
    ("very_uninteresting", "Very Uninteresting"),
)

WEARING_OCCASION_CHOICES = (
    ("everyday_casual", "Everyday Casual"),
    ("public_events", "Public Events"),
    ("outfit_coordination", "Outfit Coordination"),
    ("never", "Never"),
    ("other", "Other"),
)

PURCHASE_LIKELIHOOD_CHOICES = (
    ("definitely_would", "Definitely Would"),
    ("probably_would", "Probably Would"),
    ("might_or_might_not", "Might or Might Not"),
    ("probably_would_not", "Probably Would Not"),
    ("definitely_would_not", "Definitely Would Not"),
)

SHOE_PURCHASE_FREQUENCY_CHOICES = (
    ("1_2", "1–2 pairs"),
    ("3_5", "3–5 pairs"),
    ("5_plus", "5+ pairs"),
    ("rarely", "Rarely"),
)

AGE_BAND_CHOICES = (
    ("18_24", "18–24"),
    ("25_30", "25–30"),
    ("31_40", "31–40"),
    ("41_50", "41–50"),
    ("51_plus", "51+"),
)

GENDER_CHOICES = (
    ("male", "Male"),
    ("female", "Female"),
    ("non_binary", "Non-binary"),
    ("prefer_not_to_say", "Prefer not to say"),
)

V3_FIELD_CHOICES = (
    ("recruitment_source", RECRUITMENT_SOURCE_CHOICES),
    ("overall_appeal", APPEAL_CHOICES),
    ("modularity_value", MODULARITY_VALUE_CHOICES),
    ("wearing_occasion", WEARING_OCCASION_CHOICES),
    ("purchase_likelihood", PURCHASE_LIKELIHOOD_CHOICES),
    ("annual_purchases", SHOE_PURCHASE_FREQUENCY_CHOICES),
    ("age_band", AGE_BAND_CHOICES),
    ("gender", GENDER_CHOICES),
)


class SurveyResponse(models.Model):
    LEGACY_VERSION = LEGACY_RESPONSE_VERSION
    V2_VERSION = V2_RESPONSE_VERSION
    V3_RESPONSE_VERSION = V3_RESPONSE_VERSION
    CURRENT_VERSION = CURRENT_RESPONSE_VERSION
    LEGACY_STYLE_CHOICES = LEGACY_STYLE_CHOICES
    VISUAL_DIRECTION_CHOICES = VISUAL_DIRECTION_CHOICES
    COMFORT_CHOICES = COMFORT_CHOICES
    LEGACY_PRICE_CHOICES = LEGACY_PRICE_CHOICES
    V2_PRICE_CHOICES = V2_PRICE_CHOICES
    V3_PRICE_CHOICES = V3_PRICE_CHOICES
    CURRENT_PRICE_CHOICES = V3_PRICE_CHOICES
    RECRUITMENT_SOURCE_CHOICES = RECRUITMENT_SOURCE_CHOICES
    APPEAL_CHOICES = APPEAL_CHOICES
    MODULARITY_VALUE_CHOICES = MODULARITY_VALUE_CHOICES
    WEARING_OCCASION_CHOICES = WEARING_OCCASION_CHOICES
    PURCHASE_LIKELIHOOD_CHOICES = PURCHASE_LIKELIHOOD_CHOICES
    SHOE_PURCHASE_FREQUENCY_CHOICES = SHOE_PURCHASE_FREQUENCY_CHOICES
    AGE_BAND_CHOICES = AGE_BAND_CHOICES
    GENDER_CHOICES = GENDER_CHOICES

    response_version = models.PositiveSmallIntegerField(
        default=CURRENT_RESPONSE_VERSION,
        choices=(
            (LEGACY_RESPONSE_VERSION, "Legacy general-style survey"),
            (V2_RESPONSE_VERSION, "Heritage Court visual-direction survey"),
            (V3_RESPONSE_VERSION, "V3 research survey"),
        ),
        db_comment="Identifies the question and choice set used for this anonymous response.",
    )
    general_style_preference = models.CharField(
        max_length=50,
        choices=LEGACY_STYLE_CHOICES,
        blank=True,
        default="",
        db_comment="Legacy V1 broad footwear style choice; blank for V2 and V3 responses.",
    )
    visual_direction_preference = models.CharField(
        max_length=50,
        choices=VISUAL_DIRECTION_CHOICES,
        blank=True,
        default="",
        db_comment="V2/V3 Heritage Court visual direction; blank for V1 responses.",
    )
    comfort_importance = models.CharField(max_length=50, choices=COMFORT_CHOICES)
    price_range = models.CharField(
        max_length=50,
        choices=LEGACY_PRICE_CHOICES + V2_PRICE_CHOICES + V3_PRICE_CHOICES,
        db_comment="Price choice interpreted according to response_version.",
    )
    recruitment_source = models.CharField(
        max_length=50, choices=RECRUITMENT_SOURCE_CHOICES, blank=True, default=""
    )
    overall_appeal = models.CharField(
        max_length=50, choices=APPEAL_CHOICES, blank=True, default=""
    )
    modularity_value = models.CharField(
        max_length=50, choices=MODULARITY_VALUE_CHOICES, blank=True, default=""
    )
    wearing_occasion = models.CharField(
        max_length=50, choices=WEARING_OCCASION_CHOICES, blank=True, default=""
    )
    purchase_likelihood = models.CharField(
        max_length=50, choices=PURCHASE_LIKELIHOOD_CHOICES, blank=True, default=""
    )
    annual_purchases = models.CharField(
        max_length=50,
        choices=SHOE_PURCHASE_FREQUENCY_CHOICES,
        blank=True,
        default="",
    )
    age_band = models.CharField(
        max_length=50,
        choices=AGE_BAND_CHOICES,
        blank=True,
        default="",
        db_comment="V3 age-band response; not a customer account profile field.",
    )
    gender = models.CharField(
        max_length=50,
        choices=GENDER_CHOICES,
        blank=True,
        default="",
        db_comment="V3 gender response; not a customer account profile field.",
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
                        response_version__in=[
                            V2_RESPONSE_VERSION,
                            V3_RESPONSE_VERSION,
                        ],
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
                        response_version=V2_RESPONSE_VERSION,
                        price_range__in=[
                            value for value, _label in V2_PRICE_CHOICES
                        ],
                    )
                    | models.Q(
                        response_version=V3_RESPONSE_VERSION,
                        price_range__in=[
                            value for value, _label in V3_PRICE_CHOICES
                        ],
                    )
                ),
                name="survey_response_versioned_price_valid",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(response_version=V3_RESPONSE_VERSION)
                    & models.Q(**{
                        f"{field_name}__in": [
                            value for value, _label in choices
                        ]
                        for field_name, choices in V3_FIELD_CHOICES
                    })
                )
                | (
                    models.Q(
                        response_version__in=[
                            LEGACY_RESPONSE_VERSION,
                            V2_RESPONSE_VERSION,
                        ]
                    )
                    & models.Q(**{
                        field_name: ""
                        for field_name, _choices in V3_FIELD_CHOICES
                    })
                ),
                name="survey_response_v3_fields_valid",
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
