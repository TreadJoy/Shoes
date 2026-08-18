from django.contrib import messages
from django.shortcuts import render, redirect

from .forms import WaitlistSignupForm
from .models import WaitlistSignup
from .services import create_waitlist_signup


def join_waitlist(request):
    form = WaitlistSignupForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        _, created = create_waitlist_signup(
            email=form.cleaned_data["email"],
            first_name=form.cleaned_data["first_name"],
            source="waitlist_page",
        )

        if created:
            messages.success(request, "You joined the waitlist successfully!")
        else:
            messages.info(request, "This email is already on the waitlist.")

        return redirect("waitlist:join_waitlist")

    signup_count = WaitlistSignup.objects.count()

    return render(request, "waitlist/join_waitlist.html", {
        "form": form,
        "signup_count": signup_count,
    })
