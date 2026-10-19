from django.conf import settings
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render

from web.products.models import PartType
from web.products.services import HERITAGE_COURT_COMPONENT_CODES

from .youtube import build_homepage_video


def home(request):
    if settings.IS_COMMERCE_MODE and request.method != "GET":
        return HttpResponseNotAllowed(["GET"])

    if not settings.IS_COMMERCE_MODE and request.method != "GET":
        return HttpResponseNotAllowed(["GET"])

    types_by_code = {
        part_type.code: part_type
        for part_type in PartType.objects.filter(
            code__in=HERITAGE_COURT_COMPONENT_CODES,
        )
    }
    context = {
        "modular_part_types": [
            types_by_code[code]
            for code in HERITAGE_COURT_COMPONENT_CODES
            if code in types_by_code
        ],
        "homepage_video": build_homepage_video(
            settings.HOMEPAGE_YOUTUBE_VIDEO_ID,
            settings.HOMEPAGE_YOUTUBE_TITLE,
        ),
    }

    if not settings.IS_COMMERCE_MODE:
        # Keep research conversion state out of commerce requests entirely.
        from web.waitlist.forms import WaitlistSubscriptionForm

        context["waitlist_form"] = WaitlistSubscriptionForm()

    return render(request, "home.html", context)


def about(request):
    return render(request, "about.html")


def how_it_works(request):
    return render(request, "how_it_works.html")


def contact(request):
    return render(request, "contact.html")


def terms(request):
    return render(request, "terms.html")


def accessibility(request):
    return render(request, "accessibility.html")


def robots(request):
    if settings.IS_PUBLIC_ENVIRONMENT and not settings.TREADJOY_PRIVATE_POC:
        body = "\n".join(
            (
                "User-agent: *",
                "Disallow: /admin/",
                "Disallow: /accounts/",
                "Disallow: /cart/",
                "Disallow: /health/",
                "Disallow: /orders/",
                "Disallow: /survey/",
                "Disallow: /waitlist/",
                "Disallow: /media/",
                "Disallow: /static/",
                "",
            )
        )
    else:
        body = "User-agent: *\nDisallow: /\n"
    response = HttpResponse(body, content_type="text/plain; charset=utf-8")
    response["Cache-Control"] = "no-store"
    return response


def privacy(request):
    return render(
        request,
        "privacy.html",
        {
            "notice_version": settings.RESEARCH_PRIVACY_NOTICE_VERSION,
            "notice_is_draft": settings.RESEARCH_PRIVACY_NOTICE_VERSION.endswith(
                "draft"
            ),
            "notice_body": settings.RESEARCH_PRIVACY_NOTICE_BODY,
            "private_poc": settings.TREADJOY_PRIVATE_POC,
        },
    )
