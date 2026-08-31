from django import forms

from .models import SurveyResponse


class SurveyStepForm(forms.Form):
    company_website = forms.CharField(
        required=False,
        label="Leave this field empty",
        widget=forms.HiddenInput(attrs={"tabindex": "-1", "autocomplete": "off", "aria-hidden": "true"}),
    )


class StylePreferenceForm(SurveyStepForm):
    style_preference = forms.ChoiceField(label="Style preference", choices=SurveyResponse.STYLE_CHOICES)


class ComfortImportanceForm(SurveyStepForm):
    comfort_importance = forms.ChoiceField(label="Comfort importance", choices=SurveyResponse.COMFORT_CHOICES)


class PriceRangeForm(SurveyStepForm):
    price_range = forms.ChoiceField(label="Price range", choices=SurveyResponse.PRICE_CHOICES)


class FavoriteBrandForm(SurveyStepForm):
    favorite_brand = forms.CharField(label="Favorite brand", max_length=100, required=False)


class AdditionalFeedbackForm(SurveyStepForm):
    additional_feedback = forms.CharField(
        label="Additional feedback",
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
