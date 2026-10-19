from django.test import TestCase
from django.urls import reverse

from web.waitlist.models import ResearchAbuseMetric
from web.survey.models import SurveyResponse


class SurveyFlowTests(TestCase):
    steps = [
        (1, "visual_direction_preference", "relief_noir"),
        (2, "comfort_importance", "very_important"),
        (3, "price_range", "110_120"),
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

    def test_choice_steps_render_prompt_radio_cards_and_progress(self):
        prompts = (
            "Which Heritage Court direction would you be most likely to wear?",
            "How important is all-day comfort when you choose shoes?",
            "Based on the concept shown, what price range would feel reasonable for a pair?",
        )

        for number, prompt in enumerate(prompts, start=1):
            for prior_number, field_name, value in self.steps[: number - 1]:
                self.post_step(prior_number, field_name, value)
            response = self.client.get(
                reverse("survey:survey_question", args=[number])
            )
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, prompt)
            self.assertContains(response, 'type="radio"')
            self.assertContains(response, "survey-choice-card")
            self.assertContains(response, f"Step {number} of 5")
            self.assertContains(response, 'role="progressbar"')
            self.assertNotContains(response, "<select")

    def test_visual_direction_step_renders_six_approved_image_choices(self):
        response = self.client.get(reverse("survey:survey_question", args=[1]))

        self.assertContains(response, 'class="survey-choice-card survey-choice-card-visual"', count=6)
        self.assertContains(response, 'name="visual_direction_preference"', count=6)
        for value, label in SurveyResponse.VISUAL_DIRECTION_CHOICES:
            with self.subTest(value=value):
                self.assertContains(response, f'value="{value}"')
                self.assertContains(response, label)
        self.assertContains(response, "images/heritage-court/night-grid-960.webp")
        self.assertContains(response, "Pair of TreadJoy Heritage Court concept shoes")

    def test_optional_steps_show_optional_label_and_feedback_guidance(self):
        self.post_step(1, "visual_direction_preference", "relief_noir")
        self.post_step(2, "comfort_importance", "very_important")
        self.post_step(3, "price_range", "110_120")

        response = self.client.get(reverse("survey:survey_question", args=[4]))
        self.assertContains(response, "Is there a shoe or apparel brand you return to?")
        self.assertContains(response, "Your answer")
        self.assertContains(response, "Optional")

        self.post_step(4, "favorite_brand", "Favorite Brand")
        response = self.client.get(reverse("survey:survey_question", args=[5]))
        self.assertContains(response, "Anything else you want us to know?")
        self.assertContains(response, "Your feedback")
        self.assertContains(response, "Optional")
        self.assertContains(response, "Do not include names")

    def test_back_preserves_valid_answer_and_returns_to_previous_step(self):
        self.post_step(1, "visual_direction_preference", "relief_noir")
        self.post_step(2, "comfort_importance", "very_important")

        response = self.client.post(
            reverse("survey:survey_question", args=[3]),
            {"price_range": "110_120", "navigation": "back"},
        )
        self.assertRedirects(
            response,
            reverse("survey:survey_question", args=[2]),
        )
        response = self.client.get(reverse("survey:survey_question", args=[3]))
        self.assertContains(response, 'value="110_120"')

    def test_each_valid_step_redirects_to_next_and_keeps_session_draft(self):
        for number, field_name, value in self.steps[:-1]:
            response = self.post_step(number, field_name, value)
            self.assertRedirects(
                response,
                reverse("survey:survey_question", args=[number + 1]),
            )

        draft = self.client.session["survey_draft"]
        self.assertEqual(draft["response_version"], SurveyResponse.CURRENT_VERSION)
        self.assertEqual(
            draft["answers"]["visual_direction_preference"],
            "relief_noir",
        )
        self.assertEqual(draft["answers"]["favorite_brand"], "Favorite Brand")
        self.assertFalse(SurveyResponse.objects.exists())

    def test_invalid_choice_does_not_advance(self):
        response = self.post_step(
            1,
            "visual_direction_preference",
            "invented-choice",
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Select a valid choice")
        self.assertContains(response, "autofocus")
        self.assertContains(response, 'aria-invalid="true"')
        self.assertContains(response, 'id="id_visual_direction_preference_error"')
        self.assertContains(response, "Choose an answer")
        self.assertNotIn("survey_draft", self.client.session)

    def test_legacy_flat_session_draft_is_discarded_and_restarts_at_step_one(self):
        session = self.client.session
        session["survey_draft"] = {
            "style_preference": "athletic",
            "comfort_importance": "very_important",
        }
        session.save()

        response = self.client.get(reverse("survey:survey_question", args=[3]))

        self.assertRedirects(response, reverse("survey:survey_question", args=[1]))
        self.assertNotIn("survey_draft", self.client.session)

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
        self.assertFalse(hasattr(survey, "user"))
        self.assertFalse(hasattr(survey, "session_key"))
        self.assertEqual(survey.response_version, SurveyResponse.CURRENT_VERSION)
        self.assertEqual(survey.general_style_preference, "")
        self.assertEqual(survey.visual_direction_preference, "relief_noir")
        self.assertEqual(survey.comfort_importance, "very_important")
        self.assertEqual(survey.price_range, "110_120")
        self.assertEqual(survey.favorite_brand, "Favorite Brand")
        self.assertEqual(
            survey.additional_feedback,
            "More color choices, please.",
        )
        self.assertNotIn("survey_draft", self.client.session)

    def test_thank_you_links_home_and_waitlist(self):
        response = self.client.get(reverse("survey:survey_thank_you"))

        self.assertContains(response, reverse("core:home"))
        self.assertContains(response, reverse("waitlist:join_waitlist"))
        self.assertContains(response, "Join the Waitlist")

    def test_additional_feedback_is_capped_and_warns_against_personal_information(self):
        for number, field_name, value in self.steps[:-1]:
            self.post_step(number, field_name, value)
        response = self.post_step(5, "additional_feedback", "x" * 1001)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "at most 1000 characters")
        self.assertContains(response, "Do not include names")
        self.assertFalse(SurveyResponse.objects.exists())

    def test_second_completion_within_24_hours_is_rate_limited(self):
        self.complete_survey()
        response = self.post_step(1, "visual_direction_preference", "night_grid")
        self.assertEqual(response.status_code, 429)
        self.assertIn("Retry-After", response)

    def test_sixty_first_step_post_in_an_hour_is_rate_limited(self):
        url = reverse("survey:survey_question", args=[1])
        for _ in range(60):
            self.client.post(
                url,
                {"visual_direction_preference": "invented-choice"},
            )
        response = self.client.post(
            url,
            {"visual_direction_preference": "night_grid"},
        )
        self.assertEqual(response.status_code, 429)
        self.assertIn("Retry-After", response)

    def test_honeypot_writes_no_response_or_submitted_text(self):
        response = self.client.post(
            reverse("survey:survey_question", args=[1]),
            {
                "visual_direction_preference": "night_grid",
                "company_website": "secret bot text",
            },
        )
        self.assertRedirects(response, reverse("survey:survey_thank_you"))
        self.assertFalse(SurveyResponse.objects.exists())
        metric = ResearchAbuseMetric.objects.get(action="survey", kind="honeypot")
        self.assertEqual(metric.count, 1)
