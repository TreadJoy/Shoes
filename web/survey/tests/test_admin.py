from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import RequestFactory, TestCase

from web.survey.admin import SurveyResponseAdmin
from web.survey.models import SurveyExportEvent, SurveyResponse


class SurveyAdminContractTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="research-analyst-test",
            password="synthetic-test-password",
            is_staff=True,
        )
        self.model_admin = SurveyResponseAdmin(SurveyResponse, admin.site)
        self.factory = RequestFactory()

    def request_for(self, *, with_export_permission):
        if with_export_permission:
            self.user.user_permissions.add(
                Permission.objects.get(
                    content_type__app_label="survey",
                    codename="export_surveyresponse",
                )
            )
            self.user = get_user_model().objects.get(pk=self.user.pk)
        request = self.factory.get("/admin/survey/surveyresponse/")
        request.user = self.user
        return request

    def test_export_action_requires_the_dedicated_permission(self):
        request = self.request_for(with_export_permission=False)
        self.assertFalse(self.model_admin.has_export_permission(request))
        self.assertNotIn("export_anonymous_csv", self.model_admin.get_actions(request))

        request = self.request_for(with_export_permission=True)
        self.assertTrue(self.model_admin.has_export_permission(request))
        self.assertIn("export_anonymous_csv", self.model_admin.get_actions(request))

    def test_export_is_formula_safe_minimal_and_audited(self):
        response_record = SurveyResponse.objects.create(
            response_version=SurveyResponse.CURRENT_VERSION,
            visual_direction_preference="night_grid",
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
            favorite_brand="=HYPERLINK(\"https://example.invalid\")",
            additional_feedback="+SUM(1,1)",
        )
        legacy_record = SurveyResponse.objects.create(
            response_version=SurveyResponse.LEGACY_VERSION,
            general_style_preference="athletic",
            comfort_importance="somewhat_important",
            price_range="100_150",
        )
        request = self.request_for(with_export_permission=True)

        response = self.model_admin.export_anonymous_csv(
            request,
            SurveyResponse.objects.filter(pk__in=(response_record.pk, legacy_record.pk)),
        )

        payload = response.content.decode("utf-8")
        self.assertIn(
            "response_version,general_style_preference,visual_direction_preference,"
            "comfort_importance,price_range,recruitment_source,overall_appeal,"
            "modularity_value,wearing_occasion,purchase_likelihood,annual_purchases,"
            "age_band,gender",
            payload,
        )
        self.assertIn(
            "3,,night_grid,very_important,100_125,direct,very_appealing,"
            "very_interesting,everyday_casual,probably_would,3_5,25_30,"
            "prefer_not_to_say",
            payload,
        )
        self.assertIn("1,athletic,,somewhat_important,100_150", payload)
        self.assertIn("'=HYPERLINK", payload)
        self.assertIn("'+SUM", payload)
        self.assertNotIn("session", payload.casefold())
        self.assertNotIn("email", payload.casefold())
        self.assertNotIn("provider", payload.casefold())
        self.assertEqual(response["Cache-Control"], "no-store")
        audit = SurveyExportEvent.objects.get()
        self.assertEqual(audit.actor, self.user)
        self.assertEqual(audit.row_count, 2)
        self.assertEqual(len(audit.file_sha256), 64)

    def test_survey_admin_is_read_only_and_does_not_list_free_text(self):
        request = self.request_for(with_export_permission=True)
        self.assertFalse(self.model_admin.has_add_permission(request))
        self.assertFalse(self.model_admin.has_change_permission(request))
        self.assertFalse(self.model_admin.has_delete_permission(request))
        self.assertNotIn("additional_feedback", self.model_admin.list_display)
        self.assertEqual(self.model_admin.search_fields, ())
