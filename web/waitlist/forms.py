from django import forms


CONSENT_LABEL = (
    "I want launch and product-development updates from TreadJoy, "
    "limited to two messages per UTC calendar month."
)


class WaitlistSubscriptionForm(forms.Form):
    email = forms.EmailField(
        label="Email address",
        max_length=254,
        widget=forms.EmailInput(attrs={"autocomplete": "email", "inputmode": "email"}),
    )
    consent = forms.BooleanField(label=CONSENT_LABEL, required=True)
    company_website = forms.CharField(
        required=False,
        label="Leave this field empty",
        widget=forms.HiddenInput(attrs={"tabindex": "-1", "autocomplete": "off", "aria-hidden": "true"}),
    )

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()
