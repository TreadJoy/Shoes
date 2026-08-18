from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect, render
from django.urls import reverse

from web.products.models import PartType

from .youtube import build_homepage_video


def home(request):
    if settings.IS_COMMERCE_MODE and request.method != "GET":
        return HttpResponseNotAllowed(["GET"])

    if not settings.IS_COMMERCE_MODE and request.method not in {"GET", "POST"}:
        return HttpResponseNotAllowed(["GET", "POST"])

    context = {
        "modular_part_types": PartType.objects.filter(is_active=True)[:6],
        "homepage_video": build_homepage_video(
            settings.HOMEPAGE_YOUTUBE_VIDEO_ID,
            settings.HOMEPAGE_YOUTUBE_TITLE,
        ),
    }

    if not settings.IS_COMMERCE_MODE:
        # Keep research conversion state out of commerce requests entirely.
        from web.waitlist.forms import WaitlistSignupForm
        from web.waitlist.services import create_waitlist_signup

        waitlist_form = WaitlistSignupForm(request.POST or None)

        if request.method == "POST" and waitlist_form.is_valid():
            _, created = create_waitlist_signup(
                email=waitlist_form.cleaned_data["email"],
                first_name=waitlist_form.cleaned_data["first_name"],
                source="homepage",
            )

            if created:
                messages.success(
                    request,
                    "You joined the waitlist successfully!",
                )
            else:
                messages.info(
                    request,
                    "This email is already on the waitlist.",
                )

            return redirect(f"{reverse('core:home')}#home-waitlist")

        context["waitlist_form"] = waitlist_form

    return render(request, "home.html", context)


def about(request):
    return render(request, "about.html")


def how_it_works(request):
    return render(request, "how_it_works.html")


def contact(request):
    return render(request, "contact.html")
