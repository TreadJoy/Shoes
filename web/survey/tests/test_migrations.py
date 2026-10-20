from importlib import import_module

from django.apps import apps as global_apps
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase

from web.survey.models import SurveyResponse


class SurveyV2MigrationTests(TransactionTestCase):
    migrate_from = ("survey", "0004_alter_surveyresponse_options_and_more")
    migrate_to = ("survey", "0005_version_visual_direction_responses")

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
        super().tearDown()

    def test_legacy_response_is_versioned_without_reinterpretation(self):
        executor = MigrationExecutor(connection)
        executor.migrate([self.migrate_from])
        old_apps = executor.loader.project_state([self.migrate_from]).apps
        OldSurveyResponse = old_apps.get_model("survey", "SurveyResponse")
        legacy = OldSurveyResponse.objects.create(
            style_preference="streetwear",
            comfort_importance="very_important",
            price_range="100_150",
        )

        executor = MigrationExecutor(connection)
        executor.migrate([self.migrate_to])
        new_apps = executor.loader.project_state([self.migrate_to]).apps
        NewSurveyResponse = new_apps.get_model("survey", "SurveyResponse")
        migrated = NewSurveyResponse.objects.get(pk=legacy.pk)

        self.assertEqual(migrated.response_version, 1)
        self.assertEqual(migrated.general_style_preference, "streetwear")
        self.assertEqual(migrated.visual_direction_preference, "")
        self.assertEqual(migrated.price_range, "100_150")

    def test_reverse_guard_refuses_to_discard_current_responses(self):
        SurveyResponse.objects.create(
            response_version=SurveyResponse.V2_VERSION,
            visual_direction_preference="relief_contour",
            comfort_importance="very_important",
            price_range="110_120",
        )
        migration = import_module(
            "web.survey.migrations.0005_version_visual_direction_responses"
        )

        with self.assertRaisesRegex(RuntimeError, "cannot be reversed"):
            migration.refuse_reverse_with_v2_responses(global_apps, None)


class SurveyV3MigrationTests(TransactionTestCase):
    migrate_from = ("survey", "0005_version_visual_direction_responses")
    migrate_to = ("survey", "0006_add_v3_survey_responses")

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
        super().tearDown()

    def test_existing_v2_response_is_preserved_and_v3_fields_start_blank(self):
        executor = MigrationExecutor(connection)
        executor.migrate([self.migrate_from])
        old_apps = executor.loader.project_state([self.migrate_from]).apps
        OldSurveyResponse = old_apps.get_model("survey", "SurveyResponse")
        original = OldSurveyResponse.objects.create(
            response_version=2,
            general_style_preference="",
            visual_direction_preference="forest_noir",
            comfort_importance="very_important",
            price_range="110_120",
            favorite_brand="Existing brand",
            additional_feedback="Existing feedback",
        )

        executor = MigrationExecutor(connection)
        executor.migrate([self.migrate_to])
        new_apps = executor.loader.project_state([self.migrate_to]).apps
        NewSurveyResponse = new_apps.get_model("survey", "SurveyResponse")
        migrated = NewSurveyResponse.objects.get(pk=original.pk)

        self.assertEqual(migrated.response_version, 2)
        self.assertEqual(migrated.visual_direction_preference, "forest_noir")
        self.assertEqual(migrated.price_range, "110_120")
        self.assertEqual(migrated.favorite_brand, "Existing brand")
        self.assertEqual(migrated.additional_feedback, "Existing feedback")
        for field_name in (
            "recruitment_source",
            "overall_appeal",
            "modularity_value",
            "wearing_occasion",
            "purchase_likelihood",
            "annual_purchases",
            "age_band",
            "gender",
        ):
            with self.subTest(field=field_name):
                self.assertEqual(getattr(migrated, field_name), "")

    def test_reverse_guard_refuses_to_discard_v3_responses(self):
        SurveyResponse.objects.create(
            response_version=SurveyResponse.V3_RESPONSE_VERSION,
            visual_direction_preference="forest_noir",
            comfort_importance="very_important",
            price_range="100_125",
            recruitment_source="direct",
            overall_appeal="very_appealing",
            modularity_value="very_interesting",
            wearing_occasion="everyday_casual",
            purchase_likelihood="probably_would",
            annual_purchases="3_5",
            age_band="25_30",
            gender="prefer_not_to_say",
        )
        migration = import_module(
            "web.survey.migrations.0006_add_v3_survey_responses"
        )

        with self.assertRaisesRegex(RuntimeError, "cannot be reversed"):
            migration.refuse_reverse_with_v3_responses(global_apps, None)
