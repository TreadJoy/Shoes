from django import forms

from .models import WaitlistSignup


class WaitlistSignupForm(forms.Form):
    first_name = forms.CharField(
        label="First name",
        max_length=WaitlistSignup._meta.get_field("first_name").max_length,
        required=False,
    )
    email = forms.EmailField(
        label="Email",
        max_length=WaitlistSignup._meta.get_field("email").max_length,
    )

    def clean_email(self):
        return self.cleaned_data["email"].lower()

