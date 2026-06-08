from django.shortcuts import render
from .models import SurveyResponse

def survey_welcome(request):
    return render(request, "survey/survey_welcome.html")


def survey_question(request, question_number):
    return render(
        request,
        "survey/survey_question.html",
        {"question_number": question_number}
    )


def survey_thank_you(request):
    return render(request, "survey/survey_thank_you.html")