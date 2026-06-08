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
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", include("web.core.urls")),
    path("products/", include("web.products.urls")),
    path("cart/", include("web.cart.urls")),
    path("orders/", include("web.orders.urls")),
    path("survey/", include("web.survey.urls")),
    path("waitlist/", include("web.waitlist.urls")),

    # Your custom accounts/profile pages
    path("accounts/profile/", include("web.accounts.urls")),

    # Django allauth login/signup/logout pages
    path("accounts/", include("allauth.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)