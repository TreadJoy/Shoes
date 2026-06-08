from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.conf import settings
import stripe
from django.views.generic import TemplateView
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from web.accounts.tokens import email_verification_token

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
        step = int(request.GET.get("step", 0))

        if step == 0:
            return render(request, "survey/survey_welcome.html")

        question_index = step - 1

        if question_index >= len(QUESTIONS):
            return redirect("survey")

        question = QUESTIONS[question_index]

        saved_answers = request.session.get("survey_answers", {})

        return render(request, "survey/survey_question.html", {
            "question": question,
            "step": step,
            "total_steps": len(QUESTIONS),
            "saved_value": saved_answers.get(question["field"]),
            "is_last": step == len(QUESTIONS),
        })

    def post(self, request):
        step = int(request.POST.get("step", 0))
        action = request.POST.get("action")

        if action == "start":
            request.session["survey_answers"] = {}
            return redirect("/survey/?step=1")

        if action == "back":
            previous_step = max(step - 1, 0)
            return redirect(f"/survey/?step={previous_step}")

        question_index = step - 1
        question = QUESTIONS[question_index]

        answer = request.POST.get(question["field"])

        answers = request.session.get("survey_answers", {})
        answers[question["field"]] = answer
        request.session["survey_answers"] = answers
        request.session.modified = True

        if action == "submit":
            SurveyResponse.objects.create(
                user=request.user if request.user.is_authenticated else None,
                q1=answers.get("q1"),
                q2=answers.get("q2"),
                q3=answers.get("q3"),
                q4=answers.get("q4"),
                q5=answers.get("q5"),
                q6=answers.get("q6"),
            )

            request.session.pop("survey_answers", None)

            return redirect("survey_thank_you")

        return redirect(f"/survey/?step={step + 1}")

QUESTIONS = [
    {
        "field": "q1",
        "type": "likert",
        "text": "I want unique shoes that make me stand out."
    },
    {
        "field": "q2",
        "type": "likert",
        "text": "I want to create and customize my own shoes as I see fit."
    },
    {
        "field": "q3",
        "type": "likert",
        "text": "Price is an important factor when I buy a shoe."
    },
    {
        "field": "q4",
        "type": "likert",
        "text": "I would consider buying this product for myself."
    },
    {
        "field": "q5",
        "type": "likert",
        "text": "I would consider buying this product for someone in my family."
    },
    {
        "field": "q6",
        "type": "text",
        "text": "What is the most important factor in choosing a shoe?"
    },
]

class SurveyThankYou(TemplateView):
    template_name = "survey/survey_thank_you.html"

#User Signup, login, and logout.
#Collects just basic user data to ensure accounts.
#Currently very simple.
def signup(request):
    if request.method == "POST":
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

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect("signup")

        try:
            validate_password(password)
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
            return redirect("signup")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )

        user.is_active = False
        user.save()

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = email_verification_token.make_token(user)

        verification_url = request.build_absolute_uri(
            reverse("verify_email", kwargs={
                "uidb64": uid,
                "token": token,
            })
        )

        send_mail(
            subject="Verify your email address",
            message=f"Please click the link to verify your email address: {verification_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        return redirect("verification_sent")

    return render(request, "sign_up.html")

def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and email_verification_token.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect("signin")

    return render(request, "verification_failed.html")

class VerificationSentView(TemplateView):
    template_name = "verification_sent.html"

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

#Cart and related fields
class AddToCart(View):
    def get(self, request):
        products = {
            "1": {"id": 1, "name": "TreadJoy Shoes", "price": 2000, "quantity": 50},
            "2": {"id": 2, "name": "TreadJoy Socks", "price": 100, "quantity": 100},
            "3": {"id": 3, "name": "TreadJoy Hats", "price": 50, "quantity": 200},
        }

        product_id = request.GET.get("id")

        if product_id not in products:
            return redirect("products")

        cart = request.session.get("cart", [])
        if not isinstance(cart, list):
            cart = []

        selected_product = products[product_id]

        item = {
            "id": selected_product["id"],
            "name": selected_product["name"],
            "price": selected_product["price"],
            "quantity": 1,
        }

        cart.append(item)

        request.session["cart"] = cart
        request.session.modified = True

        return redirect("products")
class Cart(View):
    def get(self, request):
        cart = request.session.get("cart", [])
        total = 0

        for item in cart:
            total += item["price"] * item["quantity"]

        return render(request, "cart.html", {
                "cart": cart,
                "total": total
        })
class ClearCart(View):
    def get(self, request):
        request.session["cart"] = {}
        return redirect("cart")
#Payment Processing
#Currently using only stripe
class Checkout(View):
    def get(self, request):
        stripe.api_key = settings.STRIPE_SECRET_KEY

        cart = request.session.get("cart", [])

        line_items = []

        for products in cart:
            line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': products["name"],
                    },
                    "unit_amount": products["price"],
                },
                "quantity": products["quantity"],
            })
        if not line_items:
            return redirect("cart")

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            mode='payment',
            line_items=line_items,
            success_url='http://localhost:8000/payment-success/',
            cancel_url='http://localhost:8000/payment-cancel/',
        )
        return redirect(session.url)

class PaymentSuccess(View):
    def get(self, request):
        return render(request, "payment_success.html")

class PaymentCancel(View):
    def get(self, request):
        return render(request, "payment_cancel.html")


#Products
class Products(View):
    def get(self, request):
        products = [
            {"id": 1, "name": "TreadJoy Shoes", "price": 2000},
            {"id": 2, "name": "TreadJoy Socks", "price": 100},
            {"id": 3, "name": "TreadJoy Hats", "price": 50},
        ]
        return render(request, "products.html", {"products": products})

