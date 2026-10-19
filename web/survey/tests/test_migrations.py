from importlib import import_module

from django.apps import apps as global_apps
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase

from web.survey.models import SurveyResponse


class SurveyV2MigrationTests(TransactionTestCase):
    migrate_from = ("survey", "0004_alter_surveyresponse_options_and_more")
    migrate_to = ("survey", "0005_version_visual_direction_responses")

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
            response_version=SurveyResponse.CURRENT_VERSION,
            visual_direction_preference="relief_contour",
            comfort_importance="very_important",
            price_range="100_109",
        )
        migration = import_module(
            "web.survey.migrations.0005_version_visual_direction_responses"
        )

        with self.assertRaisesRegex(RuntimeError, "cannot be reversed"):
            migration.refuse_reverse_with_v2_responses(global_apps, None)
