from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from web.survey.models import SurveyResponse


class SurveyFlowTests(TestCase):
    steps = [
        (1, "style_preference", "athletic"),
        (2, "comfort_importance", "very_important"),
        (3, "price_range", "100_150"),
        (4, "favorite_brand", "Favorite Brand"),
        (5, "additional_feedback", "More color choices, please."),
    ]

    def post_step(self, number, field_name, value):
        return self.client.post(
            reverse("survey:survey_question", args=[number]),
            {field_name: value},
        )

    def complete_survey(self):
        responses = []
        for number, field_name, value in self.steps:
            responses.append(self.post_step(number, field_name, value))
        return responses

    def test_welcome_links_to_first_step(self):
        response = self.client.get(reverse("survey:survey_welcome"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            reverse("survey:survey_question", args=[1]),
        )

    def test_each_valid_step_redirects_to_next_and_keeps_session_draft(self):
        for number, field_name, value in self.steps[:-1]:
            response = self.post_step(number, field_name, value)
            self.assertRedirects(
                response,
                reverse("survey:survey_question", args=[number + 1]),
            )

        draft = self.client.session["survey_draft"]
        self.assertEqual(draft["style_preference"], "athletic")
        self.assertEqual(draft["favorite_brand"], "Favorite Brand")
        self.assertFalse(SurveyResponse.objects.exists())

    def test_invalid_choice_does_not_advance(self):
        response = self.post_step(1, "style_preference", "invented-choice")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Select a valid choice")
        self.assertNotIn("style_preference", self.client.session.get(
            "survey_draft", {}
        ))

    def test_skipping_a_required_prior_step_redirects_to_first_missing_step(self):
        response = self.client.get(
            reverse("survey:survey_question", args=[3])
        )

        self.assertRedirects(
            response,
            reverse("survey:survey_question", args=[1]),
        )

    def test_out_of_range_step_is_not_found(self):
        response = self.client.get(
            reverse("survey:survey_question", args=[6])
        )

        self.assertEqual(response.status_code, 404)

    def test_guest_completion_persists_once_and_clears_draft(self):
        responses = self.complete_survey()

        self.assertRedirects(responses[-1], reverse("survey:survey_thank_you"))
        self.assertEqual(SurveyResponse.objects.count(), 1)
        survey = SurveyResponse.objects.get()
        self.assertIsNone(survey.user)
        self.assertTrue(survey.session_key)
        self.assertEqual(survey.style_preference, "athletic")
        self.assertEqual(survey.comfort_importance, "very_important")
        self.assertEqual(survey.price_range, "100_150")
        self.assertEqual(survey.favorite_brand, "Favorite Brand")
        self.assertEqual(
            survey.additional_feedback,
            "More color choices, please.",
        )
        self.assertNotIn("survey_draft", self.client.session)

    def test_authenticated_completion_associates_response_with_user(self):
        user = get_user_model().objects.create_user(
            username="survey-user",
            email="survey@example.com",
            password="CorrectHorseBattery9!",
        )
        self.client.force_login(user)

        self.complete_survey()

        self.assertEqual(SurveyResponse.objects.get().user, user)

