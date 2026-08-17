from django import forms

from .models import ShippingAddress


def address_max_length(field_name):
    return ShippingAddress._meta.get_field(field_name).max_length


class CheckoutForm(forms.Form):
    full_name = forms.CharField(
        label="Full Name",
        max_length=address_max_length("full_name"),
    )
    email = forms.EmailField(
        label="Email",
        max_length=address_max_length("email"),
    )
    address_line_1 = forms.CharField(
        label="Address",
        max_length=address_max_length("address_line_1"),
    )
    address_line_2 = forms.CharField(
        label="Apartment, suite, etc.",
        max_length=address_max_length("address_line_2"),
        required=False,
    )
    city = forms.CharField(
        label="City",
        max_length=address_max_length("city"),
    )
    state = forms.CharField(
        label="State",
        max_length=address_max_length("state"),
    )
    postal_code = forms.CharField(
        label="ZIP Code",
        max_length=address_max_length("postal_code"),
    )

