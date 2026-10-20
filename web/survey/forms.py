from django import forms

from .models import SurveyResponse


SURVEY_PROMPTS = {
    "visual_direction_preference": "Which sneaker design do you prefer?",
    "comfort_importance": "How important is comfort when you choose shoes?",
    "price_range": "What price range would be reasonable for this sneaker?",
    "recruitment_source": "How did you hear about this survey?",
    "overall_appeal": "How appealing is this to you?",
    "modularity_value": "How interesting is this idea to you?",
    "wearing_occasion": "When would you wear a shoe like this?",
    "purchase_likelihood": "How likely would you be to buy this?",
    "annual_purchases": "How many pairs of shoes do you usually buy in a year?",
    "age_band": "Which age range are you in?",
    "gender": "Which gender best describes you?",
    "favorite_brand": "What's your favorite shoe or clothing brand?",
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
        choices=SurveyResponse.V3_PRICE_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "survey-choice-input"}),
    )


class RecruitmentSourceForm(SurveyStepForm):
    recruitment_source = forms.ChoiceField(
        label=SURVEY_PROMPTS["recruitment_source"],
        choices=SurveyResponse.RECRUITMENT_SOURCE_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "survey-choice-input"}),
    )


class OverallAppealForm(SurveyStepForm):
    overall_appeal = forms.ChoiceField(
        label=SURVEY_PROMPTS["overall_appeal"],
        choices=SurveyResponse.APPEAL_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "survey-choice-input"}),
    )


class ModularityValueForm(SurveyStepForm):
    modularity_value = forms.ChoiceField(
        label=SURVEY_PROMPTS["modularity_value"],
        choices=SurveyResponse.MODULARITY_VALUE_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "survey-choice-input"}),
    )


class WearingOccasionForm(SurveyStepForm):
    wearing_occasion = forms.ChoiceField(
        label=SURVEY_PROMPTS["wearing_occasion"],
        choices=SurveyResponse.WEARING_OCCASION_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "survey-choice-input"}),
    )


class PurchaseLikelihoodForm(SurveyStepForm):
    purchase_likelihood = forms.ChoiceField(
        label=SURVEY_PROMPTS["purchase_likelihood"],
        choices=SurveyResponse.PURCHASE_LIKELIHOOD_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "survey-choice-input"}),
    )


class AnnualPurchasesForm(SurveyStepForm):
    annual_purchases = forms.ChoiceField(
        label=SURVEY_PROMPTS["annual_purchases"],
        choices=SurveyResponse.SHOE_PURCHASE_FREQUENCY_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "survey-choice-input"}),
    )


class AgeBandForm(SurveyStepForm):
    age_band = forms.ChoiceField(
        label=SURVEY_PROMPTS["age_band"],
        choices=SurveyResponse.AGE_BAND_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "survey-choice-input"}),
    )


class GenderForm(SurveyStepForm):
    gender = forms.ChoiceField(
        label=SURVEY_PROMPTS["gender"],
        choices=SurveyResponse.GENDER_CHOICES,
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
    4: ("recruitment_source", RecruitmentSourceForm),
    5: ("overall_appeal", OverallAppealForm),
    6: ("modularity_value", ModularityValueForm),
    7: ("wearing_occasion", WearingOccasionForm),
    8: ("purchase_likelihood", PurchaseLikelihoodForm),
    9: ("annual_purchases", AnnualPurchasesForm),
    10: ("age_band", AgeBandForm),
    11: ("gender", GenderForm),
    12: ("favorite_brand", FavoriteBrandForm),
    13: ("additional_feedback", AdditionalFeedbackForm),
}
