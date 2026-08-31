from django.conf import settings
from django.http import HttpResponseNotAllowed
from django.shortcuts import render

from web.products.models import PartType

from .youtube import build_homepage_video


def home(request):
    if settings.IS_COMMERCE_MODE and request.method != "GET":
        return HttpResponseNotAllowed(["GET"])

    if not settings.IS_COMMERCE_MODE and request.method != "GET":
        return HttpResponseNotAllowed(["GET"])

    context = {
        "modular_part_types": PartType.objects.filter(is_active=True)[:6],
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


def privacy(request):
    return render(
        request,
        "privacy.html",
        {
            "notice_version": settings.RESEARCH_PRIVACY_NOTICE_VERSION,
            "notice_is_draft": settings.RESEARCH_PRIVACY_NOTICE_VERSION.endswith("draft"),
            "notice_body": settings.RESEARCH_PRIVACY_NOTICE_BODY,
        },
    )
