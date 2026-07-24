from django.urls import path

from . import views

app_name = 'orders'

urlpatterns = [
    path("", views.order_list, name='order_list'),
    path("checkout/", views.checkout, name='checkout'),
    path("success/<int:order_id>/", views.order_success, name="order_success"),
    path("history/", views.order_history, name='order_history'),
    path("<int:order_id>/", views.order_detail, name="order_detail"),
    path("stripe/webhook/", views.stripe_webhook, name="stripe_webhook"),
]