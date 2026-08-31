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
            style_preference="athletic",
            comfort_importance="very_important",
            price_range="100_150",
            favorite_brand="=HYPERLINK(\"https://example.invalid\")",
            additional_feedback="+SUM(1,1)",
        )
        request = self.request_for(with_export_permission=True)

        response = self.model_admin.export_anonymous_csv(
            request,
            SurveyResponse.objects.filter(pk=response_record.pk),
        )

        payload = response.content.decode("utf-8")
        self.assertIn("'=HYPERLINK", payload)
        self.assertIn("'+SUM", payload)
        self.assertNotIn("session", payload.casefold())
        self.assertNotIn("email", payload.casefold())
        self.assertNotIn("provider", payload.casefold())
        self.assertEqual(response["Cache-Control"], "no-store")
        audit = SurveyExportEvent.objects.get()
        self.assertEqual(audit.actor, self.user)
        self.assertEqual(audit.row_count, 1)
        self.assertEqual(len(audit.file_sha256), 64)

    def test_survey_admin_is_read_only_and_does_not_list_free_text(self):
        request = self.request_for(with_export_permission=True)
        self.assertFalse(self.model_admin.has_add_permission(request))
        self.assertFalse(self.model_admin.has_change_permission(request))
        self.assertFalse(self.model_admin.has_delete_permission(request))
        self.assertNotIn("additional_feedback", self.model_admin.list_display)
        self.assertEqual(self.model_admin.search_fields, ())
