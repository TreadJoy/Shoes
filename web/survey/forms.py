from django import forms

from .models import SurveyResponse


SURVEY_PROMPTS = {
    "style_preference": "Which style direction feels most like you?",
    "comfort_importance": "How important is all-day comfort when you choose shoes?",
    "price_range": "What price range feels right for a pair?",
    "favorite_brand": "Is there a shoe or apparel brand you return to?",
    "additional_feedback": "Anything else you want us to know?",
}


class SurveyStepForm(forms.Form):
    company_website = forms.CharField(
        required=False,
        label="Leave this field empty",
        widget=forms.HiddenInput(attrs={"tabindex": "-1", "autocomplete": "off", "aria-hidden": "true"}),
    )


class StylePreferenceForm(SurveyStepForm):
    style_preference = forms.ChoiceField(
        label=SURVEY_PROMPTS["style_preference"],
        choices=SurveyResponse.STYLE_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "survey-choice-input"}),
    )


class ComfortImportanceForm(SurveyStepForm):
    comfort_importance = forms.ChoiceField(
        label=SURVEY_PROMPTS["comfort_importance"],
        choices=SurveyResponse.COMFORT_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "survey-choice-input"}),
    )


class PriceRangeForm(SurveyStepForm):
    price_range = forms.ChoiceField(
        label=SURVEY_PROMPTS["price_range"],
        choices=SurveyResponse.PRICE_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "survey-choice-input"}),
    )


class FavoriteBrandForm(SurveyStepForm):
    favorite_brand = forms.CharField(
        label="Your answer",
        max_length=100,
        required=False,
    )


class AdditionalFeedbackForm(SurveyStepForm):
    additional_feedback = forms.CharField(
        label="Your feedback",
        max_length=1000,
        required=False,
        help_text="Up to 1,000 characters. Do not include names, contact details, or other personal information.",
        widget=forms.Textarea(attrs={"rows": 6}),
    )


SURVEY_STEPS = {
    1: ("style_preference", StylePreferenceForm),
    2: ("comfort_importance", ComfortImportanceForm),
    3: ("price_range", PriceRangeForm),
    4: ("favorite_brand", FavoriteBrandForm),
    5: ("additional_feedback", AdditionalFeedbackForm),
}
