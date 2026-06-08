from django.contrib import admin
from .models import WaitlistSignup


@admin.register(WaitlistSignup)
class WaitlistSignupAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "first_name",
        "source",
        "created_at",
    )
    search_fields = (
        "email",
        "first_name",
        "source",
    )
    list_filter = (
        "source",
        "created_at",
    )
    readonly_fields = (
        "created_at",
    )