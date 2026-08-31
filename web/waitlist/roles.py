from django.conf import settings
from django.contrib.auth.models import Group, Permission


def configure_research_roles(**kwargs):
    if settings.IS_COMMERCE_MODE:
        return
    analyst, _ = Group.objects.get_or_create(name="Research analyst")
    analyst.permissions.set(
        Permission.objects.filter(
            content_type__app_label="survey",
            codename__in=("view_surveyresponse", "export_surveyresponse"),
        )
    )
    manager, _ = Group.objects.get_or_create(name="Relationship manager")
    manager.permissions.set(
        Permission.objects.filter(
            content_type__app_label="waitlist",
            codename__in=(
                "view_waitlistsubscription",
                "view_consentevent",
                "view_emailsuppression",
                "view_researchoutboundemail",
                "view_resendwebhookevent",
                "view_marketingbroadcast",
                "add_marketingbroadcast",
                "approve_marketingbroadcast",
            ),
        )
    )
