"""
URL configuration for the TreadJoy project.

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
admin.autodiscover()
if settings.IS_COMMERCE_MODE:
    from allauth.account.decorators import secure_admin_login

    admin.site.login = secure_admin_login(admin.site.login)

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", include("web.core.urls")),
    path("products/", include("web.products.urls")),
    path("survey/", include("web.survey.urls")),
    path("waitlist/", include("web.waitlist.urls")),

]

if settings.IS_COMMERCE_MODE:
    urlpatterns += [
        path("accounts/profile/", include("web.accounts.urls")),
        path("accounts/", include("allauth.urls")),
        path("cart/", include("web.cart.urls")),
        path("orders/", include("web.orders.urls")),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
