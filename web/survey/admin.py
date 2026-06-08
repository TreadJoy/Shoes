from django.contrib import admin
from .models import SurveyResponse


@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "style_preference",
        "comfort_importance",
        "price_range",
        "favorite_brand",
        "created_at",
    )
    list_filter = (
        "style_preference",
        "comfort_importance",
        "price_range",
        "created_at",
    )
    search_fields = (
        "favorite_brand",
        "additional_feedback",
    )
    readonly_fields = (
        "created_at",
    )