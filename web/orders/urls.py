from django.contrib.auth.decorators import login_required
from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = "orders"

urlpatterns = [
    path("", views.order_list, name="order_list"),
    path("checkout/", views.checkout, name="checkout"),
    path(
        "success/attempt/<uuid:attempt_id>/",
        views.checkout_success,
        name="checkout_success",
    ),
    path("success/<int:order_id>/", views.order_success, name="order_success"),
    path(
        "history/",
        login_required(
            RedirectView.as_view(
                pattern_name="orders:order_list",
                permanent=False,
            )
        ),
    ),
    path("<int:order_id>/", views.order_detail, name="order_detail"),
    path("stripe/webhook/", views.stripe_webhook, name="stripe_webhook"),
]
