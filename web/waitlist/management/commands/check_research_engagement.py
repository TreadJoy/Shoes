import hashlib
import hmac

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError

from web.core.research_boundary import database_boundary_violations, runtime_boundary_violations, url_boundary_violations


class Command(BaseCommand):
    help = "Read-only validation of the research identity, consent, email, and retention profile."

    def handle(self, *args, **options):
        if settings.IS_COMMERCE_MODE:
            raise CommandError("check_research_engagement only passes in research mode.")
        findings = runtime_boundary_violations() + url_boundary_violations() + database_boundary_violations()
        analyst = Group.objects.filter(name="Research analyst").first()
        manager = Group.objects.filter(name="Relationship manager").first()
        analyst_permissions = (
            set(analyst.permissions.values_list("codename", flat=True))
            if analyst
            else set()
        )
        manager_permissions = (
            set(manager.permissions.values_list("codename", flat=True))
            if manager
            else set()
        )
        required = {
            "privacy_notice": bool(settings.RESEARCH_PRIVACY_NOTICE_VERSION)
            and (
                settings.TREADJOY_PRIVATE_POC
                or "draft" not in settings.RESEARCH_PRIVACY_NOTICE_VERSION.casefold()
            ),
            "privacy_notice_body": bool(settings.RESEARCH_PRIVACY_NOTICE_BODY),
            "privacy_notice_digest": hmac.compare_digest(
                hashlib.sha256(settings.RESEARCH_PRIVACY_NOTICE_BODY.encode()).hexdigest(),
                settings.RESEARCH_PRIVACY_NOTICE_SHA256,
            ),
            "identity_hmac": bool(settings.RESEARCH_IDENTITY_HMAC_KEY),
            "send_key": settings.RESEARCH_EMAIL_PROVIDER == "fake" or bool(settings.RESEARCH_RESEND_SEND_API_KEY),
            "webhook_secret": settings.RESEARCH_EMAIL_PROVIDER == "fake" or bool(settings.RESEARCH_RESEND_WEBHOOK_SECRET),
            "segment": (
                settings.RESEARCH_EMAIL_PROVIDER == "fake"
                or settings.TREADJOY_PRIVATE_POC
                or bool(settings.RESEARCH_RESEND_SEGMENT_ID)
            ),
            "management_key": (
                settings.RESEARCH_EMAIL_PROVIDER == "fake"
                or settings.TREADJOY_PRIVATE_POC
                or bool(settings.RESEARCH_RESEND_MANAGEMENT_API_KEY)
            ),
            "retention_policy": bool(settings.RESEARCH_RETENTION_POLICY_VERSION)
            and (
                settings.TREADJOY_PRIVATE_POC
                or "draft" not in settings.RESEARCH_RETENTION_POLICY_VERSION.casefold()
            ),
            "staff_roles": analyst_permissions
            == {"view_surveyresponse", "export_surveyresponse"}
            and manager_permissions
            == {
                "view_waitlistsubscription",
                "view_consentevent",
                "view_emailsuppression",
                "view_researchoutboundemail",
                "view_resendwebhookevent",
                "view_marketingbroadcast",
                "add_marketingbroadcast",
                "approve_marketingbroadcast",
            },
        }
        findings.extend(f"research engagement requirement not ready: {name}" for name, ready in required.items() if not ready)
        if findings:
            for finding in findings:
                self.stderr.write(f"ERROR: {finding}")
            raise CommandError(f"Research engagement boundary failed with {len(findings)} aggregate finding(s).")
        self.stdout.write(self.style.SUCCESS("Research engagement boundary passed."))
