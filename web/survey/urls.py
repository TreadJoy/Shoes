from django.urls import path
from . import views

app_name = "survey"

urlpatterns = [
    path("", views.survey_welcome, name="survey_welcome"),
    path("question/<int:question_number>/", views.survey_question, name="survey_question"),
    path("thank-you/", views.survey_thank_you, name="survey_thank_you"),
]
