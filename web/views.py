from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views import View
# from web.models import


# Create your views here.
class HomePage(View):
    def get(self, request):
        return render(request, 'homepage.html')