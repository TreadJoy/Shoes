from django.db import migrations, models


LEGACY_STYLE_VALUES = ("athletic", "casual", "streetwear", "formal", "outdoor")
VISUAL_DIRECTION_VALUES = (
    "night_grid",
    "relief_contour",
    "evergreen_route",
    "relief_noir",
    "forest_noir",
    "relief_joyfront",
)
LEGACY_PRICE_VALUES = ("under_50", "50_100", "100_150", "150_plus")
CURRENT_PRICE_VALUES = (
    "under_90",
    "90_99",
    "100_109",
    "110_120",
    "121_150",
    "over_150",
)


def validate_legacy_responses(apps, schema_editor):
    SurveyResponse = apps.get_model("survey", "SurveyResponse")
    invalid_style_count = SurveyResponse.objects.exclude(
        general_style_preference__in=LEGACY_STYLE_VALUES
    ).count()
    invalid_price_count = SurveyResponse.objects.exclude(
        price_range__in=LEGACY_PRICE_VALUES
    ).count()
    if invalid_style_count or invalid_price_count:
        raise RuntimeError(
            "Survey V2 migration stopped: existing responses contain "
            f"{invalid_style_count} unknown style value(s) and "
            f"{invalid_price_count} unknown price value(s)."
        )


def refuse_reverse_with_v2_responses(apps, schema_editor):
    SurveyResponse = apps.get_model("survey", "SurveyResponse")
    if SurveyResponse.objects.filter(response_version=2).exists():
        raise RuntimeError(
            "Survey V2 migration cannot be reversed while V2 responses exist; "
            "use a forward fix so visual-direction data is not discarded."
        )


class Migration(migrations.Migration):
    dependencies = [
        ("survey", "0004_alter_surveyresponse_options_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="surveyresponse",
            old_name="style_preference",
            new_name="general_style_preference",
        ),
        migrations.AlterField(
            model_name="surveyresponse",
            name="general_style_preference",
            field=models.CharField(
                blank=True,
                choices=[
                    ("athletic", "Athletic"),
                    ("casual", "Casual"),
                    ("streetwear", "Streetwear"),
                    ("formal", "Formal"),
                    ("outdoor", "Outdoor"),
                ],
                db_comment="Legacy V1 broad footwear style choice; blank for V2 responses.",
                default="",
                max_length=50,
            ),
        ),
        migrations.AddField(
            model_name="surveyresponse",
            name="visual_direction_preference",
            field=models.CharField(
                blank=True,
                choices=[
                    ("night_grid", "Night Grid"),
                    ("relief_contour", "Relief Contour"),
                    ("evergreen_route", "Evergreen Route"),
                    ("relief_noir", "Relief / Noir"),
                    ("forest_noir", "Forest / Noir"),
                    ("relief_joyfront", "Relief Joyfront"),
                ],
                db_comment="V2 Heritage Court visual direction; blank for legacy responses.",
                default="",
                max_length=50,
            ),
        ),
        migrations.AddField(
            model_name="surveyresponse",
            name="response_version",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (1, "Legacy general-style survey"),
                    (2, "Heritage Court visual-direction survey"),
                ],
                db_comment="Identifies the question and choice set used for this anonymous response.",
                default=1,
            ),
        ),
        migrations.RunPython(
            validate_legacy_responses,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="surveyresponse",
            name="response_version",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (1, "Legacy general-style survey"),
                    (2, "Heritage Court visual-direction survey"),
                ],
                db_comment="Identifies the question and choice set used for this anonymous response.",
                default=2,
            ),
        ),
        migrations.AlterField(
            model_name="surveyresponse",
            name="price_range",
            field=models.CharField(
                choices=[
                    ("under_50", "Legacy: Under $50"),
                    ("50_100", "Legacy: $50–$100"),
                    ("100_150", "Legacy: $100–$150"),
                    ("150_plus", "Legacy: $150+"),
                    ("under_90", "Under $90"),
                    ("90_99", "$90–$99"),
                    ("100_109", "$100–$109"),
                    ("110_120", "$110–$120"),
                    ("121_150", "$121–$150"),
                    ("over_150", "Over $150"),
                ],
                db_comment="Price choice interpreted according to response_version.",
                max_length=50,
            ),
        ),
        migrations.AddConstraint(
            model_name="surveyresponse",
            constraint=models.CheckConstraint(
                condition=(
                    models.Q(
                        response_version=1,
                        general_style_preference__in=LEGACY_STYLE_VALUES,
                        visual_direction_preference="",
                    )
                    | models.Q(
                        response_version=2,
                        general_style_preference="",
                        visual_direction_preference__in=VISUAL_DIRECTION_VALUES,
                    )
                ),
                name="survey_response_versioned_preference_valid",
            ),
        ),
        migrations.AddConstraint(
            model_name="surveyresponse",
            constraint=models.CheckConstraint(
                condition=(
                    models.Q(
                        response_version=1,
                        price_range__in=LEGACY_PRICE_VALUES,
                    )
                    | models.Q(
                        response_version=2,
                        price_range__in=CURRENT_PRICE_VALUES,
                    )
                ),
                name="survey_response_versioned_price_valid",
            ),
        ),
        migrations.RunPython(
            migrations.RunPython.noop,
            refuse_reverse_with_v2_responses,
        ),
    ]
