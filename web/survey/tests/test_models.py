from django.db import IntegrityError, transaction
from django.test import TestCase

from web.survey.models import SurveyResponse


class SurveyResponseVersionContractTests(TestCase):
    def _valid_v3_payload(self):
        return {
            "response_version": SurveyResponse.V3_RESPONSE_VERSION,
            "general_style_preference": "",
            "visual_direction_preference": "forest_noir",
            "comfort_importance": "very_important",
            "price_range": "100_125",
            "recruitment_source": "direct",
            "overall_appeal": "very_appealing",
            "modularity_value": "very_interesting",
            "wearing_occasion": "everyday_casual",
            "purchase_likelihood": "probably_would",
            "annual_purchases": "3_5",
            "age_band": "25_30",
            "gender": "prefer_not_to_say",
            "favorite_brand": "",
            "additional_feedback": "This is a test comment.",
        }

    def test_legacy_v2_and_v3_payloads_remain_distinct(self):
        legacy = SurveyResponse.objects.create(
            response_version=SurveyResponse.LEGACY_VERSION,
            general_style_preference="streetwear",
            comfort_importance="very_important",
            price_range="100_150",
        )
        v2 = SurveyResponse.objects.create(
            response_version=SurveyResponse.V2_VERSION,
            visual_direction_preference="relief_noir",
            comfort_importance="very_important",
            price_range="110_120",
        )
        v3 = SurveyResponse.objects.create(**self._valid_v3_payload())

        self.assertEqual(legacy.general_style_preference, "streetwear")
        self.assertEqual(legacy.visual_direction_preference, "")
        self.assertEqual(v2.general_style_preference, "")
        self.assertEqual(v2.visual_direction_preference, "relief_noir")
        self.assertEqual(v3.response_version, SurveyResponse.CURRENT_VERSION)
        self.assertEqual(v3.visual_direction_preference, "forest_noir")
        self.assertEqual(v3.annual_purchases, "3_5")
        self.assertEqual(v3.age_band, "25_30")
        self.assertEqual(v3.gender, "prefer_not_to_say")

    def test_v3_rejects_legacy_preference_or_price_values(self):
        invalid_payloads = (
            {
                **self._valid_v3_payload(),
                "general_style_preference": "athletic",
            },
            {
                **self._valid_v3_payload(),
                "price_range": "100_150",
            },
        )

        for payload in invalid_payloads:
            with self.subTest(payload=payload), self.assertRaises(IntegrityError):
                with transaction.atomic():
                    SurveyResponse.objects.create(**payload)

    def test_v3_rejects_values_that_are_not_stored_choice_values(self):
        invalid_payloads = (
            {**self._valid_v3_payload(), "modularity_value": "Very Interesting"},
            {**self._valid_v3_payload(), "annual_purchases": "2-5"},
            {**self._valid_v3_payload(), "age_band": "25-30"},
        )

        for payload in invalid_payloads:
            with self.subTest(payload=payload), self.assertRaises(IntegrityError):
                with transaction.atomic():
                    SurveyResponse.objects.create(**payload)

    def test_historical_responses_reject_v3_fields(self):
        for version, style, visual, price in (
            (SurveyResponse.LEGACY_VERSION, "athletic", "", "100_150"),
            (SurveyResponse.V2_VERSION, "", "night_grid", "110_120"),
        ):
            payload = {
                "response_version": version,
                "general_style_preference": style,
                "visual_direction_preference": visual,
                "comfort_importance": "very_important",
                "price_range": price,
                "overall_appeal": "very_appealing",
            }
            with self.subTest(version=version), self.assertRaises(IntegrityError):
                with transaction.atomic():
                    SurveyResponse.objects.create(**payload)
