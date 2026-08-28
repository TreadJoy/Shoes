from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


def signup_view(request):
    return redirect("account_signup")


@login_required
def profile(request):
    return render(request, "account/profile.html")
