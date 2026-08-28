from django import forms

class CheckoutForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        max_length=254,
    )
    state = forms.CharField(
        label="Shipping State",
        max_length=2,
        min_length=2,
        help_text="Used only to confirm contiguous-U.S. shipping eligibility.",
    )
