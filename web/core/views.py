from django.shortcuts import render


def home(request):
    return render(request, "home.html")


def about(request):
    return render(request, "about.html")


def how_it_works(request):
    return render(request, "how_it_works.html")


def contact(request):
    return render(request, "contact.html")
