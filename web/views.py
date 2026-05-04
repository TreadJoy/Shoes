from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.conf import settings
import stripe
# from web.models import


# Create your views here.
class HomePage(View):
    def get(self, request):
        return render(request, 'homepage.html')

class Contact(View):
    def get(self, request):
        return render(request, "contact.html")

#Original survey
#The first goal we want from this website
#Still needs set up for it to be functional
class Survey(View):
    def get(self, request):
        return render(request, "survey.html")

#User Signup, login, and logout.
#Collects just basic user data to ensure account.
#Currently very simple.
class SignUp(View):
    def get(self, request):
        return render(request, "sign_up.html")
    def post(self, request):
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("signup")

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        login(request, user)
        return redirect('home')
class SignIn(View):
    def get(self, request):
        return render(request, "sign_in.html")

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password")
            return redirect("signin")

class SignOut(View):
    def get(self, request):
        logout(request)
        return redirect('home')

#Payment Processing
#Currently using only stripe
class Cart(View):
    def get(self, request):
        return render(request, "cart.html")
class Checkout(View):
    def get(self, request):
        stripe.api_key = settings.STRIPE_SECRET_KEY

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            mode='payment',
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'TreadJoy Shoes',
                    },
                    'unit_amount': 2000,
                },
                "quantity": 1,
            }
            ],
            success_url='http://localhost:8000/success/',
            cancel_url='http://localhost:8000/cancel/',
        )
        return redirect(session.url)

class PaymentSuccess(View):
    def get(self, request):
        return render(request, "payment_success.html")

class PaymentCancel(View):
    def get(self, request):
        return render(request, "payment_cancel.html")