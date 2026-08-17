from django.contrib.auth import login
from django.contrib.auth.models import User
from django.conf import settings
from django.shortcuts import render, redirect
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.decorators import login_required
from .tokens import account_activation_token


def signup_view(request):
    return redirect("account_signup")


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(
            request,
            user,
            backend=settings.AUTHENTICATION_BACKENDS[0],
        )
        return redirect("core:home")

    return render(request, "account/activate.html", {
        "activation_failed": True,
    })

@login_required
def profile(request):
    return render(request, "account/profile.html")
