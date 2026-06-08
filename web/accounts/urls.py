from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path("signup/", views.signup_view, name="signup"),
    path("activate/<uidb64>/<token>/", views.activate, name="activate"),
    path("", views.profile, name="profile"),
]