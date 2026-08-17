from django.http import Http404
from django.shortcuts import redirect, render

from .forms import SURVEY_STEPS
from .models import SurveyResponse


SURVEY_DRAFT_SESSION_KEY = "survey_draft"

def survey_welcome(request):
    return render(request, "survey/survey_welcome.html")


def survey_question(request, question_number):
    if question_number not in SURVEY_STEPS:
        raise Http404("Survey step not found.")

    draft = request.session.get(SURVEY_DRAFT_SESSION_KEY, {})
    for prior_number in range(1, question_number):
        prior_field_name, _ = SURVEY_STEPS[prior_number]
        if prior_field_name not in draft:
            return redirect("survey:survey_question", prior_number)

    field_name, form_class = SURVEY_STEPS[question_number]
    initial = {field_name: draft[field_name]} if field_name in draft else None
    form = form_class(request.POST or None, initial=initial)

    if request.method == "POST" and form.is_valid():
        draft[field_name] = form.cleaned_data[field_name]
        request.session[SURVEY_DRAFT_SESSION_KEY] = draft
        request.session.modified = True

        if question_number < len(SURVEY_STEPS):
            return redirect("survey:survey_question", question_number + 1)

        if not request.session.session_key:
            request.session.create()

        SurveyResponse.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_key=request.session.session_key,
            **draft,
        )
        del request.session[SURVEY_DRAFT_SESSION_KEY]
        request.session.modified = True
        return redirect("survey:survey_thank_you")

    return render(
        request,
        "survey/survey_question.html",
        {
            "form": form,
            "question_number": question_number,
            "total_questions": len(SURVEY_STEPS),
        },
    )


def survey_thank_you(request):
    return render(request, "survey/survey_thank_you.html")
