from django.contrib import messages
from django.shortcuts import render, redirect
from .models import WaitlistSignup


def join_waitlist(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        first_name = request.POST.get("first_name", "").strip()

        if not email:
            messages.error(request, "Please enter an email address.")
            return redirect("waitlist:join_waitlist")

        if "@" not in email or "." not in email:
            messages.error(request, "Please enter a valid email address.")
            return redirect("waitlist:join_waitlist")

        signup, created = WaitlistSignup.objects.get_or_create(
            email=email,
            defaults={"first_name": first_name},
        )

        if created:
            messages.success(request, "You joined the waitlist successfully!")
        else:
            messages.info(request, "This email is already on the waitlist.")

        return redirect("waitlist:join_waitlist")

    signup_count = WaitlistSignup.objects.count()

    return render(request, "waitlist/join_waitlist.html", {
        "signup_count": signup_count,
    })