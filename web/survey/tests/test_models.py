from django.db import IntegrityError, transaction
from django.test import TestCase

from web.survey.models import SurveyResponse


class SurveyResponseVersionContractTests(TestCase):
    def test_legacy_and_current_payloads_remain_distinct(self):
        legacy = SurveyResponse.objects.create(
            response_version=SurveyResponse.LEGACY_VERSION,
            general_style_preference="streetwear",
            comfort_importance="very_important",
            price_range="100_150",
        )
        current = SurveyResponse.objects.create(
            response_version=SurveyResponse.CURRENT_VERSION,
            visual_direction_preference="forest_noir",
            comfort_importance="very_important",
            price_range="110_120",
        )

        self.assertEqual(legacy.general_style_preference, "streetwear")
        self.assertEqual(legacy.visual_direction_preference, "")
        self.assertEqual(current.general_style_preference, "")
        self.assertEqual(current.visual_direction_preference, "forest_noir")

    def test_current_response_rejects_legacy_preference_or_price(self):
        invalid_payloads = (
            {
                "response_version": SurveyResponse.CURRENT_VERSION,
                "general_style_preference": "athletic",
                "visual_direction_preference": "",
                "price_range": "110_120",
            },
            {
                "response_version": SurveyResponse.CURRENT_VERSION,
                "general_style_preference": "",
                "visual_direction_preference": "night_grid",
                "price_range": "100_150",
            },
        )
        for payload in invalid_payloads:
            with self.subTest(payload=payload), self.assertRaises(IntegrityError):
                with transaction.atomic():
                    SurveyResponse.objects.create(
                        comfort_importance="very_important",
                        **payload,
                    )

    def test_legacy_response_rejects_current_preference_or_price(self):
        invalid_payloads = (
            {
                "response_version": SurveyResponse.LEGACY_VERSION,
                "general_style_preference": "",
                "visual_direction_preference": "night_grid",
                "price_range": "100_150",
            },
            {
                "response_version": SurveyResponse.LEGACY_VERSION,
                "general_style_preference": "athletic",
                "visual_direction_preference": "",
                "price_range": "110_120",
            },
        )
        for payload in invalid_payloads:
            with self.subTest(payload=payload), self.assertRaises(IntegrityError):
                with transaction.atomic():
                    SurveyResponse.objects.create(
                        comfort_importance="very_important",
                        **payload,
                    )
