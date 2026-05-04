"""
URL configuration for Shoes project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
#from web.models import
from web.views import HomePage, Contact, Survey, SignIn, SignUp, SignOut, Cart, Checkout, PaymentSuccess, PaymentCancel

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', HomePage.as_view(), name='home'),
    path("contact/", Contact.as_view(), name="contact"),
    path("survey/", Survey.as_view(), name="survey"),
    path("signin/", SignIn.as_view(), name="signin"),
    path("signup/", SignUp.as_view(), name="signup"),
    path("signout/", SignOut.as_view(), name="signout"),
    path("cart/", Cart.as_view(), name="cart"),
    path("checkout/", Checkout.as_view(), name="checkout"),
    path("payment-success/", PaymentSuccess.as_view(), name="payment_success"),
    path("payment-cancel/", PaymentCancel.as_view(), name="payment_cancel"),
]
