from django import forms

from .models import SurveyResponse


class StylePreferenceForm(forms.Form):
    style_preference = forms.ChoiceField(
        label="Style preference",
        choices=SurveyResponse.STYLE_CHOICES,
    )


class ComfortImportanceForm(forms.Form):
    comfort_importance = forms.ChoiceField(
        label="Comfort importance",
        choices=SurveyResponse.COMFORT_CHOICES,
    )


class PriceRangeForm(forms.Form):
    price_range = forms.ChoiceField(
        label="Price range",
        choices=SurveyResponse.PRICE_CHOICES,
    )


class FavoriteBrandForm(forms.Form):
    favorite_brand = forms.CharField(
        label="Favorite brand",
        max_length=SurveyResponse._meta.get_field("favorite_brand").max_length,
        required=False,
    )


class AdditionalFeedbackForm(forms.Form):
    additional_feedback = forms.CharField(
        label="Additional feedback",
        required=False,
        widget=forms.Textarea,
    )


SURVEY_STEPS = {
    1: ("style_preference", StylePreferenceForm),
    2: ("comfort_importance", ComfortImportanceForm),
    3: ("price_range", PriceRangeForm),
    4: ("favorite_brand", FavoriteBrandForm),
    5: ("additional_feedback", AdditionalFeedbackForm),
}

