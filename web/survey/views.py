from datetime import timedelta

from django.http import Http404
from django.shortcuts import redirect, render
from django.utils import timezone

from web.core.rate_limits import completed_within, consume_session_limit, record_abuse_metric, throttled_response
from web.core.forms import focus_first_error

from .forms import SURVEY_PROMPTS, SURVEY_STEPS, VISUAL_DIRECTION_OPTIONS
from .models import SurveyResponse


SURVEY_DRAFT_SESSION_KEY = "survey_draft"
SURVEY_COMPLETED_SESSION_KEY = "research_survey_completed_at"


def _load_current_draft(request):
    payload = request.session.get(SURVEY_DRAFT_SESSION_KEY)
    if payload is None:
        return {}
    if (
        not isinstance(payload, dict)
        or payload.get("response_version") != SurveyResponse.CURRENT_VERSION
        or not isinstance(payload.get("answers"), dict)
    ):
        request.session.pop(SURVEY_DRAFT_SESSION_KEY, None)
        request.session.modified = True
        return {}
    return payload["answers"]


def _store_current_draft(request, answers):
    request.session[SURVEY_DRAFT_SESSION_KEY] = {
        "response_version": SurveyResponse.CURRENT_VERSION,
        "answers": answers,
    }
    request.session.modified = True


def survey_welcome(request):
    return render(request, "survey/survey_welcome.html")


def survey_question(request, question_number):
    if question_number not in SURVEY_STEPS:
        raise Http404("Survey step not found.")

    if request.method == "POST":
        retry_after = completed_within(
            request, key=SURVEY_COMPLETED_SESSION_KEY, window=timedelta(hours=24)
        )
        if retry_after:
            record_abuse_metric(action="survey", kind="completion_throttle")
            return throttled_response(request, retry_after)
        retry_after = consume_session_limit(
            request,
            key="research_survey_step_posts",
            limit=60,
            window=timedelta(hours=1),
        )
        if retry_after:
            record_abuse_metric(action="survey", kind="session_throttle")
            return throttled_response(request, retry_after)

    draft = _load_current_draft(request)
    for prior_number in range(1, question_number):
        prior_field_name, _ = SURVEY_STEPS[prior_number]
        if prior_field_name not in draft:
            return redirect("survey:survey_question", prior_number)

    field_name, form_class = SURVEY_STEPS[question_number]
    initial = {field_name: draft[field_name]} if field_name in draft else None
    form = form_class(request.POST or None, initial=initial)

    if request.method == "POST" and request.POST.get("navigation") == "back":
        if form.is_valid():
            if form.cleaned_data["company_website"]:
                record_abuse_metric(action="survey", kind="honeypot")
                request.session.pop(SURVEY_DRAFT_SESSION_KEY, None)
                return redirect("survey:survey_thank_you")
            draft[field_name] = form.cleaned_data[field_name]
            _store_current_draft(request, draft)

        if question_number == 1:
            return redirect("survey:survey_welcome")
        return redirect("survey:survey_question", question_number - 1)

    if request.method == "POST" and form.is_valid():
        if form.cleaned_data["company_website"]:
            record_abuse_metric(action="survey", kind="honeypot")
            request.session.pop(SURVEY_DRAFT_SESSION_KEY, None)
            return redirect("survey:survey_thank_you")
        draft[field_name] = form.cleaned_data[field_name]
        _store_current_draft(request, draft)

        if question_number < len(SURVEY_STEPS):
            return redirect("survey:survey_question", question_number + 1)

        completed_answers = {
            step_field_name: draft[step_field_name]
            for step_field_name, _form_class in SURVEY_STEPS.values()
        }
        SurveyResponse.objects.create(
            response_version=SurveyResponse.CURRENT_VERSION,
            general_style_preference="",
            **completed_answers,
        )
        request.session.pop(SURVEY_DRAFT_SESSION_KEY, None)
        request.session[SURVEY_COMPLETED_SESSION_KEY] = timezone.now().timestamp()
        request.session.modified = True
        return redirect("survey:survey_thank_you")

    if request.method == "POST":
        focus_first_error(form)
        for error_field_name in form.errors:
            bound_error_field = form[error_field_name]
            error_field = bound_error_field.field
            if error_field.widget.is_hidden:
                continue
            described_by = error_field.widget.attrs.get("aria-describedby", "").split()
            error_id = f"{bound_error_field.auto_id}_error"
            if error_id not in described_by:
                described_by.append(error_id)
            error_field.widget.attrs["aria-describedby"] = " ".join(described_by)

    return render(
        request,
        "survey/survey_question.html",
        {
            "form": form,
            "question_number": question_number,
            "total_questions": len(SURVEY_STEPS),
            "progress_percent": question_number * 100 // len(SURVEY_STEPS),
            "question_prompt": SURVEY_PROMPTS[field_name],
            "is_visual_direction_step": field_name == "visual_direction_preference",
            "selected_visual_direction": (
                form[field_name].value()
                if field_name == "visual_direction_preference"
                else None
            ),
            "visual_direction_options": VISUAL_DIRECTION_OPTIONS,
        },
    )


def survey_thank_you(request):
    return render(request, "survey/survey_thank_you.html")
