import csv
import hashlib
import io

from django.contrib import admin
from django.http import HttpResponse

from .models import SurveyExportEvent, SurveyResponse


def _safe_csv_cell(value):
    text = "" if value is None else str(value)
    return f"'{text}" if text.startswith(("=", "+", "-", "@")) else text


@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "response_version",
        "general_style_preference",
        "visual_direction_preference",
        "comfort_importance",
        "price_range",
        "recruitment_source",
        "overall_appeal",
        "modularity_value",
        "wearing_occasion",
        "purchase_likelihood",
        "annual_purchases",
        "age_band",
        "gender",
    )
    list_filter = (
        "response_version",
        "general_style_preference",
        "visual_direction_preference",
        "comfort_importance",
        "price_range",
        "created_at",
    )
    fields = (
        "response_version",
        "general_style_preference",
        "visual_direction_preference",
        "comfort_importance",
        "price_range",
        "recruitment_source",
        "overall_appeal",
        "modularity_value",
        "wearing_occasion",
        "purchase_likelihood",
        "annual_purchases",
        "age_band",
        "gender",
        "favorite_brand",
        "additional_feedback",
        "created_at",
    )
    readonly_fields = fields
    actions = ("export_anonymous_csv",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_export_permission(self, request):
        return request.user.has_perm("survey.export_surveyresponse")

    @admin.action(description="Export selected anonymous responses as CSV", permissions=("export",))
    def export_anonymous_csv(self, request, queryset):
        output = io.StringIO(newline="")
        writer = csv.writer(output)
        writer.writerow(
            (
                "response_version",
                "general_style_preference",
                "visual_direction_preference",
                "comfort_importance",
                "price_range",
                "recruitment_source",
                "overall_appeal",
                "modularity_value",
                "wearing_occasion",
                "purchase_likelihood",
                "annual_purchases",
                "age_band",
                "gender",
                "favorite_brand",
                "additional_feedback",
                "created_at_utc",
            )
        )
        row_count = 0
        for response in queryset.order_by("created_at"):
            writer.writerow(
                tuple(
                    _safe_csv_cell(value)
                    for value in (
                        response.response_version,
                        response.general_style_preference,
                        response.visual_direction_preference,
                        response.comfort_importance,
                        response.price_range,
                        response.recruitment_source,
                        response.overall_appeal,
                        response.modularity_value,
                        response.wearing_occasion,
                        response.purchase_likelihood,
                        response.annual_purchases,
                        response.age_band,
                        response.gender,
                        response.favorite_brand,
                        response.additional_feedback,
                        response.created_at.isoformat(),
                    )
                )
            )
            row_count += 1
        payload = output.getvalue().encode("utf-8")
        SurveyExportEvent.objects.create(
            actor=request.user,
            row_count=row_count,
            file_sha256=hashlib.sha256(payload).hexdigest(),
        )
        result = HttpResponse(payload, content_type="text/csv; charset=utf-8")
        result["Content-Disposition"] = 'attachment; filename="treadjoy-anonymous-survey.csv"'
        result["Cache-Control"] = "no-store"
        return result


@admin.register(SurveyExportEvent)
class SurveyExportEventAdmin(admin.ModelAdmin):
    list_display = ("created_at", "actor", "purpose", "row_count")
    readonly_fields = ("actor", "purpose", "row_count", "file_sha256", "created_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
