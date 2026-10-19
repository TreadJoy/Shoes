from django import forms

from .models import SurveyResponse


SURVEY_PROMPTS = {
    "visual_direction_preference": "Which Heritage Court direction would you be most likely to wear?",
    "comfort_importance": "How important is all-day comfort when you choose shoes?",
    "price_range": "Based on the concept shown, what price range would feel reasonable for a pair?",
    "favorite_brand": "Is there a shoe or apparel brand you return to?",
    "additional_feedback": "Anything else you want us to know?",
}


VISUAL_DIRECTION_OPTIONS = (
    {
        "value": "night_grid",
        "label": "Night Grid",
        "description": "Tonal black foundation",
        "image_960": "images/heritage-court/night-grid-960.webp",
        "image_1600": "images/heritage-court/night-grid-1600.webp",
        "alt": "Pair of TreadJoy Heritage Court concept shoes with near-black overlays, charcoal laces, warm-stone panels, and off-white soles.",
    },
    {
        "value": "relief_contour",
        "label": "Relief Contour",
        "description": "White-on-white topography",
        "image_960": "images/heritage-court/relief-contour-960.webp",
        "image_1600": "images/heritage-court/relief-contour-1600.webp",
        "alt": "Pair of TreadJoy Heritage Court concept shoes in white-on-white contour-pattern overlays with warm-stone panels.",
    },
    {
        "value": "evergreen_route",
        "label": "Evergreen Route",
        "description": "Forest route texture",
        "image_960": "images/heritage-court/evergreen-route-960.webp",
        "image_1600": "images/heritage-court/evergreen-route-1600.webp",
        "alt": "Pair of TreadJoy Heritage Court concept shoes with forest-green route-textured overlays, cream laces, and gold logos.",
    },
    {
        "value": "relief_noir",
        "label": "Relief / Noir",
        "description": "Relief shell, Noir supports",
        "image_960": "images/heritage-court/relief-noir-960.webp",
        "image_1600": "images/heritage-court/relief-noir-1600.webp",
        "alt": "Pair of TreadJoy Heritage Court concept shoes combining white contour overlays with black tongues, laces, heels, and badges.",
    },
    {
        "value": "forest_noir",
        "label": "Forest / Noir",
        "description": "Evergreen shell, Noir supports",
        "image_960": "images/heritage-court/forest-noir-960.webp",
        "image_1600": "images/heritage-court/forest-noir-1600.webp",
        "alt": "Pair of TreadJoy Heritage Court concept shoes combining forest-green route-textured overlays with black tongues, laces, and heels.",
    },
    {
        "value": "relief_joyfront",
        "label": "Relief Joyfront",
        "description": "Relief shell, Joy Step front",
        "image_960": "images/heritage-court/relief-joyfront-960.webp",
        "image_1600": "images/heritage-court/relief-joyfront-1600.webp",
        "alt": "Pair of white TreadJoy Heritage Court concept shoes with sky-blue toe panels featuring the black, gold, and coral Joy Step mascot.",
    },
)


class SurveyStepForm(forms.Form):
    company_website = forms.CharField(
        required=False,
        label="Leave this field empty",
        widget=forms.HiddenInput(attrs={"tabindex": "-1", "autocomplete": "off", "aria-hidden": "true"}),
    )


class VisualDirectionPreferenceForm(SurveyStepForm):
    visual_direction_preference = forms.ChoiceField(
        label=SURVEY_PROMPTS["visual_direction_preference"],
        choices=SurveyResponse.VISUAL_DIRECTION_CHOICES,
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
        choices=SurveyResponse.CURRENT_PRICE_CHOICES,
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
    1: ("visual_direction_preference", VisualDirectionPreferenceForm),
    2: ("comfort_importance", ComfortImportanceForm),
    3: ("price_range", PriceRangeForm),
    4: ("favorite_brand", FavoriteBrandForm),
    5: ("additional_feedback", AdditionalFeedbackForm),
}
