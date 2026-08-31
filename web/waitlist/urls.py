from django.urls import path

from . import views

app_name = "waitlist"

urlpatterns = [
    path("join/", views.join_waitlist, name="join_waitlist"),
    path("join/homepage/", views.join_homepage, name="join_homepage"),
    path("confirm/<str:token>/", views.confirm, name="confirm"),
    path("unsubscribe/<str:token>/", views.unsubscribe, name="unsubscribe"),
    path("provider/resend/webhook/", views.resend_webhook, name="resend_webhook"),
]
